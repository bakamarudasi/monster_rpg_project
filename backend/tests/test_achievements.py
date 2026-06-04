"""実績＆進行データ（progress）のテスト。"""

import unittest

from monster_rpg.player import Player
from monster_rpg.achievements import check_achievements
from monster_rpg import progress
from monster_rpg.monsters.monster_data import ALL_MONSTERS


def _capture_n(player, n):
    for mid in list(ALL_MONSTERS)[:n]:
        player.monster_book.record_captured(mid)


class AchievementTests(unittest.TestCase):
    def test_collector_milestone_grants_reward(self):
        p = Player("A")
        _capture_n(p, 10)
        gold0 = p.gold
        newly = check_achievements(p)
        self.assertIn("collector_10", p.achievements)
        self.assertGreater(p.gold, gold0)
        self.assertTrue(newly)

    def test_idempotent_no_double_grant(self):
        p = Player("A")
        _capture_n(p, 10)
        check_achievements(p)
        gold_after = p.gold
        self.assertEqual(check_achievements(p), [])
        self.assertEqual(p.gold, gold_after)

    def test_event_flag_achievements(self):
        p = Player("A")
        p.story_flags.add("boss_defeated")
        p.story_flags.add("synthesized")
        check_achievements(p)
        self.assertIn("boss_slayer", p.achievements)
        self.assertIn("synthesizer", p.achievements)


class ProgressPersistenceTests(unittest.TestCase):
    def test_roundtrip(self):
        p = Player("A")
        p.achievements.update({"collector_10", "synthesizer"})
        p.story_flags.add("boss_defeated")
        p.quests_completed.add("q_first")
        p.arena_best = 3
        text = progress.to_json(p)

        p2 = Player("B")
        progress.apply_json(p2, text)
        self.assertEqual(p2.achievements, {"collector_10", "synthesizer"})
        self.assertEqual(p2.story_flags, {"boss_defeated"})
        self.assertEqual(p2.quests_completed, {"q_first"})
        self.assertEqual(p2.arena_best, 3)

    def test_apply_handles_empty(self):
        p = Player("A")
        progress.apply_json(p, None)
        self.assertEqual(p.achievements, set())
        self.assertEqual(p.arena_best, 0)


if __name__ == "__main__":
    unittest.main()
