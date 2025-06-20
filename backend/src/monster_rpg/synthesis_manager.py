"""Functions for synthesizing monsters and items."""

from __future__ import annotations

import copy
import random
from typing import Tuple, Optional

from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
from .monsters.synthesis_rules import (
    SYNTHESIS_RECIPES,
    SYNTHESIS_ITEMS_REQUIRED,
    MONSTER_ITEM_RECIPES,
    ITEM_ITEM_RECIPES,
)
from .items.item_data import ALL_ITEMS
from .items.equipment import (
    create_titled_equipment,
    EquipmentInstance,
    Equipment,
    ALL_EQUIPMENT,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player

DEBUG_MODE = False


def synthesize_monster(player: "Player", monster1_idx: int, monster2_idx: int, item_id: str | None = None) -> Tuple[bool, str, Optional[Monster]]:
    if not (0 <= monster1_idx < len(player.party_monsters) and 0 <= monster2_idx < len(player.party_monsters)):
        return False, "無効なモンスターの選択です。", None
    if monster1_idx == monster2_idx:
        return False, "同じモンスター同士は合成できません。", None

    parent1 = player.party_monsters[monster1_idx]
    parent2 = player.party_monsters[monster2_idx]

    if not parent1.monster_id or not parent2.monster_id:
        return False, "エラー: 合成元のモンスターにIDが設定されていません。", None

    id1_lower = parent1.monster_id.lower()
    id2_lower = parent2.monster_id.lower()
    recipe_key = tuple(sorted([id1_lower, id2_lower]))

    if recipe_key in SYNTHESIS_RECIPES:
        required_item = SYNTHESIS_ITEMS_REQUIRED.get(recipe_key)
        if required_item:
            item_index = next(
                (i for i, itm in enumerate(player.items) if getattr(itm, "item_id", None) == required_item),
                None,
            )
            if item_index is None:
                item_name = ALL_ITEMS[required_item].name if required_item in ALL_ITEMS else required_item
                return False, f"合成には {item_name} が必要だ。", None
            player.items.pop(item_index)

        result_monster_id = SYNTHESIS_RECIPES[recipe_key]
        if result_monster_id in ALL_MONSTERS:
            base_new_monster_template = ALL_MONSTERS[result_monster_id]
            new_monster = base_new_monster_template.copy()
            if new_monster is None:
                return False, f"エラー: 合成結果のモンスター '{result_monster_id}' の生成に失敗しました。", None

            inherited_skills = []
            for parent in (parent1, parent2):
                if parent.skills:
                    skill = random.choice(parent.skills)
                    current_names = [s.name for s in new_monster.skills + inherited_skills]
                    if getattr(skill, "name", None) not in current_names:
                        inherited_skills.append(copy.deepcopy(skill))
            new_monster.skills.extend(inherited_skills)

            avg_level = (parent1.level + parent2.level) / 2
            hp_bonus = int(avg_level * 2)
            atk_bonus = int(avg_level)
            def_bonus = int(avg_level)
            spd_bonus = int(avg_level * 0.5)
            new_monster.max_hp += hp_bonus
            new_monster.attack += atk_bonus
            new_monster.defense += def_bonus
            new_monster.speed += spd_bonus
            new_monster.level = 1
            new_monster.exp = 0
            new_monster.hp = new_monster.max_hp
            new_monster.is_alive = True

            indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
            removed_monster_names = []
            for idx in indices_to_remove:
                removed_monster_names.append(player.party_monsters.pop(idx).name)
            player.party_monsters.append(new_monster)
            player.monster_book.record_captured(new_monster.monster_id)
            return True, f"{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {new_monster.name} が誕生した！", new_monster
        else:
            return False, f"エラー: 合成結果のモンスターID '{result_monster_id}' がモンスター定義に存在しません。", None
    else:
        return False, f"{parent1.name} と {parent2.name} の組み合わせでは何も生まれなかった...", None


def synthesize_monster_with_item(player: "Player", monster_idx: int, item_id: str) -> Tuple[bool, str, Optional[Monster]]:
    if not (0 <= monster_idx < len(player.party_monsters)):
        return False, "無効なモンスターの選択です。", None

    item_index = next(
        (i for i, it in enumerate(player.items) if getattr(it, "item_id", None) == item_id),
        None,
    )
    if item_index is None:
        return False, "そのアイテムを所持していない。", None

    parent = player.party_monsters[monster_idx]
    recipe_key = (parent.monster_id.lower(), item_id)

    if recipe_key not in MONSTER_ITEM_RECIPES:
        item_name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
        return False, f"{parent.name} と {item_name} では何も起こらなかった...", None

    result_id = MONSTER_ITEM_RECIPES[recipe_key]
    if result_id not in ALL_MONSTERS:
        return False, f"エラー: 合成結果のモンスターID '{result_id}' が見つかりません。", None

    new_mon = ALL_MONSTERS[result_id].copy()
    if new_mon is None:
        return False, f"エラー: 合成結果のモンスター '{result_id}' の生成に失敗しました。", None

    removed_name = player.party_monsters.pop(monster_idx).name
    player.items.pop(item_index)

    new_mon.level = 1
    new_mon.exp = 0
    new_mon.hp = new_mon.max_hp
    new_mon.is_alive = True
    player.party_monsters.append(new_mon)
    player.monster_book.record_captured(new_mon.monster_id)

    item_name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
    return True, f"{removed_name} と {item_name} を合成して {new_mon.name} が誕生した！", new_mon


def synthesize_items(player: "Player", item1_id: str, item2_id: str):
    key = tuple(sorted([item1_id, item2_id]))
    if key not in ITEM_ITEM_RECIPES:
        return False, "その組み合わせでは何も起こらなかった...", None

    def remove_material(iid: str):
        for idx, it in enumerate(player.items):
            if getattr(it, "item_id", None) == iid:
                return player.items.pop(idx)
        for idx, eq in enumerate(player.equipment_inventory):
            if isinstance(eq, EquipmentInstance):
                if eq.base_item.equip_id == iid:
                    return player.equipment_inventory.pop(idx)
            elif getattr(eq, "equip_id", None) == iid:
                return player.equipment_inventory.pop(idx)
        return None

    mat1 = remove_material(item1_id)
    if not mat1:
        return False, "素材が足りない。", None
    mat2 = remove_material(item2_id)
    if not mat2:
        if isinstance(mat1, (Equipment, EquipmentInstance)):
            player.equipment_inventory.append(mat1)
        else:
            player.items.append(mat1)
        return False, "素材が足りない。", None

    result_id = ITEM_ITEM_RECIPES[key]
    if result_id in ALL_ITEMS:
        new_obj = ALL_ITEMS[result_id]
        player.items.append(new_obj)
    elif result_id in ALL_EQUIPMENT:
        new_obj = create_titled_equipment(result_id)
        if new_obj:
            player.equipment_inventory.append(new_obj)
    else:
        return False, "レシピ結果が不明です。", None

    return True, f"{getattr(new_obj, 'name', '')} を手に入れた！", new_obj
