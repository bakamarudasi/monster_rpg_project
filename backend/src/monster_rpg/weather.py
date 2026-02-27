"""Battle weather system (天候システム).

Weather changes dynamically during battle and modifies damage, healing,
status effect chances, and other mechanics.
"""

from __future__ import annotations

import random
from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# Weather definitions
# ---------------------------------------------------------------------------

WEATHER_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "sunny": {
        "name": "晴天",
        "description": "火属性ダメージ+20%、水属性ダメージ-20%",
        "element_bonus": {"火": 1.20},
        "element_penalty": {"水": 0.80},
        "icon": "sun",
    },
    "rain": {
        "name": "豪雨",
        "description": "水属性ダメージ+20%、火属性ダメージ-20%",
        "element_bonus": {"水": 1.20},
        "element_penalty": {"火": 0.80},
        "icon": "rain",
    },
    "storm": {
        "name": "嵐",
        "description": "雷属性ダメージ+30%、命中率-10%",
        "element_bonus": {"雷": 1.30},
        "accuracy_penalty": 0.10,
        "icon": "storm",
    },
    "fog": {
        "name": "濃霧",
        "description": "命中率-15%、素早さ-10%",
        "accuracy_penalty": 0.15,
        "speed_modifier": 0.90,
        "icon": "fog",
    },
    "blizzard": {
        "name": "吹雪",
        "description": "氷属性ダメージ+25%、毎ターン微量ダメージ",
        "element_bonus": {"氷": 1.25},
        "dot_damage_percent": 0.02,
        "icon": "snow",
    },
    "sandstorm": {
        "name": "砂嵐",
        "description": "土属性ダメージ+20%、毎ターン微量ダメージ",
        "element_bonus": {"土": 1.20},
        "dot_damage_percent": 0.03,
        "immune_elements": ["土"],
        "icon": "sand",
    },
    "darkness": {
        "name": "暗闇",
        "description": "闇属性ダメージ+25%、光属性ダメージ-15%",
        "element_bonus": {"闇": 1.25},
        "element_penalty": {"光": 0.85},
        "icon": "dark",
    },
    "holy_light": {
        "name": "聖光",
        "description": "光属性ダメージ+25%、回復量+20%",
        "element_bonus": {"光": 1.25},
        "heal_modifier": 1.20,
        "icon": "light",
    },
}


class BattleWeather:
    """Manages weather state during a battle."""

    # Probability of weather changing each turn
    CHANGE_CHANCE = 0.15
    # Maximum turns a weather can last
    MAX_DURATION = 5
    # Minimum turns before weather can change
    MIN_DURATION = 2

    def __init__(self, initial_weather: Optional[str] = None):
        if initial_weather and initial_weather in WEATHER_DEFINITIONS:
            self.current = initial_weather
        else:
            self.current: Optional[str] = None  # None = clear/normal weather
        self.turns_active = 0
        self.forced_duration = 0  # If set by a skill, weather won't change randomly

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        if self.current is None:
            return None
        return WEATHER_DEFINITIONS.get(self.current)

    @property
    def name(self) -> str:
        if self.current is None:
            return "通常"
        d = WEATHER_DEFINITIONS.get(self.current)
        return d["name"] if d else "通常"

    def set_weather(self, weather_id: str, duration: int = 0) -> None:
        """Force a specific weather (e.g. from a skill)."""
        if weather_id in WEATHER_DEFINITIONS:
            self.current = weather_id
            self.turns_active = 0
            self.forced_duration = duration

    def clear(self) -> None:
        """Clear all weather effects."""
        self.current = None
        self.turns_active = 0
        self.forced_duration = 0

    def advance_turn(self, log: Optional[List[Dict[str, str]]] = None) -> None:
        """Process turn progression for weather."""
        if log is None:
            log = []

        self.turns_active += 1

        # If forced duration, count down
        if self.forced_duration > 0:
            self.forced_duration -= 1
            if self.forced_duration <= 0:
                log.append({
                    'type': 'weather',
                    'message': f"天候「{self.name}」がおさまった。",
                })
                self.clear()
            return

        # Random weather changes
        if self.current is not None and self.turns_active >= self.MIN_DURATION:
            if self.turns_active >= self.MAX_DURATION or random.random() < self.CHANGE_CHANCE:
                log.append({
                    'type': 'weather',
                    'message': f"天候「{self.name}」がおさまった。",
                })
                self.clear()
                return

        # Random chance to start new weather
        if self.current is None and random.random() < 0.10:
            new_weather = random.choice(list(WEATHER_DEFINITIONS.keys()))
            self.current = new_weather
            self.turns_active = 0
            d = WEATHER_DEFINITIONS[new_weather]
            log.append({
                'type': 'weather',
                'message': f"天候が「{d['name']}」に変わった！ {d['description']}",
            })

    def get_damage_modifier(self, attacker_element: Optional[str]) -> float:
        """Return damage multiplier based on weather and attacker element."""
        if self.current is None or attacker_element is None:
            return 1.0
        d = WEATHER_DEFINITIONS.get(self.current, {})

        # Check bonus
        bonus = d.get("element_bonus", {}).get(attacker_element, 1.0)
        # Check penalty
        penalty = d.get("element_penalty", {}).get(attacker_element, 1.0)

        return bonus * penalty

    def get_heal_modifier(self) -> float:
        """Return healing multiplier based on weather."""
        if self.current is None:
            return 1.0
        d = WEATHER_DEFINITIONS.get(self.current, {})
        return float(d.get("heal_modifier", 1.0))

    def get_accuracy_penalty(self) -> float:
        """Return accuracy penalty (0.0 - 1.0) that reduces hit chance."""
        if self.current is None:
            return 0.0
        d = WEATHER_DEFINITIONS.get(self.current, {})
        return float(d.get("accuracy_penalty", 0.0))

    def get_speed_modifier(self) -> float:
        """Return speed modifier applied to all monsters."""
        if self.current is None:
            return 1.0
        d = WEATHER_DEFINITIONS.get(self.current, {})
        return float(d.get("speed_modifier", 1.0))

    def get_dot_damage(self, max_hp: int, element: Optional[str] = None) -> int:
        """Return weather DOT damage (0 if immune)."""
        if self.current is None:
            return 0
        d = WEATHER_DEFINITIONS.get(self.current, {})
        pct = d.get("dot_damage_percent", 0)
        if not pct:
            return 0
        immune = d.get("immune_elements", [])
        if element and element in immune:
            return 0
        return max(1, int(max_hp * pct))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current": self.current,
            "turns_active": self.turns_active,
            "forced_duration": self.forced_duration,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BattleWeather":
        w = cls(initial_weather=data.get("current"))
        w.turns_active = data.get("turns_active", 0)
        w.forced_duration = data.get("forced_duration", 0)
        return w
