"""ものがたり（コーデックス）の解禁ロジックのテスト。"""

import unittest

from monster_rpg.player import Player
from monster_rpg import story


def _by_title(player):
    return {e["title"]: e["unlocked"] for e in story.codex_entries(player)}


class StoryCodexTests(unittest.TestCase):
    def test_prologue_always_unlocked(self):
        p = Player("A")
        self.assertTrue(story.codex_entries(p)[0]["unlocked"])

    def test_area_lore_unlocks_on_visit(self):
        p = Player("A")
        self.assertFalse(_by_title(p)["物語の墓標"])
        p.exploration_progress["graveyard_of_tales"] = 40
        self.assertTrue(_by_title(p)["物語の墓標"])

    def test_boss_lore_unlocks_on_defeat(self):
        p = Player("A")
        self.assertFalse(_by_title(p)["白雪の毒后"])
        p.story_flags.add("defeated:poison_queen")
        self.assertTrue(_by_title(p)["白雪の毒后"])

    def test_unlocked_count_grows(self):
        p = Player("A")
        u0, total = story.unlocked_count(p)
        p.story_flags.add("defeated:tale_devourer")
        u1, _ = story.unlocked_count(p)
        self.assertGreater(u1, u0)
        self.assertGreaterEqual(total, u1)


if __name__ == "__main__":
    unittest.main()
