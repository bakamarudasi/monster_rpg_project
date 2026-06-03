"""装備ドメイン：作成・装着・分解・限界突破。

party_manager に同居していた装備系ロジックを分離したもの。CLI/Web どちらからも
使えるよう Flask 非依存。分解・限界突破は結果メッセージを返し、表示は呼び出し側に委ねる。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .items.item_data import ALL_ITEMS
from .items.equipment import (
    CRAFTING_RECIPES,
    create_titled_equipment,
    EquipmentInstance,
    _generate_random_sub_stat,
)
from .items.equipment_synthesis import EQUIPMENT_SYNTHESIS_RULES

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player


# 分解時、装備カテゴリ×レアリティ から得られる素材アイテム
MATERIAL_MAPPING = {
    "weapon": {"common": "weapon_core_common", "rare": "weapon_core_rare"},
    "armor": {"common": "armor_fragment_common", "rare": "armor_fragment_rare"},
}


def craft_equipment(player: "Player", equip_id: str):
    recipe = CRAFTING_RECIPES.get(equip_id)
    if not recipe:
        print("その装備は作成できない。")
        return None
    for item_id, qty in recipe.items():
        count = sum(1 for it in player.items if getattr(it, "item_id", None) == item_id)
        if count < qty:
            print("素材が足りない。")
            return None
    for item_id, qty in recipe.items():
        removed = 0
        for i in range(len(player.items) - 1, -1, -1):
            if getattr(player.items[i], "item_id", None) == item_id and removed < qty:
                player.items.pop(i)
                removed += 1
    new_equip = create_titled_equipment(equip_id)
    if new_equip:
        player.equipment_inventory.append(new_equip)
        print(f"{new_equip.name} を作成した！")
        return new_equip
    print("装備の作成に失敗した。")
    return None


def equip_to_monster(player: "Player", party_idx: int, equip_id: str | None = None, slot: str | None = None) -> bool:
    if not (0 <= party_idx < len(player.party_monsters)):
        print("無効なモンスター番号")
        return False

    monster = player.party_monsters[party_idx]

    if equip_id is None:
        if slot is None or slot not in monster.equipment:
            print("そのスロットには装備がない。")
            return False
        equip = monster.equipment.pop(slot)
        player.equipment_inventory.append(equip)
        print(f"{monster.name} の {slot} を外した。")
        return True

    equip = None
    for e in player.equipment_inventory:
        if isinstance(e, EquipmentInstance):
            if e.instance_id == equip_id or e.base_item.equip_id == equip_id:
                equip = e
                break
        else:
            if getattr(e, "equip_id", None) == equip_id:
                equip = e
                break
    if not equip:
        print("その装備を所持していない。")
        return False

    monster.equip(equip)
    player.equipment_inventory.remove(equip)
    print(f"{monster.name} に {equip.name} を装備した。")
    return True


def disassemble_equipment(player: "Player", equip_instance_id: str) -> tuple[bool, str]:
    """装備を分解して素材を得る。戻り値 (success, message)。"""
    idx = None
    equip = None
    for i, e in enumerate(player.equipment_inventory):
        if isinstance(e, EquipmentInstance) and e.instance_id == equip_instance_id:
            idx = i
            equip = e
            break
        if not isinstance(e, EquipmentInstance) and getattr(e, "equip_id", None) == equip_instance_id:
            idx = i
            equip = EquipmentInstance(base_item=e, title=None)
            break
    if equip is None or idx is None:
        return False, "その装備を所持していない。"

    category = equip.base_item.category
    rarity = getattr(equip.base_item, "rarity", "common")
    item_id = MATERIAL_MAPPING.get(category, {}).get(rarity)
    if not item_id or item_id not in ALL_ITEMS:
        return False, "分解できない装備だ。"

    player.equipment_inventory.pop(idx)
    player.items.append(ALL_ITEMS[item_id])
    return True, f"{equip.name} を分解して {ALL_ITEMS[item_id].name} を手に入れた。"


def limit_break_equipment(player: "Player", equip_instance_id: str) -> tuple[bool, str]:
    """装備を限界突破（合成ランクを1段階上げる）。戻り値 (success, message)。"""
    equip = None
    idx = None
    convert_later = False
    for i, e in enumerate(player.equipment_inventory):
        if isinstance(e, EquipmentInstance) and e.instance_id == equip_instance_id:
            equip = e
            idx = i
            break
        if not isinstance(e, EquipmentInstance) and getattr(e, "equip_id", None) == equip_instance_id:
            equip = e
            idx = i
            convert_later = True
            break

    if equip is None:
        return False, "その装備を所持していない。"

    base_item = equip.base_item if isinstance(equip, EquipmentInstance) else equip
    current_rank = equip.synthesis_rank if isinstance(equip, EquipmentInstance) else 0
    rules = EQUIPMENT_SYNTHESIS_RULES.get(base_item.category, [])
    next_rank = current_rank + 1
    rule = next((r for r in rules if r.get("rank") == next_rank), None)
    if not rule:
        return False, "これ以上強化できない。"

    for c in rule.get("cost", []):
        item_id = c.get("item_id")
        amount = int(c.get("amount", 0))
        have = sum(1 for it in player.items if getattr(it, "item_id", None) == item_id)
        if have < amount:
            return False, "素材が足りない。"

    if convert_later:
        equip = EquipmentInstance(base_item=equip, title=None)
        player.equipment_inventory[idx] = equip

    for c in rule.get("cost", []):
        item_id = c.get("item_id")
        amount = int(c.get("amount", 0))
        removed = 0
        for i in range(len(player.items) - 1, -1, -1):
            if getattr(player.items[i], "item_id", None) == item_id and removed < amount:
                player.items.pop(i)
                removed += 1

    equip.synthesis_rank = next_rank
    bonus_type = rule.get("bonus_type")
    value = rule.get("value")
    if bonus_type == "base_stats_multiplier" and isinstance(value, (int, float)):
        equip.stat_multiplier *= float(value)
    elif bonus_type == "add_sub_stat_slot":
        equip.sub_stat_slots += int(value)
        current = equip.random_bonuses.setdefault("sub_stats", [])
        used = {s.get("stat") for s in current}
        while len(current) < equip.sub_stat_slots:
            bonus = _generate_random_sub_stat(equip.base_item.category, used)
            if not bonus:
                break
            current.append(bonus)
            used.add(bonus["stat"])
    return True, f"{equip.name} がランク{equip.synthesis_rank}になった！"
