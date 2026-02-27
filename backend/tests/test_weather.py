"""Tests for the weather battle system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monster_rpg.weather import BattleWeather, WEATHER_DEFINITIONS


def test_weather_definitions_exist():
    """All expected weather types should be defined."""
    assert "sunny" in WEATHER_DEFINITIONS
    assert "rain" in WEATHER_DEFINITIONS
    assert "storm" in WEATHER_DEFINITIONS
    assert "fog" in WEATHER_DEFINITIONS
    assert "blizzard" in WEATHER_DEFINITIONS
    assert "sandstorm" in WEATHER_DEFINITIONS
    assert "darkness" in WEATHER_DEFINITIONS
    assert "holy_light" in WEATHER_DEFINITIONS


def test_default_weather_is_none():
    """Default weather should be None (clear)."""
    w = BattleWeather()
    assert w.current is None
    assert w.name == "通常"


def test_set_weather():
    """Setting weather should change current weather."""
    w = BattleWeather()
    w.set_weather("sunny")
    assert w.current == "sunny"
    assert w.name == "晴天"


def test_clear_weather():
    """Clearing weather should reset to none."""
    w = BattleWeather("rain")
    w.clear()
    assert w.current is None


def test_sunny_fire_bonus():
    """Sunny weather should boost fire damage by 20%."""
    w = BattleWeather("sunny")
    assert w.get_damage_modifier("火") == 1.20


def test_sunny_water_penalty():
    """Sunny weather should reduce water damage by 20%."""
    w = BattleWeather("sunny")
    assert w.get_damage_modifier("水") == 0.80


def test_rain_water_bonus():
    """Rain should boost water damage."""
    w = BattleWeather("rain")
    assert w.get_damage_modifier("水") == 1.20


def test_storm_accuracy_penalty():
    """Storm should have accuracy penalty."""
    w = BattleWeather("storm")
    assert w.get_accuracy_penalty() == 0.10


def test_fog_speed_modifier():
    """Fog should reduce speed."""
    w = BattleWeather("fog")
    assert w.get_speed_modifier() == 0.90


def test_blizzard_dot():
    """Blizzard should deal DOT damage."""
    w = BattleWeather("blizzard")
    dot = w.get_dot_damage(100, element="火")
    assert dot == 2  # 2% of 100


def test_sandstorm_immune():
    """Earth element should be immune to sandstorm DOT."""
    w = BattleWeather("sandstorm")
    dot_earth = w.get_dot_damage(100, element="土")
    assert dot_earth == 0
    dot_fire = w.get_dot_damage(100, element="火")
    assert dot_fire == 3  # 3% of 100


def test_holy_light_heal_modifier():
    """Holy light should boost healing by 20%."""
    w = BattleWeather("holy_light")
    assert w.get_heal_modifier() == 1.20


def test_no_weather_modifiers():
    """No weather should return neutral modifiers."""
    w = BattleWeather()
    assert w.get_damage_modifier("火") == 1.0
    assert w.get_heal_modifier() == 1.0
    assert w.get_accuracy_penalty() == 0.0
    assert w.get_speed_modifier() == 1.0
    assert w.get_dot_damage(100) == 0


def test_to_from_dict():
    """Weather should serialize and deserialize."""
    w = BattleWeather("storm")
    w.turns_active = 3
    w.forced_duration = 2
    d = w.to_dict()
    assert d["current"] == "storm"
    assert d["turns_active"] == 3

    w2 = BattleWeather.from_dict(d)
    assert w2.current == "storm"
    assert w2.turns_active == 3
    assert w2.forced_duration == 2


def test_forced_duration_countdown():
    """Forced weather should count down and clear."""
    w = BattleWeather()
    w.set_weather("rain", duration=2)
    log = []
    w.advance_turn(log)
    assert w.current == "rain"  # still active (1 remaining)
    w.advance_turn(log)
    assert w.current is None  # cleared after duration
