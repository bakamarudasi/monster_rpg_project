"""Tests for the monster trait (特性) system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.monsters.traits import (
    apply_attack_trait,
    apply_defense_trait,
    check_on_hit_trait,
    check_fatal_survive,
    get_drain_percent,
    get_regen_amount,
    get_mp_regen,
    get_status_resist,
    get_exp_multiplier,
    get_scout_bonus,
    get_speed_multiplier,
    get_trait,
    TRAIT_DEFINITIONS,
)


def test_trait_definitions_exist():
    """All expected traits should be defined."""
    assert len(TRAIT_DEFINITIONS) > 0
    assert "fierce" in TRAIT_DEFINITIONS
    assert "iron_wall" in TRAIT_DEFINITIONS
    assert "regenerator" in TRAIT_DEFINITIONS
    assert "last_stand" in TRAIT_DEFINITIONS


def test_fierce_attack_multiplier():
    """Fierce trait should increase attack damage by ~15%."""
    damage = apply_attack_trait("fierce", 200)
    # 200 * 1.15 = 230.0
    assert damage == 230


def test_berserker_low_hp():
    """Berserker trait should increase damage when HP is low."""
    # Normal HP
    normal = apply_attack_trait("berserker", 200, attacker_hp_ratio=0.5)
    assert normal == 200
    # Low HP
    low = apply_attack_trait("berserker", 200, attacker_hp_ratio=0.2)
    assert low == 300


def test_ambush_first_strike():
    """Ambush trait should boost damage on first strike."""
    first = apply_attack_trait("ambush", 200, is_first_strike=True)
    assert first == 250
    normal = apply_attack_trait("ambush", 200, is_first_strike=False)
    assert normal == 200


def test_iron_wall_defense():
    """Iron wall should reduce incoming damage by 15%."""
    damage = apply_defense_trait("iron_wall", 200)
    assert damage == 170


def test_fire_resist():
    """Fire resist should reduce fire damage by 30%."""
    fire_damage = apply_defense_trait("fire_resist", 200, attacker_element="火")
    assert fire_damage == 140
    # Non-fire damage should be unaffected
    normal_damage = apply_defense_trait("fire_resist", 200, attacker_element="水")
    assert normal_damage == 200


def test_on_hit_status():
    """Poison body should return poison status on hit."""
    result = check_on_hit_trait("poison_body")
    assert result is not None
    assert result[0] == "poison"
    assert result[1] == 0.20


def test_fatal_survive():
    """Last stand trait should survive fatal blow once."""
    assert check_fatal_survive("last_stand", already_triggered=False) is True
    assert check_fatal_survive("last_stand", already_triggered=True) is False
    assert check_fatal_survive(None, already_triggered=False) is False


def test_drain_percent():
    """Life steal trait should return 10% drain."""
    assert get_drain_percent("life_steal") == 0.10
    assert get_drain_percent(None) == 0.0


def test_regen_amount():
    """Regenerator trait should heal 5% of max HP."""
    assert get_regen_amount("regenerator", 100) == 5
    assert get_regen_amount(None, 100) == 0


def test_mp_regen():
    """Mana flow trait should restore 3 MP."""
    assert get_mp_regen("mana_flow") == 3
    assert get_mp_regen(None) == 0


def test_exp_multiplier():
    """EXP boost trait should give 1.2x exp."""
    assert get_exp_multiplier("exp_boost") == 1.20
    assert get_exp_multiplier(None) == 1.0


def test_scout_bonus():
    """Scout charm should give 15% bonus."""
    assert get_scout_bonus("scout_charm") == 0.15
    assert get_scout_bonus(None) == 0.0


def test_speed_multiplier():
    """Swift trait should give 1.2x speed."""
    assert get_speed_multiplier("swift") == 1.20
    assert get_speed_multiplier(None) == 1.0


def test_slow_starter():
    """Slow starter should scale damage with turn count."""
    t0 = apply_attack_trait("slow_starter", 200, turn_count=0)
    assert t0 == 200
    t5 = apply_attack_trait("slow_starter", 200, turn_count=5)
    assert t5 == 250  # 5 * 0.05 = 0.25 -> 1.25x -> 200 * 1.25 = 250
    t10 = apply_attack_trait("slow_starter", 200, turn_count=10)
    assert t10 == 260  # capped at 30% -> 200 * 1.30 = 260


def test_monster_trait_from_json():
    """Monsters loaded from JSON should have traits."""
    from monster_rpg.monsters.monster_data import ALL_MONSTERS
    slime = ALL_MONSTERS.get("slime")
    assert slime is not None
    assert slime.trait == "thick_hide"

    wolf = ALL_MONSTERS.get("wolf")
    assert wolf is not None
    assert wolf.trait == "ambush"


def test_monster_to_dict_includes_trait():
    """Monster to_dict should include trait field."""
    m = Monster("Test", hp=50, attack=10, defense=5, trait="fierce")
    d = m.to_dict()
    assert d["trait"] == "fierce"


def test_monster_copy_preserves_trait():
    """Monster copy should preserve trait."""
    m = Monster("Test", hp=50, attack=10, defense=5, trait="iron_wall")
    c = m.copy()
    assert c.trait == "iron_wall"
