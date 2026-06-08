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
from ..monsters.personality import (
    DESTINY_KNOT_ITEM,
    DESTINY_KNOT_INHERIT_COUNT,
    EVERSTONE_ITEM,
    POWER_ITEMS,
)

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
    trait: str = ''

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
                trait=self.trait,
            )
        return data


def _parse_index(value):
    """合成対象のインデックス（int）を取り出す。失敗時は (None, 'invalid')。"""
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, 'invalid'


def _as_parent(value):
    """親指定（1=base / 2=material）に正規化する。不正なら None。"""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    return v if v in (1, 2) else None


def _parse_breeding(player, data: dict) -> dict:
    """配合補助アイテムの指定を、所持チェックしたうえでドメイン辞書に変換する。

    入力（``data['breeding']``）例::

        {"destiny_knot": true,
         "everstone_parent": 1,
         "power": {"power_bracer": 1, "power_anklet": 2}}

    アイテムは消費されない（ポケモンの持ち物と同じく、所持していれば使える）。
    """
    req = data.get('breeding') or {}
    if not isinstance(req, dict):
        return {}
    owned = {getattr(it, 'item_id', None) for it in getattr(player, 'items', [])}

    breeding: dict = {}
    if req.get('destiny_knot') and DESTINY_KNOT_ITEM in owned:
        breeding['inherit_count'] = DESTINY_KNOT_INHERIT_COUNT

    power_stats: dict[str, int] = {}
    for item_id, parent in (req.get('power') or {}).items():
        parent = _as_parent(parent)
        if item_id in POWER_ITEMS and item_id in owned and parent is not None:
            power_stats[POWER_ITEMS[item_id]] = parent
    if power_stats:
        breeding['power_stats'] = power_stats

    everstone_parent = _as_parent(req.get('everstone_parent'))
    if everstone_parent is not None and EVERSTONE_ITEM in owned:
        breeding['everstone_parent'] = everstone_parent

    return breeding


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
            trait=result.trait.name if result.trait else '',
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
        breeding = _parse_breeding(player, data)
        result_choice = data.get('result_choice')
        if not isinstance(result_choice, str):
            result_choice = None
        success, msg, result = player.synthesize_monster(
            base_idx, material_idx, inherit_skill_ids=inherit, breeding=breeding,
            result_choice=result_choice,
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
    result_choice = data.get('result_choice')
    if not isinstance(result_choice, str):
        result_choice = None
    return player.preview_synthesis(base_idx, material_idx, result_choice=result_choice), None
