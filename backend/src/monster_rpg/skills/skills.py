"""Skill class and JSON loader."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Any


class Skill:
    """Represents an ability usable in battle."""

    def __init__(
        self,
        name: str,
        power: int,
        cost: int = 0,
        skill_type: str = "attack",
        effects: List[dict] | None = None,
        target: str = "enemy",
        scope: str = "single",
        duration: int = 0,
        description: str = "",
        category: str | None = None,
    ) -> None:
        self.name = name
        self.power = power
        self.cost = cost
        self.skill_type = skill_type
        self.effects = effects or []
        self.target = target
        self.scope = scope
        self.duration = duration
        self.description = description
        self.category = category

    def describe(self) -> str:  # pragma: no cover - simple helper
        scope_text = "全体" if self.scope == "all" else "単体"
        cost_text = f"MP:{self.cost}" if self.cost else ""
        return f"{self.name} ({self.skill_type}, Pow:{self.power}, {cost_text} {scope_text})"


def load_skills(filepath: str | None = None) -> Dict[str, Skill]:
    """Load skills from a JSON file."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "skills.json")

    try:
        with open(filepath, encoding="utf-8") as f:
            text = f.read().replace("\u00a0", " ")
    except FileNotFoundError as e:
        raise ValueError(f"Skill data file not found: {filepath}") from e

    try:
        data: Dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid skill data JSON in {filepath}") from e

    skills: Dict[str, Skill] = {}
    for skill_id, attrs in data.items():
        skills[skill_id] = Skill(
            name=attrs.get("name", skill_id),
            power=attrs.get("power", 0),
            cost=attrs.get("cost", 0),
            skill_type=attrs.get("skill_type", "attack"),
            effects=attrs.get("effects", []),
            target=attrs.get("target", "enemy"),
            scope=attrs.get("scope", "single"),
            duration=attrs.get("duration", 0),
            description=attrs.get("description", ""),
            category=attrs.get("category"),
        )
    return skills


# Load default skills on import
ALL_SKILLS: Dict[str, Skill] = load_skills()
