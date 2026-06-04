"""合成（配合）のアプリケーションサービス。

ルートが直接 ``player.synthesize_*`` を叩き、結果オブジェクトの型を見て
レスポンスを組み立てる…という処理が複数ルートに重複していた。
ここに集約し、ルートには「サービスを呼ぶ → 成功ならセーブ → DTO を返す」だけを残す。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..items.equipment import Equipment, EquipmentInstance
from ..monsters.monster_class import Monster
from ..monsters.synthesis_rules import SPECIAL_MONSTER_POOL

# ペイロード検証で返るメッセージ。これらは HTTP 400（不正リクエスト）に対応づける。
VALIDATION_ERRORS = frozenset({
    'invalid base index', 'invalid base id',
    'invalid material index', 'invalid material id', 'invalid types',
})


@dataclass
class SynthesisOutcome:
    """合成結果を表示用に正規化した DTO。ドメインの型をルートに漏らさない。"""

    success: bool
    message: str = ''
    result_type: str | None = None      # 'equipment' | 'monster' | 'item'
    name: str = ''
    rare: bool = False
    jackpot: bool = False
    plus_value: int = 0
    personality: str = ''
    talent: str = ''
    talent_hidden: bool = False

    @property
    def is_validation_error(self) -> bool:
        """入力不正（=400 を返すべき失敗）かどうか。"""
        return not self.success and self.message in VALIDATION_ERRORS

    def to_dict(self) -> dict:
        """JSON レスポンス用の辞書に変換する。"""
        if not self.success:
            return {'success': False, 'error': self.message}
        data = {'success': True, 'result_type': self.result_type, 'name': self.name}
        if self.result_type == 'monster':
            data.update(
                message=self.message,
                rare=self.rare,
                jackpot=self.jackpot,
                plus_value=self.plus_value,
                personality=self.personality,
                talent=self.talent,
                talent_hidden=self.talent_hidden,
            )
        return data


def _parse_index(value):
    """合成対象のインデックス（int）を取り出す。失敗時は (None, 'invalid')。"""
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, 'invalid'


def _describe(result) -> SynthesisOutcome:
    """ドメインの合成結果を表示用 DTO（成功）に翻訳する。"""
    if isinstance(result, (Equipment, EquipmentInstance)):
        return SynthesisOutcome(True, result_type='equipment', name=result.name)
    if isinstance(result, Monster):
        talent = result.talent
        return SynthesisOutcome(
            True,
            result_type='monster',
            name=result.name,
            rare=bool(getattr(result, 'is_rare', False)),
            jackpot=result.monster_id in SPECIAL_MONSTER_POOL,
            plus_value=getattr(result, 'plus_value', 0),
            personality=result.personality.name,
            talent=talent.name,
            talent_hidden=talent.hidden,
        )
    return SynthesisOutcome(True, result_type='item', name=getattr(result, 'name', ''))


def perform_synthesis(player, data: dict) -> SynthesisOutcome:
    """合成ペイロードを検証し、ドメイン処理を実行して表示用の結果を返す。

    base/material は monster（パーティのインデックス）か item（アイテムID）。
    永続化はここでは行わず、呼び出し側に委ねる（サービスは保存方式に無関心）。
    """
    base_type = data.get('base_type')
    base_id = data.get('base_id')
    material_type = data.get('material_type')
    material_id = data.get('material_id')

    base_idx = material_idx = None
    if base_type == 'monster':
        base_idx, err = _parse_index(base_id)
        if err:
            return SynthesisOutcome(False, 'invalid base index')
    elif not isinstance(base_id, str):
        return SynthesisOutcome(False, 'invalid base id')

    if material_type == 'monster':
        material_idx, err = _parse_index(material_id)
        if err:
            return SynthesisOutcome(False, 'invalid material index')
    elif not isinstance(material_id, str):
        return SynthesisOutcome(False, 'invalid material id')

    if base_type == 'monster' and material_type == 'monster':
        inherit = data.get('inherit_skills')
        if inherit is not None and not isinstance(inherit, list):
            inherit = None
        success, msg, result = player.synthesize_monster(
            base_idx, material_idx, inherit_skill_ids=inherit
        )
    elif base_type == 'monster' and material_type == 'item':
        success, msg, result = player.synthesize_monster_with_item(base_idx, material_id)
    elif base_type == 'item' and material_type == 'monster':
        success, msg, result = player.synthesize_monster_with_item(material_idx, base_id)
    elif base_type == 'item' and material_type == 'item':
        success, msg, result = player.synthesize_items(base_id, material_id)
    else:
        return SynthesisOutcome(False, 'invalid types')

    if not success:
        return SynthesisOutcome(False, msg)
    outcome = _describe(result)
    outcome.message = msg
    return outcome


def preview_synthesis(player, data: dict):
    """モンスター同士の配合結果を確定せず予測する。

    戻り値は (preview_dict, error)。error が None なら成功、文字列なら入力不正。
    """
    base_idx, err1 = _parse_index(data.get('base_id'))
    material_idx, err2 = _parse_index(data.get('material_id'))
    if err1 or err2:
        return None, 'invalid index'
    return player.preview_synthesis(base_idx, material_idx), None
