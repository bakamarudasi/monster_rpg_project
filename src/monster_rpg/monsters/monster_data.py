import json
import os
from dataclasses import dataclass
from typing import Dict, Tuple

from .monster_class import (
    Monster,
    GROWTH_TYPE_AVERAGE,
    RANK_D,
)
from ..skills.skills import ALL_SKILLS
from ..items.item_data import ALL_ITEMS
from ..items.equipment import ALL_EQUIPMENT


@dataclass
class MonsterBookEntry:
    monster_id: str
    description: str = ""
    location_hint: str = ""
    synthesis_hint: str = ""
    reward: int = 0


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
        m = Monster(
            name=attrs.get("name", monster_id),
            hp=stats.get("hp", 10),
            attack=stats.get("attack", 5),
            defense=stats.get("defense", 5),
            mp=stats.get("mp", 30),
            level=attrs.get("level", 1),
            element=attrs.get("element"),
            speed=stats.get("speed", 5),
            ai_role=attrs.get("ai_role", "attacker"),
            growth_type=attrs.get("growth_type", GROWTH_TYPE_AVERAGE),
            monster_id=monster_id,
            rank=attrs.get("rank", RANK_D),
            image_filename=attrs.get("image_filename"),
        )
        m.skills = [ALL_SKILLS[s] for s in attrs.get("skills", []) if s in ALL_SKILLS]

        drops = []
        for item_id, rate in attrs.get("drop_items", []):
            item = ALL_ITEMS.get(item_id) or ALL_EQUIPMENT.get(item_id)
            if item:
                drops.append((item, rate))
        m.drop_items = drops

        learnset = attrs.get("learnset", {})
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


# Load monster data at import time
ALL_MONSTERS, MONSTER_BOOK_DATA = _load_from_json()

# Additional learnsets applied to loaded monsters for compatibility
_LEARNSETS = {
    "slime": {2: ["guard_up"]},
    "goblin": {3: ["power_up"]},
    "wolf": {4: ["speed_up"]},
}
for mid, ls in _LEARNSETS.items():
    if mid in ALL_MONSTERS:
        ALL_MONSTERS[mid].learnset.update(ls)

# Provide direct access to common monsters
SLIME = ALL_MONSTERS.get("slime")
