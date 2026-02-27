"""Functions for synthesizing monsters and items (強化版)."""

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
    find_family_synthesis_result,
    get_synthesis_trait_bonus,
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

# ---------------------------------------------------------------------------
# Enhanced skill inheritance
# ---------------------------------------------------------------------------

def _inherit_skills(parent1: Monster, parent2: Monster, child: Monster, max_inherit: int = 3) -> list:
    """Inherit skills from parents to child.

    Enhanced version: inherits up to max_inherit skills, prioritizing
    rare/powerful skills and avoiding duplicates.
    """
    inherited = []
    parent_skills = []
    for parent in (parent1, parent2):
        for skill in parent.skills:
            if getattr(skill, "name", None) not in [s.name for s in child.skills + inherited]:
                parent_skills.append(skill)

    # Sort by cost (higher cost = rarer/more powerful)
    parent_skills.sort(key=lambda s: getattr(s, "cost", 0), reverse=True)

    for skill in parent_skills[:max_inherit]:
        inherited.append(copy.deepcopy(skill))

    return inherited


def _calculate_stat_bonus(parent1: Monster, parent2: Monster) -> dict:
    """Calculate stat bonuses for the synthesized monster.

    Enhanced version: bonuses scale with parent levels and ranks.
    """
    avg_level = (parent1.level + parent2.level) / 2
    from .monsters.synthesis_rules import RANK_VALUES
    r1 = RANK_VALUES.get(parent1.rank, 0)
    r2 = RANK_VALUES.get(parent2.rank, 0)
    rank_bonus = (r1 + r2) / 2

    return {
        "hp": int(avg_level * 2 + rank_bonus * 3),
        "attack": int(avg_level + rank_bonus * 1.5),
        "defense": int(avg_level + rank_bonus * 1.5),
        "speed": int(avg_level * 0.5 + rank_bonus),
        "magic": int(avg_level * 0.3 + rank_bonus),
    }


def _create_child_from_template(
    result_monster_id: str,
    parent1: Monster,
    parent2: Monster,
) -> Optional[Monster]:
    """Create a child monster from template with inherited stats/skills."""
    if result_monster_id not in ALL_MONSTERS:
        return None

    template = ALL_MONSTERS[result_monster_id]
    child = template.copy()
    if child is None:
        return None

    # Inherit skills
    inherited_skills = _inherit_skills(parent1, parent2, child)
    child.skills.extend(inherited_skills)

    # Apply stat bonuses
    bonuses = _calculate_stat_bonus(parent1, parent2)
    child.max_hp += bonuses["hp"]
    child.base_attack += bonuses["attack"]
    child.base_defense += bonuses["defense"]
    child.base_speed += bonuses["speed"]
    child.base_magic += bonuses["magic"]

    # Check for trait bonus from synthesis
    bonus_trait = get_synthesis_trait_bonus(result_monster_id)
    if bonus_trait:
        child.trait = bonus_trait

    child.level = 1
    child.exp = 0
    child.hp = child.max_hp
    child.mp = child.max_mp
    child.is_alive = True

    return child


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
        new_monster = _create_child_from_template(result_monster_id, parent1, parent2)
        if new_monster is None:
            return False, f"エラー: 合成結果のモンスター '{result_monster_id}' の生成に失敗しました。", None

        indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
        removed_monster_names = []
        for idx in indices_to_remove:
            removed_monster_names.append(player.party_monsters.pop(idx).name)
        player.party_monsters.append(new_monster)
        player.monster_book.record_captured(new_monster.monster_id)

        rank_msg = f" (ランク: {new_monster.rank})" if new_monster.rank else ""
        trait_msg = ""
        if new_monster.trait:
            from .monsters.traits import get_trait
            trait_data = get_trait(new_monster.trait)
            if trait_data:
                trait_msg = f" 特性「{trait_data['name']}」を持っている！"

        return True, f"{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {new_monster.name} が誕生した！{rank_msg}{trait_msg}", new_monster
    else:
        result_monster_id = find_family_synthesis_result(
            parent1.family, parent1.rank, parent2.family, parent2.rank
        )
        if result_monster_id and result_monster_id in ALL_MONSTERS:
            new_monster = _create_child_from_template(result_monster_id, parent1, parent2)
            if new_monster is None:
                return False, f"エラー: 合成結果のモンスター '{result_monster_id}' の生成に失敗しました。", None

            indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
            removed_monster_names = []
            for idx in indices_to_remove:
                removed_monster_names.append(player.party_monsters.pop(idx).name)
            player.party_monsters.append(new_monster)
            player.monster_book.record_captured(new_monster.monster_id)
            return True, f"{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {new_monster.name} が誕生した！", new_monster

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

    # アイテム合成でも親のスキルを一部引き継ぎ
    parent_skills = parent.skills[:]
    for skill in parent_skills[:2]:
        if getattr(skill, "name", None) not in [s.name for s in new_mon.skills]:
            new_mon.skills.append(copy.deepcopy(skill))

    # 親のレベルに応じたボーナス
    level_bonus = parent.level // 3
    new_mon.max_hp += level_bonus * 2
    new_mon.base_attack += level_bonus
    new_mon.base_defense += level_bonus

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


def get_possible_synthesis_results(player: "Player") -> list:
    """Return a list of possible synthesis results for the player's current party.

    Each entry is a dict with monster indices and the expected result.
    """
    results = []
    party = player.party_monsters
    for i in range(len(party)):
        for j in range(i + 1, len(party)):
            m1, m2 = party[i], party[j]
            key = tuple(sorted([m1.monster_id.lower(), m2.monster_id.lower()]))
            if key in SYNTHESIS_RECIPES:
                result_id = SYNTHESIS_RECIPES[key]
                template = ALL_MONSTERS.get(result_id)
                if template:
                    required_item = SYNTHESIS_ITEMS_REQUIRED.get(key)
                    has_item = True
                    if required_item:
                        has_item = any(
                            getattr(it, "item_id", None) == required_item
                            for it in player.items
                        )
                    results.append({
                        "idx1": i,
                        "idx2": j,
                        "monster1": m1.name,
                        "monster2": m2.name,
                        "result_name": template.name,
                        "result_rank": template.rank,
                        "required_item": required_item,
                        "has_item": has_item,
                        "type": "recipe",
                    })
            else:
                result_id = find_family_synthesis_result(
                    m1.family, m1.rank, m2.family, m2.rank
                )
                if result_id and result_id in ALL_MONSTERS:
                    template = ALL_MONSTERS[result_id]
                    results.append({
                        "idx1": i,
                        "idx2": j,
                        "monster1": m1.name,
                        "monster2": m2.name,
                        "result_name": template.name,
                        "result_rank": template.rank,
                        "type": "family",
                    })
    return results
