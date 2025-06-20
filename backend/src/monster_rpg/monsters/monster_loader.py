from typing import Dict, Tuple

from .monster_class import Monster
from .monster_data import MonsterBookEntry, load_monsters as _load_from_data


def load_monsters(filepath: str | None = None) -> Tuple[Dict[str, Monster], Dict[str, MonsterBookEntry]]:
    """Load monsters and monster book entries from a JSON file."""
    return _load_from_data(filepath)
