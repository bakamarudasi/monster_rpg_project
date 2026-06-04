"""戦闘のアプリケーションサービス。

web/battle.py のルートに直書きされていたオーケストレーション
（HTTP パラメータ → アクション変換 / 戦闘開始 / 終了時の報酬計算）を集約する。
シリアライズ（JSON 化）は url_for に依存する presentation 都合のためルート側に残す。
ここは Flask 非依存。
"""

from __future__ import annotations

import random

from ..battle import start_atb_battle
from ..items.equipment import Equipment, EquipmentInstance, create_titled_equipment
from ..map_data import LOCATIONS
from ..exploration import generate_enemy_party


def _to_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_player_action(data_src) -> dict:
    """HTTP のフォーム/JSON から Battle.process_player_action 用のアクション辞書を作る。"""
    action = data_src.get('action', 'attack')
    if action == 'run':
        return {'type': 'run'}
    if action.startswith('skill'):
        return {
            'type': 'skill',
            'skill': _to_int(action[5:], 0),
            'target_enemy': _to_int(data_src.get('target_enemy', '-1'), -1),
            'target_ally': _to_int(data_src.get('target_ally', '0'), 0),
        }
    if action == 'item':
        return {
            'type': 'item',
            'item_idx': _to_int(data_src.get('item_idx', '-1'), -1),
            'target_ally': _to_int(data_src.get('target_ally', '0'), 0),
        }
    if action == 'scout':
        return {'type': 'scout', 'target_enemy': _to_int(data_src.get('target_enemy', '-1'), -1)}
    return {'type': 'attack', 'target_enemy': _to_int(data_src.get('target_enemy', '-1'), -1)}


def start_new_battle(player):
    """現在地で新しい戦闘を開始する。

    戻り値 (battle_obj, error)。error は None / 'no_location' / 'no_enemies'。
    """
    loc = LOCATIONS.get(player.current_location_id)
    if not loc:
        return None, 'no_location'
    enemies = generate_enemy_party(loc, player)
    if not enemies:
        return None, 'no_enemies'
    battle_obj = start_atb_battle(player.party_monsters, enemies, player)
    enemy_names = ', '.join(e.name for e in enemies)
    battle_obj.log.append({'type': 'info', 'message': f'{enemy_names} が現れた！'})
    # ボス個体がいれば登場演出を出す
    for e in enemies:
        if getattr(e, 'is_boss', False):
            battle_obj.log.append({'type': 'boss', 'message': f'⚠ {e.name} が立ちはだかった！'})
    return battle_obj, None


def apply_battle_rewards(player, outcome, player_party, enemy_party, log) -> list:
    """戦闘終了時の報酬（経験値・ゴールド・ドロップ）を適用し、表示用メッセージ列を返す。

    log は戦闘ログ。これに結果メッセージを足したものを返す（呼び出し側が
    last_battle_log への保存・表示を行う）。
    """
    msgs = log[:]
    if outcome == 'win':
        total_exp = sum(e.level * 10 for e in enemy_party)
        gold_gain = sum(e.level * 5 for e in enemy_party)
        alive_members = [m for m in player_party if m.is_alive]
        if alive_members and total_exp:
            share = total_exp // len(alive_members)
            for m in alive_members:
                m.gain_exp(share)
        player.gold += gold_gain
        for enemy in enemy_party:
            for item_obj, rate in getattr(enemy, 'drop_items', []):
                if random.random() < rate:
                    if isinstance(item_obj, Equipment):
                        new_equip = create_titled_equipment(item_obj.equip_id)
                        if new_equip:
                            player.equipment_inventory.append(new_equip)
                            msgs.append({'type': 'item_drop', 'message': f'{new_equip.name} を手に入れた！', 'item_name': new_equip.name})
                        else:
                            msgs.append({'type': 'info', 'message': f'{item_obj.name} を手に入れ損ねた...'})
                    elif isinstance(item_obj, EquipmentInstance):
                        player.equipment_inventory.append(item_obj)
                        msgs.append({'type': 'item_drop', 'message': f'{item_obj.name} を手に入れた！', 'item_name': item_obj.name})
                    else:
                        player.items.append(item_obj)
                        msgs.append({'type': 'item_drop', 'message': f'{item_obj.name} を手に入れた！', 'item_name': item_obj.name})
        msgs.append({'type': 'info', 'message': f'勝利した！ {gold_gain}G を得た。'})
    elif outcome == 'fled':
        msgs.append({'type': 'info', 'message': 'うまく逃げ切れた！'})
    else:
        msgs.append({'type': 'info', 'message': '敗北してしまった...'})

    # 実績判定（ボス撃破フラグ＋捕獲数などの節目）
    if outcome == 'win' and any(getattr(e, 'is_boss', False) for e in enemy_party):
        player.story_flags.add('boss_defeated')
    from ..achievements import check_achievements
    check_achievements(player, msgs)
    return msgs
