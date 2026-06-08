"""Functions for managing player parties and inventories."""

from __future__ import annotations

from typing import Optional

from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
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
