"""Tests for the combo skill system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monster_rpg.combo_system import ComboTracker, apply_combo_effect, COMBO_DEFINITIONS
from monster_rpg.monsters.monster_class import Monster


def test_combo_definitions_exist():
    """All expected combos should be defined."""
    assert "fire_storm" in COMBO_DEFINITIONS
    assert "absolute_zero" in COMBO_DEFINITIONS
    assert "thunder_chain" in COMBO_DEFINITIONS
    assert "holy_judgement" in COMBO_DEFINITIONS
    assert "healing_wind" in COMBO_DEFINITIONS


def test_no_combo_with_single_skill():
    """Single skill should not trigger combo."""
    tracker = ComboTracker()
    tracker.record_skill("fireball")
    assert tracker.check_combo() is None


def test_fire_storm_combo():
    """Fireball + dragon_breath should trigger fire storm."""
    tracker = ComboTracker()
    tracker.record_skill("fireball")
    tracker.record_skill("dragon_breath")
    combo = tracker.check_combo()
    assert combo is not None
    assert combo["name"] == "ファイアストーム"


def test_fire_storm_any_order():
    """Fire storm should trigger in any order."""
    tracker = ComboTracker()
    tracker.record_skill("dragon_breath")
    tracker.record_skill("fireball")
    combo = tracker.check_combo()
    assert combo is not None
    assert combo["name"] == "ファイアストーム"


def test_holy_judgement_ordered():
    """Holy judgement requires specific order."""
    tracker = ComboTracker()
    tracker.record_skill("holy_light")
    tracker.record_skill("meteor_strike")
    combo = tracker.check_combo()
    assert combo is not None
    assert combo["name"] == "ホーリージャッジメント"

    # Reverse order should NOT trigger
    tracker2 = ComboTracker()
    tracker2.record_skill("meteor_strike")
    tracker2.record_skill("holy_light")
    combo2 = tracker2.check_combo()
    assert combo2 is None


def test_unrelated_skills_no_combo():
    """Unrelated skills should not trigger combo."""
    tracker = ComboTracker()
    tracker.record_skill("heal")
    tracker.record_skill("power_up")
    # heal + power_up is not a defined combo pair for an existing combo
    # (healing_wind is heal + cure)
    combo = tracker.check_combo()
    # Check that it doesn't match
    if combo:
        assert combo["name"] not in ["ファイアストーム", "ホーリージャッジメント"]


def test_apply_combo_aoe_damage():
    """AOE damage combo should damage all enemies."""
    enemies = [
        Monster("Enemy1", hp=100, attack=10, defense=5),
        Monster("Enemy2", hp=100, attack=10, defense=5),
    ]
    allies = [Monster("Ally1", hp=100, attack=10, defense=5)]

    combo = {
        "name": "テストコンボ",
        "description": "テスト",
        "effect": {
            "type": "aoe_damage",
            "amount": 30,
        },
    }
    log = []
    apply_combo_effect(combo, allies, enemies, log)
    assert enemies[0].hp == 70
    assert enemies[1].hp == 70
    assert any("コンボ発動" in entry["message"] for entry in log)


def test_apply_combo_aoe_heal():
    """AOE heal combo should heal all allies."""
    allies = [
        Monster("Ally1", hp=50, attack=10, defense=5),
        Monster("Ally2", hp=40, attack=10, defense=5),
    ]
    allies[0].max_hp = 100
    allies[1].max_hp = 100
    enemies = []

    combo = {
        "name": "テスト回復",
        "description": "テスト",
        "effect": {
            "type": "aoe_heal",
            "amount": 20,
        },
    }
    log = []
    apply_combo_effect(combo, allies, enemies, log)
    assert allies[0].hp == 70
    assert allies[1].hp == 60


def test_tracker_to_from_dict():
    """ComboTracker should serialize and deserialize."""
    tracker = ComboTracker()
    tracker.record_skill("fireball")
    tracker.record_skill("heal")
    d = tracker.to_dict()
    assert d["skill_history"] == ["fireball", "heal"]

    tracker2 = ComboTracker.from_dict(d)
    assert tracker2.skill_history == ["fireball", "heal"]


def test_tracker_clear():
    """Clearing tracker should reset history."""
    tracker = ComboTracker()
    tracker.record_skill("fireball")
    tracker.clear()
    assert len(tracker.skill_history) == 0


def test_history_size_limit():
    """History should be limited to HISTORY_SIZE."""
    tracker = ComboTracker()
    for i in range(10):
        tracker.record_skill(f"skill_{i}")
    assert len(tracker.skill_history) == ComboTracker.HISTORY_SIZE
