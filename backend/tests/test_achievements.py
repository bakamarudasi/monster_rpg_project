"""Tests for the achievement system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from monster_rpg.achievements import AchievementManager, ACHIEVEMENT_DEFINITIONS


def test_achievement_definitions_exist():
    """All expected achievements should be defined."""
    assert "first_victory" in ACHIEVEMENT_DEFINITIONS
    assert "win_10" in ACHIEVEMENT_DEFINITIONS
    assert "first_scout" in ACHIEVEMENT_DEFINITIONS
    assert "first_synthesis" in ACHIEVEMENT_DEFINITIONS


def test_unlock_achievement():
    """Unlocking an achievement should return True and add to unlocked."""
    mgr = AchievementManager()
    log = []
    result = mgr.check_and_unlock("first_victory", log)
    assert result is True
    assert "first_victory" in mgr.unlocked
    assert any("実績解除" in entry["message"] for entry in log)


def test_no_double_unlock():
    """Same achievement should not unlock twice."""
    mgr = AchievementManager()
    mgr.check_and_unlock("first_victory")
    result = mgr.check_and_unlock("first_victory")
    assert result is False


def test_record_battle_win():
    """Battle wins should unlock progressively."""
    mgr = AchievementManager()
    log = []
    mgr.record_battle_win(log=log)
    assert "first_victory" in mgr.unlocked
    assert mgr.stats["battles_won"] == 1


def test_record_battle_win_no_damage():
    """No damage win should unlock special achievement."""
    mgr = AchievementManager()
    log = []
    mgr.record_battle_win(no_damage=True, log=log)
    assert "no_damage_win" in mgr.unlocked


def test_record_scout():
    """Scout should unlock first_scout."""
    mgr = AchievementManager()
    log = []
    mgr.record_scout(log=log)
    assert "first_scout" in mgr.unlocked


def test_record_synthesis():
    """Synthesis should unlock first_synthesis."""
    mgr = AchievementManager()
    log = []
    mgr.record_synthesis(log=log)
    assert "first_synthesis" in mgr.unlocked


def test_record_synthesis_s_rank():
    """S rank synthesis should unlock special achievement."""
    mgr = AchievementManager()
    log = []
    mgr.record_synthesis(result_rank="S", log=log)
    assert "synthesis_s_rank" in mgr.unlocked


def test_record_evolution():
    """Evolution should unlock evolution_first."""
    mgr = AchievementManager()
    log = []
    mgr.record_evolution(log=log)
    assert "evolution_first" in mgr.unlocked


def test_record_gold():
    """Gold milestones should unlock."""
    mgr = AchievementManager()
    log = []
    mgr.record_gold(1500, log=log)
    assert "rich_1000" in mgr.unlocked
    assert "rich_10000" not in mgr.unlocked


def test_record_monster_book():
    """Monster book milestones should unlock."""
    mgr = AchievementManager()
    log = []
    mgr.record_monster_book(15, log=log)
    assert "monster_10" in mgr.unlocked
    assert "monster_30" not in mgr.unlocked


def test_collect_rewards():
    """Collecting rewards should return gold total."""
    mgr = AchievementManager()
    mgr.check_and_unlock("first_victory")
    mgr.check_and_unlock("first_scout")
    total = mgr.collect_rewards()
    assert total > 0
    # After collecting, pending should be empty
    assert mgr.collect_rewards() == 0


def test_get_all_achievements():
    """Should return all achievements with status."""
    mgr = AchievementManager()
    mgr.check_and_unlock("first_victory")
    all_achs = mgr.get_all_achievements()
    assert len(all_achs) == len(ACHIEVEMENT_DEFINITIONS)

    fv = next(a for a in all_achs if a["id"] == "first_victory")
    assert fv["unlocked"] is True

    w10 = next(a for a in all_achs if a["id"] == "win_10")
    assert w10["unlocked"] is False


def test_to_from_dict():
    """AchievementManager should serialize and deserialize."""
    mgr = AchievementManager()
    mgr.record_battle_win()  # This unlocks first_victory AND increments counter
    mgr.record_battle_win()  # Second win
    d = mgr.to_dict()

    mgr2 = AchievementManager.from_dict(d)
    assert "first_victory" in mgr2.unlocked
    assert mgr2.stats["battles_won"] == 2


def test_combo_master_at_10():
    """Combo master should unlock after 10 combos."""
    mgr = AchievementManager()
    for _ in range(10):
        mgr.record_combo()
    assert "combo_master" in mgr.unlocked
