"""Skill set loader module."""

from __future__ import annotations

import json
import os
from typing import Dict, Any


def load_skill_sets(filepath: str | None = None) -> Dict[str, Dict[str, Any]]:
    """Load skill set data from JSON file."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "skill_sets.json")

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        raise ValueError(f"Skill set data file not found: {filepath}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid skill set JSON in {filepath}") from e

    sets: Dict[str, Dict[str, Any]] = {}
    for set_id, attrs in data.items():
        learnset = attrs.get("learnset", {})
        sets[set_id] = {
            "name": attrs.get("name", set_id),
            "learnset": {int(k): v for k, v in learnset.items()},
        }
    return sets


# Load default skill sets on import
ALL_SKILL_SETS: Dict[str, Dict[str, Any]] = load_skill_sets()
