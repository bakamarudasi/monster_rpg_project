import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple

from .monster_class import (
    Monster,
    GROWTH_TYPE_AVERAGE,
    GROWTH_TYPE_MAGIC,
    RANK_D,
)
from ..skills.skills import ALL_SKILLS
from ..skills.skill_sets import ALL_SKILL_SETS
from ..items.item_data import ALL_ITEMS
from ..items.equipment import ALL_EQUIPMENT


@dataclass
class MonsterBookEntry:
    monster_id: str
    description: str = ""
    location_hint: str = ""
    synthesis_hint: str = ""
    reward: int = 0


# 属性ごとの既定耐性（自属性は半減、特定状態に強い）。値は被ダメ/被状態の係数。
ELEMENT_RESIST_DEFAULTS = {
    "火": {"status": {"burn": 0.0}, "element": {"火": 0.5}},
    "氷": {"status": {"freeze": 0.0}, "element": {"氷": 0.5}},
    "雷": {"status": {"paralyze": 0.5}, "element": {"雷": 0.5}},
    "水": {"status": {"burn": 0.5}, "element": {"水": 0.5}},
    "毒": {"status": {"poison": 0.0, "spore_poison": 0.0}, "element": {"毒": 0.5}},
    "光": {"status": {"blind": 0.5}, "element": {"光": 0.5}},
    "闇": {"status": {"fear": 0.5, "curse": 0.5}, "element": {"闇": 0.5}},
    "風": {"element": {"風": 0.5}},
    "土": {"status": {"paralyze": 0.5}, "element": {"土": 0.5}},
}

# family ごとの既定耐性。生物でないものは毒/呪いに強く、弱点も持つ。
FAMILY_RESIST_DEFAULTS = {
    "undead":    {"status": {"poison": 0.0, "spore_poison": 0.0, "sleep": 0.5}, "element": {"光": 1.25}},
    "construct": {"status": {"poison": 0.0, "spore_poison": 0.0, "curse": 0.5, "fear": 0.0}, "element": {"雷": 1.25}},
    "elemental": {"status": {"poison": 0.0, "stun": 0.5}},
    "demon":     {"status": {"fear": 0.0}, "element": {"光": 1.25}},
    "plant":     {"element": {"火": 1.25, "水": 0.5}},
    "slime":     {"element": {"水": 0.5}},
    "dragon":    {"status": {"fear": 0.5}},
}


def _resolve_resistances(element, family, attrs):
    """属性・family の既定耐性を合成し、JSON の明示指定で上書きして返す。"""
    status: Dict[str, float] = {}
    elem: Dict[str, float] = {}
    for table in (ELEMENT_RESIST_DEFAULTS.get(element, {}),
                  FAMILY_RESIST_DEFAULTS.get((family or "").lower(), {})):
        status.update(table.get("status", {}))
        elem.update(table.get("element", {}))
    status.update({k: float(v) for k, v in attrs.get("status_resist", {}).items()})
    elem.update({k: float(v) for k, v in attrs.get("element_resist", {}).items()})
    return status, elem


def _load_from_json(filepath: str | None = None) -> Tuple[Dict[str, Monster], Dict[str, MonsterBookEntry]]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "monsters.json")

    try:
        with open(filepath, encoding="utf-8") as f:
            text = f.read().replace("\u00a0", " ")
    except FileNotFoundError as e:
        raise ValueError(f"Monster data file not found: {filepath}") from e

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid monster data JSON in {filepath}") from e

    monsters: Dict[str, Monster] = {}
    book_entries: Dict[str, MonsterBookEntry] = {}

    for monster_id, attrs in data.items():
        stats = attrs.get("stats", {})
        growth_type = attrs.get("growth_type", GROWTH_TYPE_AVERAGE)
        # 魔法型は Lv1 から術者として機能するよう、初期魔力を持たせる
        # （JSON で magic を明示していればそれを優先）。魔法スキルは magic 依存。
        default_magic = stats.get("attack", 5) if growth_type == GROWTH_TYPE_MAGIC else 0
        m = Monster(
            name=attrs.get("name", monster_id),
            hp=stats.get("hp", 10),
            attack=stats.get("attack", 5),
            defense=stats.get("defense", 5),
            mp=stats.get("mp", 30),
            level=attrs.get("level", 1),
            element=attrs.get("element"),
            speed=stats.get("speed", 5),
            magic=stats.get("magic", default_magic),
            ai_role=attrs.get("ai_role", "attacker"),
            growth_type=growth_type,
            monster_id=monster_id,
            family=attrs.get("family"),
            rank=attrs.get("rank", RANK_D),
            image_filename=attrs.get("image_filename"),
            skill_sequence=attrs.get("skill_sequence"),
            scout_rate=attrs.get("scout_rate", 0.25),
        )
        skill_ids = list(attrs.get("skills", []))
        for set_id in attrs.get("skill_sets", []):
            sset = ALL_SKILL_SETS.get(set_id)
            if not sset:
                continue
            for lvl, ids in sset.get("learnset", {}).items():
                if lvl <= m.level:
                    if isinstance(ids, str):
                        ids = [ids]
                    for sid in ids:
                        if sid not in skill_ids:
                            skill_ids.append(sid)
        for sid in attrs.get("additional_skills", []):
            if sid not in skill_ids:
                skill_ids.append(sid)
        m.skills = [ALL_SKILLS[s] for s in skill_ids if s in ALL_SKILLS]

        # 耐性（状態異常/属性の被ダメ係数）。属性・family の既定＋JSON 明示で決定
        m.status_resist, m.element_resist = _resolve_resistances(m.element, m.family, attrs)

        # ボス判定: 明示 is_boss、または専用行動台本(skill_sequence)を持つ個体
        m.is_boss = bool(attrs.get("is_boss", bool(attrs.get("skill_sequence"))))

        drops = []
        for item_id, rate in attrs.get("drop_items", []):
            item = ALL_ITEMS.get(item_id) or ALL_EQUIPMENT.get(item_id)
            if item:
                drops.append((item, rate))
        m.drop_items = drops

        # 直接定義の learnset を取り込む（内側のリストもコピーして元データを汚さない）
        learnset: Dict[str, list] = {}
        for key, ids in attrs.get("learnset", {}).items():
            learnset[str(key)] = [ids] if isinstance(ids, str) else list(ids)
        # skill_sets 由来の learnset をマージ。ALL_SKILL_SETS の共有リストは
        # 参照・破壊せず、必ず新しいリストへコピーしてから追記する。
        for set_id in attrs.get("skill_sets", []):
            sset = ALL_SKILL_SETS.get(set_id)
            if not sset:
                continue
            for lvl, ids in sset.get("learnset", {}).items():
                key = str(lvl)
                add_ids = [ids] if isinstance(ids, str) else list(ids)
                existing = learnset.get(key)
                if existing is None:
                    learnset[key] = add_ids
                    continue
                for sid in add_ids:
                    if sid not in existing:
                        existing.append(sid)
        m.learnset = {int(k): v for k, v in learnset.items()}

        monsters[monster_id] = m

        book = attrs.get("book", {})
        book_entries[monster_id] = MonsterBookEntry(
            monster_id=monster_id,
            description=book.get("description", ""),
            location_hint=book.get("location_hint", ""),
            synthesis_hint=book.get("synthesis_hint", ""),
            reward=book.get("reward", 0),
        )

    return monsters, book_entries


def load_monsters(filepath: str | None = None) -> Tuple[Dict[str, Monster], Dict[str, MonsterBookEntry]]:
    """Public wrapper for loading monsters from a JSON file."""
    return _load_from_json(filepath)


def get_all_monsters() -> Dict[str, Monster]:
    """Return the dictionary of all loaded monsters."""
    return ALL_MONSTERS


# Load monster data at import time
ALL_MONSTERS, MONSTER_BOOK_DATA = _load_from_json()


# Provide direct access to common monsters
SLIME = ALL_MONSTERS.get("slime")
