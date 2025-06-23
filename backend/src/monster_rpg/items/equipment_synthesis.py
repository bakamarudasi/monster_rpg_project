import json
import os
from typing import Dict, Any


def load_rules(filepath: str | None = None) -> Dict[str, Any]:
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "equipment_synthesis_rules.json")
    try:
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError as e:
        raise ValueError(f"Rules file not found: {filepath}") from e
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {filepath}") from e


EQUIPMENT_SYNTHESIS_RULES: Dict[str, Any] = load_rules()
