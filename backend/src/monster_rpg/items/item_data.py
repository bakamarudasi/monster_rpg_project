"""Item class and JSON loader."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Any


class Item:
    """Simple item data container."""

    def __init__(self, item_id: str, name: str, description: str, usable: bool = False, effects: List[dict] | None = None):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.usable = usable
        self.effects = effects or []

    def __repr__(self) -> str:  # pragma: no cover - simple debug helper
        return f"Item({self.item_id})"


def load_items(filepath: str | None = None) -> Dict[str, Item]:
    """Load item definitions from a JSON file."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "items.json")

    try:
        with open(filepath, encoding="utf-8") as f:
            text = f.read().replace("\u00a0", " ")
    except FileNotFoundError as e:
        raise ValueError(f"Item data file not found: {filepath}") from e

    try:
        data: Dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid item data JSON in {filepath}") from e

    items: Dict[str, Item] = {}
    for item_id, attrs in data.items():
        items[item_id] = Item(
            item_id=item_id,
            name=attrs.get("name", item_id),
            description=attrs.get("description", ""),
            usable=attrs.get("usable", False),
            effects=attrs.get("effects", []),
        )
    return items


# Load default items on import
ALL_ITEMS: Dict[str, Item] = load_items()
