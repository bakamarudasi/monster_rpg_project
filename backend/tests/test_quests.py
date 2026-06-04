"""依頼（クエスト）システムのテスト。"""

import unittest

from monster_rpg.player import Player
from monster_rpg import quests
from monster_rpg.monsters.monster_data import ALL_MONSTERS

FIRST = list(ALL_MONSTERS)[0]


class QuestTests(unittest.TestCase):
    def test_accept_then_claim_capture_count(self):
        p = Player("A")
        ok, _ = quests.accept_quest(p, "q_first_friend")
        self.assertTrue(ok)
        self.assertIn("q_first_friend", p.quests_active)
        # 条件未達では受け取れない
        ok, _ = quests.claim_quest(p, "q_first_friend")
        self.assertFalse(ok)
        # 1体捕獲 → 受け取り可能
        p.monster_book.record_captured(FIRST)
        gold0 = p.gold
        ok, _ = quests.claim_quest(p, "q_first_friend")
        self.assertTrue(ok)
        self.assertIn("q_first_friend", p.quests_completed)
        self.assertNotIn("q_first_friend", p.quests_active)
        self.assertGreater(p.gold, gold0)

    def test_cannot_claim_unaccepted(self):
        p = Player("A")
        p.monster_book.record_captured(FIRST)
        ok, _ = quests.claim_quest(p, "q_first_friend")
        self.assertFalse(ok)

    def test_defeat_quest_condition(self):
        p = Player("A")
        q = quests.QUEST_BY_ID["q_slay_match_ember"]
        self.assertFalse(quests.is_complete(p, q))
        p.story_flags.add("defeated:match_ember")
        self.assertTrue(quests.is_complete(p, q))

    def test_view_status_transitions(self):
        p = Player("A")
        self.assertTrue(all(r["status"] == "available" for r in quests.quest_view(p)))
        quests.accept_quest(p, "q_first_friend")
        self.assertEqual(
            {r["id"]: r["status"] for r in quests.quest_view(p)}["q_first_friend"], "active")
        p.monster_book.record_captured(FIRST)
        self.assertEqual(
            {r["id"]: r["status"] for r in quests.quest_view(p)}["q_first_friend"], "ready")

    def test_battle_win_sets_defeat_flag(self):
        from monster_rpg.services.battle_service import apply_battle_rewards
        p = Player("A")
        p.add_monster_to_party("slime")
        boss = ALL_MONSTERS["match_ember"].copy()
        apply_battle_rewards(p, "win", p.party_monsters, [boss], [])
        self.assertIn("defeated:match_ember", p.story_flags)
        self.assertIn("boss_defeated", p.story_flags)


if __name__ == "__main__":
    unittest.main()
