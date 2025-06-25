"""Functions for managing player parties and inventories."""

from __future__ import annotations

import copy
from typing import Optional

from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
from .items.item_data import ALL_ITEMS
from .items.equipment import (
    CRAFTING_RECIPES,
    create_titled_equipment,
    EquipmentInstance,
    Equipment,
    _generate_random_sub_stat,
)
from .items.equipment_synthesis import EQUIPMENT_SYNTHESIS_RULES
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player


def add_monster_to_party(player: "Player", monster_id_or_object) -> Optional[Monster]:
    """Add a monster to the player's active party."""
    newly_added_monster = None
    if isinstance(monster_id_or_object, str):
        monster_id_key = monster_id_or_object.lower()
        if monster_id_key in ALL_MONSTERS:
            new_monster_instance = ALL_MONSTERS[monster_id_key].copy()
            if new_monster_instance is None:
                print(f"エラー: モンスター '{monster_id_key}' のコピーに失敗しました。")
                return None
            new_monster_instance.level = 1
            new_monster_instance.exp = 0
            new_monster_instance.hp = new_monster_instance.max_hp
            new_monster_instance.mp = new_monster_instance.max_mp
            player.party_monsters.append(new_monster_instance)
            print(f"{new_monster_instance.name} が仲間に加わった！")
            newly_added_monster = new_monster_instance
        else:
            print(f"エラー: モンスターID '{monster_id_key}' は存在しません。")
    elif isinstance(monster_id_or_object, Monster):
        monster_object = monster_id_or_object
        copied_monster = monster_object.copy()
        if copied_monster is None:
            print(f"エラー: モンスターオブジェクト '{monster_object.name}' のコピーに失敗しました。")
            return None
        player.party_monsters.append(copied_monster)
        copied_monster.mp = copied_monster.max_mp
        print(f"{copied_monster.name} が仲間に加わった！")
        newly_added_monster = copied_monster
    else:
        print("エラー: add_monster_to_party の引数が不正です。")

    if newly_added_monster:
        print(
            f"[DEBUG add_monster_to_party] Actual monster_id of added monster '{newly_added_monster.name}': '{newly_added_monster.monster_id}' (type: {type(newly_added_monster.monster_id)})"
        )
        player.monster_book.record_captured(newly_added_monster.monster_id)
        return newly_added_monster
    return None


def show_all_party_monsters_status(player: "Player") -> None:
    if not player.party_monsters:
        print(f"{player.name} はまだ仲間モンスターを持っていません。")
        return

    print(f"===== {player.name} のパーティーメンバー詳細 =====")
    for i, monster in enumerate(player.party_monsters):
        print(f"--- {i+1}. ---")
        monster.show_status()
    print("=" * 30)


def move_monster(player: "Player", from_idx: int, to_idx: int) -> bool:
    if not (0 <= from_idx < len(player.party_monsters) and 0 <= to_idx < len(player.party_monsters)):
        return False
    monster = player.party_monsters.pop(from_idx)
    player.party_monsters.insert(to_idx, monster)
    return True


def move_to_reserve(player: "Player", party_idx: int) -> bool:
    if not (0 <= party_idx < len(player.party_monsters)):
        return False
    if len(player.party_monsters) <= 1:
        return False
    monster = player.party_monsters.pop(party_idx)
    player.reserve_monsters.append(monster)
    return True


def move_from_reserve(player: "Player", reserve_idx: int) -> bool:
    if not (0 <= reserve_idx < len(player.reserve_monsters)):
        return False
    monster = player.reserve_monsters.pop(reserve_idx)
    player.party_monsters.append(monster)
    return True


def reset_formation(player: "Player") -> None:
    while len(player.party_monsters) > 1:
        player.reserve_monsters.append(player.party_monsters.pop())


def show_items(player: "Player") -> None:
    if not player.items:
        print("アイテムを何も持っていない。")
        return

    print("===== 所持アイテム =====")
    for i, item in enumerate(player.items, 1):
        name = getattr(item, "name", str(item))
        desc = getattr(item, "description", "")
        print(f"{i}. {name} - {desc}")
    print("=" * 20)


def use_item(player: "Player", item_idx: int, target_monster: Monster) -> bool:
    if not (0 <= item_idx < len(player.items)):
        print("無効なアイテム番号です。")
        return False

    item = player.items[item_idx]
    from .items import apply_item_effect

    success = apply_item_effect(item, target_monster)
    if success:
        player.items.pop(item_idx)
    return success


def rest_at_inn(player: "Player", cost: int) -> bool:
    if player.gold >= cost:
        player.gold -= cost
        print(f"{cost}G を支払い、宿屋に泊まった。")
        for monster in player.party_monsters:
            monster.hp = monster.max_hp
            monster.mp = monster.max_mp
            monster.is_alive = True
        print("パーティは完全に回復した！")
        return True
    else:
        print("お金が足りない！宿屋に泊まれない...")
        return False


def buy_item(player: "Player", item_id: str, price: int) -> bool:
    if player.gold < price:
        print("お金が足りない！")
        return False
    if item_id not in ALL_ITEMS:
        print("そのアイテムは存在しない。")
        return False
    player.gold -= price
    player.items.append(ALL_ITEMS[item_id])
    print(f"{ALL_ITEMS[item_id].name} を {price}G で購入した。")
    return True


def buy_monster(player: "Player", monster_id: str, price: int) -> bool:
    if player.gold < price:
        print("お金が足りない！")
        return False
    if monster_id not in ALL_MONSTERS:
        print("そのモンスターは存在しない。")
        return False
    player.gold -= price
    add_monster_to_party(player, monster_id)
    print(f"{ALL_MONSTERS[monster_id].name} を {price}G で仲間にした。")
    return True


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


MATERIAL_MAPPING = {
    "weapon": {"common": "weapon_core_common", "rare": "weapon_core_rare"},
    "armor": {"common": "armor_fragment_common", "rare": "armor_fragment_rare"},
}


def disassemble_equipment(player: "Player", equip_instance_id: str):
    """Break down equipment and award materials."""
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
        print("その装備を所持していない。")
        return False

    category = equip.base_item.category
    rarity = getattr(equip.base_item, "rarity", "common")
    item_id = MATERIAL_MAPPING.get(category, {}).get(rarity)
    if not item_id or item_id not in ALL_ITEMS:
        print("分解できない装備だ。")
        return False

    player.equipment_inventory.pop(idx)
    player.items.append(ALL_ITEMS[item_id])
    print(f"{equip.name} を分解して {ALL_ITEMS[item_id].name} を手に入れた。")
    return True


def limit_break_equipment(player: "Player", equip_instance_id: str) -> bool:
    """Upgrade equipment using synthesis materials."""
    equip = None
    for e in player.equipment_inventory:
        if isinstance(e, EquipmentInstance) and e.instance_id == equip_instance_id:
            equip = e
            break
        if not isinstance(e, EquipmentInstance) and getattr(e, "equip_id", None) == equip_instance_id:
            equip = EquipmentInstance(base_item=e, title=None)
            player.equipment_inventory.remove(e)
            player.equipment_inventory.append(equip)
            break

    if equip is None:
        print("その装備を所持していない。")
        return False

    rules = EQUIPMENT_SYNTHESIS_RULES.get(equip.base_item.category, [])
    next_rank = equip.synthesis_rank + 1
    rule = next((r for r in rules if r.get("rank") == next_rank), None)
    if not rule:
        print("これ以上強化できない。")
        return False

    for c in rule.get("cost", []):
        item_id = c.get("item_id")
        amount = int(c.get("amount", 0))
        have = sum(1 for it in player.items if getattr(it, "item_id", None) == item_id)
        if have < amount:
            print("素材が足りない。")
            return False

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
    print(f"{equip.name} がランク{equip.synthesis_rank}になった！")
    return True


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
