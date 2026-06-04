"""Functions for synthesizing monsters and items."""

from __future__ import annotations

import copy
import random
from typing import Tuple, Optional

from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
from .monsters.personality import inherit_personality_id, inherit_ivs, DEFAULT_INHERIT_COUNT
from .monsters.synthesis_rules import (
    SYNTHESIS_RECIPES,
    SYNTHESIS_ITEMS_REQUIRED,
    MONSTER_ITEM_RECIPES,
    ITEM_ITEM_RECIPES,
    SPECIAL_MONSTER_POOL,
    RANK_VALUES,
    find_family_synthesis_result,
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


# 配合で継承できるスキルの最大数
MAX_INHERIT_SKILLS = 3

# レア個体（★）の出現基礎確率
RARE_INDIVIDUAL_BASE_CHANCE = 0.07
# ジャックポット（特殊配合・大当たり）の基礎確率
JACKPOT_BASE_CHANCE = 0.03


def _rank_value(monster: Monster) -> int:
    return RANK_VALUES.get(str(getattr(monster, "rank", "")).upper(), 0)


def _jackpot_chance(parent1: Monster, parent2: Monster) -> float:
    """親のランクと＋値が高いほど大当たり確率が上がる（最大30%）。"""
    rank_sum = _rank_value(parent1) + _rank_value(parent2)          # 0〜10
    plus_sum = getattr(parent1, "plus_value", 0) + getattr(parent2, "plus_value", 0)
    chance = JACKPOT_BASE_CHANCE + rank_sum * 0.015 + min(plus_sum, 20) * 0.005
    return min(0.30, chance)


def _rare_individual_chance(parent1: Monster, parent2: Monster) -> float:
    """＋値が高いほどレア個体が出やすい（最大25%）。"""
    plus_sum = getattr(parent1, "plus_value", 0) + getattr(parent2, "plus_value", 0)
    return min(0.25, RARE_INDIVIDUAL_BASE_CHANCE + min(plus_sum, 20) * 0.006)


def _roll_jackpot_result(parent1: Monster, parent2: Monster) -> Optional[str]:
    """非レシピ配合時のジャックポット抽選。当たればダーク童話の住人IDを返す。"""
    if random.random() >= _jackpot_chance(parent1, parent2):
        return None
    pool = [m for m in SPECIAL_MONSTER_POOL if m in ALL_MONSTERS]
    rank_sum = _rank_value(parent1) + _rank_value(parent2)
    # 最高レア（終焉の語り部）は十分に強い親同士でのみ抽選対象
    if rank_sum < 7:
        pool = [m for m in pool if m != "tale_devourer"]
    return random.choice(pool) if pool else None


def _apply_rare_individual(monster: Monster) -> None:
    """レア個体（★）化。実体は Monster.make_rare_individual に集約（進化の覚醒と共通）。"""
    monster.make_rare_individual()


def resolve_synthesis_result(parent1: Monster, parent2: Monster):
    """親2体から合成結果のモンスターIDを解決する。

    戻り値は (result_id or None, recipe_key or None)。recipe_key はレシピ配合の
    ときのみ非Noneで、必要触媒アイテムの判定に使う。
    """
    id1 = (parent1.monster_id or "").lower()
    id2 = (parent2.monster_id or "").lower()
    recipe_key = tuple(sorted([id1, id2]))
    if recipe_key in SYNTHESIS_RECIPES:
        return SYNTHESIS_RECIPES[recipe_key], recipe_key
    result_id = find_family_synthesis_result(
        parent1.family, parent1.rank, parent2.family, parent2.rank
    )
    return result_id, None


def inheritable_skills(parent1: Monster, parent2: Monster) -> dict:
    """両親の所持スキルの和集合（同名は1つ）。name -> skill_obj の辞書。"""
    pool: dict = {}
    for parent in (parent1, parent2):
        for sk in (parent.skills or []):
            nm = getattr(sk, "name", None)
            if nm and nm not in pool:
                pool[nm] = sk
    return pool


def _compute_child_plus(parent1: Monster, parent2: Monster) -> int:
    """配合の累代＋値。高い方を引き継ぎつつ最低でも+1される。"""
    return max(getattr(parent1, "plus_value", 0), getattr(parent2, "plus_value", 0)) + 1


def _build_child(parent1: Monster, parent2: Monster, result_id: str, inherit_skill_ids=None, breeding=None) -> Monster:
    """合成結果のモンスターを生成（スキル継承・ステ補正・累代＋値・個体値遺伝を適用）。

    ``breeding`` は配合補助アイテムの効果（``inherit_count`` / ``power_stats`` /
    ``everstone_parent``）を表す辞書。None なら通常の継承（個体値3継承・性格は親or変異）。
    """
    new_monster = ALL_MONSTERS[result_id].copy()

    existing = {getattr(s, "name", None) for s in new_monster.skills}
    chosen: list = []
    if inherit_skill_ids is None:
        # 後方互換: 各親からランダムに1つずつ継承
        for parent in (parent1, parent2):
            if parent.skills:
                sk = random.choice(parent.skills)
                nm = getattr(sk, "name", None)
                if nm and nm not in existing and nm not in {c.name for c in chosen}:
                    chosen.append(copy.deepcopy(sk))
    else:
        pool = inheritable_skills(parent1, parent2)
        for key in list(inherit_skill_ids)[:MAX_INHERIT_SKILLS]:
            sk = pool.get(key)
            if sk is None:
                # スキルIDで指定された場合は name に解決して照合
                from .skills.skills import ALL_SKILLS
                obj = ALL_SKILLS.get(key)
                if obj is not None:
                    sk = pool.get(getattr(obj, "name", None))
            if sk is not None:
                nm = getattr(sk, "name", None)
                if nm and nm not in existing and nm not in {c.name for c in chosen}:
                    chosen.append(copy.deepcopy(sk))
    new_monster.skills.extend(chosen)

    avg_level = (parent1.level + parent2.level) / 2
    new_monster.max_hp += int(avg_level * 2)
    new_monster.base_attack += int(avg_level)
    new_monster.base_defense += int(avg_level)
    new_monster.base_speed += int(avg_level * 0.5)
    new_monster.level = 1
    new_monster.exp = 0

    # 累代＋値（強い親ほど強い子になるループ）
    new_monster.add_plus_value(_compute_child_plus(parent1, parent2))

    # 個性の継承：性格はどちらかの親（稀に変異／かわらずのいしで確定）、個体値はステ
    # ごとに親から引き継ぐ（ポケモンの遺伝に準拠）。あかいいとで継承数3→5、パワー系で
    # 指定ステを確定継承。良個体値を集めて厳選＝才能（鬼才）を狙う配合ループの核。
    breeding = breeding or {}
    new_monster.personality_id = inherit_personality_id(
        getattr(parent1, "personality_id", None),
        getattr(parent2, "personality_id", None),
        everstone_parent=breeding.get("everstone_parent"),
    )
    new_monster.ivs = inherit_ivs(
        getattr(parent1, "ivs", None),
        getattr(parent2, "ivs", None),
        inherit_count=breeding.get("inherit_count", DEFAULT_INHERIT_COUNT),
        power_stats=breeding.get("power_stats") or None,
    )
    new_monster.iv_appraised = False

    new_monster.hp = new_monster.max_hp
    new_monster.mp = new_monster.max_mp
    new_monster.is_alive = True
    return new_monster


def preview_synthesis(player: "Player", monster1_idx: int, monster2_idx: int, item_id: str | None = None) -> dict:
    """配合結果を確定せずに予測する（種族・予測ステ・継承候補スキル・＋値）。"""
    if not (0 <= monster1_idx < len(player.party_monsters) and 0 <= monster2_idx < len(player.party_monsters)):
        return {"ok": False, "message": "無効なモンスターの選択です。"}
    if monster1_idx == monster2_idx:
        return {"ok": False, "message": "同じモンスター同士は合成できません。"}
    p1 = player.party_monsters[monster1_idx]
    p2 = player.party_monsters[monster2_idx]
    if not p1.monster_id or not p2.monster_id:
        return {"ok": False, "message": "合成元のモンスターにIDがありません。"}

    result_id, recipe_key = resolve_synthesis_result(p1, p2)
    if not result_id or result_id not in ALL_MONSTERS:
        return {"ok": False, "message": f"{p1.name} と {p2.name} では何も生まれない…"}

    required_item = SYNTHESIS_ITEMS_REQUIRED.get(recipe_key) if recipe_key else None
    has_item = required_item is None or any(
        getattr(it, "item_id", None) == required_item for it in player.items
    )

    child = _build_child(p1, p2, result_id, inherit_skill_ids=[])  # スキル無しでステ予測
    base_skill_names = {getattr(s, "name", None) for s in ALL_MONSTERS[result_id].skills}
    pool = inheritable_skills(p1, p2)
    skills = [{"id": nm, "name": nm} for nm in pool.keys() if nm not in base_skill_names]

    return {
        "ok": True,
        "result_id": result_id,
        "result_name": child.name,
        "element": child.element,
        "rank": child.rank,
        "plus_value": child.plus_value,
        "stats": {
            "max_hp": child.max_hp,
            "attack": child.attack,
            "defense": child.defense,
            "speed": child.speed,
        },
        "skills": skills,
        "max_inherit": MAX_INHERIT_SKILLS,
        "required_item": (ALL_ITEMS[required_item].name if required_item in ALL_ITEMS else required_item) if required_item else None,
        "has_required_item": has_item,
        "message": "",
    }


def synthesize_monster(player: "Player", monster1_idx: int, monster2_idx: int, item_id: str | None = None, inherit_skill_ids=None, breeding=None) -> Tuple[bool, str, Optional[Monster]]:
    if not (0 <= monster1_idx < len(player.party_monsters) and 0 <= monster2_idx < len(player.party_monsters)):
        return False, "無効なモンスターの選択です。", None
    if monster1_idx == monster2_idx:
        return False, "同じモンスター同士は合成できません。", None

    parent1 = player.party_monsters[monster1_idx]
    parent2 = player.party_monsters[monster2_idx]

    # ロックされた個体は素材にしない（事故防止）
    locked = [p.name for p in (parent1, parent2) if getattr(p, "locked", False)]
    if locked:
        return False, f"{'・'.join(locked)} はロックされている。合成するには解除が必要。", None

    if not parent1.monster_id or not parent2.monster_id:
        return False, "エラー: 合成元のモンスターにIDが設定されていません。", None

    result_monster_id, recipe_key = resolve_synthesis_result(parent1, parent2)
    if not result_monster_id or result_monster_id not in ALL_MONSTERS:
        return False, f"{parent1.name} と {parent2.name} の組み合わせでは何も生まれなかった...", None

    # レシピ配合で触媒アイテムが必要な場合は消費する
    if recipe_key is not None:
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

    # 大当たり抽選（家系配合など、特定レシピ以外でのみ発生）
    is_jackpot = False
    if recipe_key is None:
        jackpot_id = _roll_jackpot_result(parent1, parent2)
        if jackpot_id:
            result_monster_id = jackpot_id
            is_jackpot = True

    new_monster = _build_child(parent1, parent2, result_monster_id, inherit_skill_ids=inherit_skill_ids, breeding=breeding)

    # レア個体（★）抽選
    if random.random() < _rare_individual_chance(parent1, parent2):
        _apply_rare_individual(new_monster)

    indices_to_remove = sorted([monster1_idx, monster2_idx], reverse=True)
    removed_monster_names = []
    for idx in indices_to_remove:
        removed_monster_names.append(player.party_monsters.pop(idx).name)
    player.party_monsters.append(new_monster)
    player.monster_book.record_captured(new_monster.monster_id)

    # 進行フラグ＆実績判定（初合成・レア誕生・捕獲数の節目など）
    player.story_flags.add("synthesized")
    if new_monster.is_rare:
        player.story_flags.add("rare_born")
    from .achievements import check_achievements
    achv = check_achievements(player)

    star = "★" if new_monster.is_rare else ""
    plus_txt = f"（+{new_monster.plus_value}）" if new_monster.plus_value else ""
    if is_jackpot:
        prefix = "✨大当たり！✨ "
    elif new_monster.is_rare:
        prefix = "✨レア個体出現！✨ "
    else:
        prefix = ""
    msg = f"{prefix}{removed_monster_names[1]} と {removed_monster_names[0]} を合成して {star}{new_monster.name}{plus_txt} が誕生した！"
    # 生まれた個体の個性（性格・才能）を知らせる。隠し才能はとくに強調する。
    talent = new_monster.talent
    msg += f" 性格は『{new_monster.personality.name}』、才能は『{talent.name}』。"
    if talent.hidden:
        msg = f"🌟隠し才能『{talent.name}』が覚醒！🌟 " + msg
    if achv:
        msg += " " + " ".join(achv)
    return True, msg, new_monster


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
