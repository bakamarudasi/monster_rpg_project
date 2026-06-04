"""闘技場（アリーナ）のテスト。"""

import random
import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg import arena


def _strong_party(player):
    # 圧倒的に強い編成（段位下位は確実に勝てる）
    for mid in ["vampire_lord", "fallen_deity", "obsidian_titan"]:
        m = ALL_MONSTERS[mid].copy()
        m.advance_to_level(60)
        player.party_monsters.append(m)


class ArenaGatingTests(unittest.TestCase):
    def test_can_challenge_only_next_tier(self):
        p = Player("A")
        self.assertTrue(arena.can_challenge(p, 0))
        self.assertFalse(arena.can_challenge(p, 1))
        p.arena_best = 2
        self.assertTrue(arena.can_challenge(p, 2))
        self.assertFalse(arena.can_challenge(p, 3))

    def test_locked_tier_rejected(self):
        p = Player("A")
        _strong_party(p)
        win, msg, _ = arena.run_arena_tier(p, 3)
        self.assertFalse(win)

    def test_empty_party_rejected(self):
        p = Player("A")
        win, _, _ = arena.run_arena_tier(p, 0)
        self.assertFalse(win)


class ArenaProgressTests(unittest.TestCase):
    def test_clear_advances_and_grants_reward(self):
        random.seed(2)
        p = Player("A")
        _strong_party(p)
        gold0 = p.gold
        win, _, rew = arena.run_arena_tier(p, 0)
        self.assertTrue(win)
        self.assertEqual(p.arena_best, 1)
        self.assertGreater(p.gold, gold0)
        self.assertTrue(rew)

    def test_replay_gives_no_extra_gold(self):
        random.seed(2)
        p = Player("A")
        _strong_party(p)
        arena.run_arena_tier(p, 0)
        gold_after = p.gold
        win, _, rew = arena.run_arena_tier(p, 0)
        self.assertTrue(win)
        self.assertEqual(rew, [])
        self.assertEqual(p.gold, gold_after)

    def test_view_statuses(self):
        p = Player("A")
        p.arena_best = 1
        statuses = {r["name"]: r["status"] for r in arena.arena_view(p)}
        names = [r["name"] for r in arena.arena_view(p)]
        self.assertEqual(statuses[names[0]], "cleared")
        self.assertEqual(statuses[names[1]], "open")
        self.assertEqual(statuses[names[2]], "locked")

    def test_champion_achievement(self):
        from monster_rpg.achievements import check_achievements
        p = Player("A")
        p.arena_best = 5
        check_achievements(p)
        self.assertIn("arena_champion", p.achievements)


if __name__ == "__main__":
    unittest.main()
