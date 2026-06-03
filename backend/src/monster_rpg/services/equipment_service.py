"""装備まわりのアプリケーションサービス（装着・強化・分解・限界突破）。

ルートが直接ドメインを叩き、応答データやメッセージを組み立てていた処理を集約する。
永続化（セーブ）は呼び出し側＝Web 層の責務として残す。
"""

from __future__ import annotations

from ..items.equipment import EquipmentInstance
from ..enhancement import (
    enhance_equipment,
    enhance_cost,
    required_material_names,
    ENHANCE_MAX,
)


def equip(player, party_idx: int, equip_id, slot):
    """装備を装着/解除し、画面更新用データとともに結果を返す。

    戻り値 (success, data)。data は equipment_inventory / monster_equipment /
    monster_stats を含み、ルートはそのまま JSON にできる。
    """
    normalized = equip_id if equip_id not in ['', None] else None
    success = player.equip_to_monster(party_idx, normalized, slot)
    monster = player.party_monsters[party_idx]
    data = {
        'equipment_inventory': [
            {
                'id': (e.instance_id if isinstance(e, EquipmentInstance)
                       else getattr(e, 'equip_id', str(e))),
                'name': getattr(e, 'name', ''),
            }
            for e in player.equipment_inventory
        ],
        'monster_equipment': {slot: eq.name for slot, eq in monster.equipment.items()},
        'monster_stats': {
            'attack': monster.total_attack(),
            'defense': monster.total_defense(),
            'speed': monster.total_speed(),
        },
    }
    return success, data


def enhance(player, instance_id: str):
    """装備を強化する。戻り値 (success, message)。"""
    return enhance_equipment(player, instance_id)


def disassemble(player, instance_id: str):
    """装備を分解して素材を得る。戻り値 (success, message)。"""
    if player.disassemble_equipment(instance_id):
        return True, '装備を分解して素材を手に入れた。'
    return False, '分解できなかった。'


def limit_break(player, instance_id: str):
    """装備を限界突破（合成ランクを1段階上げる）する。戻り値 (success, message)。"""
    if player.limit_break_equipment(instance_id):
        return True, '限界突破に成功した！'
    return False, '限界突破できなかった（素材不足など）。'


def enhance_entries(player):
    """強化画面用に、所持装備を強化情報つきの一覧として組み立てる。"""
    entries = []
    for eq in player.equipment_inventory:
        level = getattr(eq, 'enhance_level', 0)
        entries.append({
            'instance_id': getattr(eq, 'instance_id', ''),
            'name': eq.name,
            'slot': eq.slot,
            'attack': eq.total_attack,
            'defense': eq.total_defense,
            'speed': eq.total_speed,
            'level': level,
            'maxed': level >= ENHANCE_MAX,
            'cost': enhance_cost(level),
            'material': required_material_names(eq.slot),
            'rank': getattr(eq, 'synthesis_rank', 0),
        })
    return entries
