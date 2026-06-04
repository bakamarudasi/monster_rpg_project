"""個体の個性（性格・才能）のテスト。

- 性格＝ステ傾向（攻撃/防御/素早さ/魔力の倍率）
- 才能＝素質ランク（全ステ倍率、最上位「鬼才」は隠し才能）
- 既定（バランス型＋凡才）はステ無変化＝既存挙動と後方互換
- 配合での継承（良個体ほど高才能が出やすい）と保存/読み込み
"""

import os
import unittest
from unittest.mock import patch

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.monsters import personality as P
from monster_rpg.player import Player
from monster_rpg import database_setup, save_manager

RANDOM_PATH = "monster_rpg.monsters.personality.random"


def _wolf():
    m = ALL_MONSTERS["wolf"].copy()
    m.base_magic = 20  # 魔力系の性格を検証できるよう下駄をはかせる
    return m


class PersonalityStatTests(unittest.TestCase):
    def test_default_is_neutral(self):
        """バランス型＋凡才では倍率1.0＝従来どおりのステータス。"""
        m = _wolf()
        self.assertEqual(m.personality_id, P.DEFAULT_PERSONALITY_ID)
        self.assertEqual(m.talent_id, P.DEFAULT_TALENT_ID)
        self.assertEqual(m.attack, m.base_attack)
        self.assertEqual(m.defense, m.base_defense)
        self.assertEqual(m.speed, m.base_speed)
        self.assertEqual(m.magic, m.base_magic)

    def test_personality_raises_and_lowers(self):
        """ちからじまん＝攻撃↑/魔力↓。基準は素のステ。"""
        m = _wolf()
        base_atk, base_mag = m.base_attack, m.base_magic
        m.personality_id = "brave"
        self.assertEqual(m.attack, int(base_atk * 1.10))
        self.assertEqual(m.magic, int(base_mag * 0.90))
        # 触れない防御・素早さは変化しない
        self.assertEqual(m.defense, m.base_defense)
        self.assertEqual(m.speed, m.base_speed)

    def test_talent_multiplies_all_stats(self):
        """天才は派生4ステすべてに同じ倍率を乗せる。"""
        m = _wolf()
        m.talent_id = "genius"  # x1.10
        self.assertEqual(m.attack, int(m.base_attack * 1.10))
        self.assertEqual(m.defense, int(m.base_defense * 1.10))
        self.assertEqual(m.speed, int(m.base_speed * 1.10))
        self.assertEqual(m.magic, int(m.base_magic * 1.10))

    def test_personality_and_talent_stack(self):
        """性格と才能は掛け算で重なる。"""
        m = _wolf()
        m.personality_id = "brave"   # attack +10%
        m.talent_id = "prodigy"      # x1.06
        self.assertEqual(m.attack, int(m.base_attack * 1.06 * 1.10))
        self.assertEqual(m.magic, int(m.base_magic * 1.06 * 0.90))

    def test_unknown_ids_fall_back_to_defaults(self):
        m = _wolf()
        m.personality_id = "???"
        m.talent_id = "???"
        self.assertEqual(m.personality.id, P.DEFAULT_PERSONALITY_ID)
        self.assertEqual(m.talent.id, P.DEFAULT_TALENT_ID)
        self.assertEqual(m.attack, m.base_attack)


class IndividualityHelpersTests(unittest.TestCase):
    def test_roll_assigns_valid_ids_and_never_hidden(self):
        m = ALL_MONSTERS["slime"].copy()
        for _ in range(200):
            m.roll_individuality()
            self.assertIn(m.personality_id, P.ALL_PERSONALITIES)
            self.assertIn(m.talent_id, P.ALL_TALENTS)
            # 隠し才能（鬼才）は野生抽選では出ない
            self.assertFalse(P.get_talent(m.talent_id).hidden)

    def test_copy_preserves_individuality(self):
        m = ALL_MONSTERS["slime"].copy()
        m.personality_id = "hasty"
        m.talent_id = "genius"
        c = m.copy()
        self.assertEqual(c.personality_id, "hasty")
        self.assertEqual(c.talent_id, "genius")

    def test_summary_shape(self):
        m = ALL_MONSTERS["slime"].copy()
        m.personality_id = "brave"
        m.talent_id = "genius"
        s = m.individuality_summary()
        self.assertEqual(s["personality"]["name"], "ちからじまん")
        self.assertIn("攻撃↑", s["personality"]["effect"])
        self.assertEqual(s["talent"]["name"], "天才")
        self.assertEqual(s["talent"]["bonus_percent"], 10)
        self.assertFalse(s["talent"]["hidden"])

    def test_random_talent_weighted_excludes_hidden(self):
        ids = {P.random_talent_id() for _ in range(500)}
        self.assertNotIn("mastermind", ids)
        self.assertIn("common", ids)


class InheritanceTests(unittest.TestCase):
    def test_personality_inherits_from_a_parent(self):
        # 変異なし（random>=0.10）→ どちらかの親の性格
        with patch(RANDOM_PATH + ".random", return_value=0.99), \
             patch(RANDOM_PATH + ".choice", side_effect=lambda seq: seq[0]):
            self.assertEqual(P.inherit_personality_id("brave", "clever"), "brave")

    def test_personality_mutates(self):
        # 変異あり（random<0.10）→ 親と無関係に全性格から一様抽選
        with patch(RANDOM_PATH + ".random", return_value=0.0), \
             patch(RANDOM_PATH + ".choice", side_effect=lambda seq: seq[-1]):
            result = P.inherit_personality_id("brave", "brave")
            self.assertEqual(result, list(P.ALL_PERSONALITIES.keys())[-1])

    def test_talent_keeps_better_parent(self):
        with patch(RANDOM_PATH + ".random", return_value=0.99):
            self.assertEqual(P.inherit_talent_id("common", "genius"), "genius")
            self.assertEqual(P.inherit_talent_id("prodigy", "hardworking"), "prodigy")

    def test_talent_can_upgrade_one_tier(self):
        with patch(RANDOM_PATH + ".random", return_value=0.0):
            # 秀才×秀才 → 1段昇格して天才
            self.assertEqual(P.inherit_talent_id("prodigy", "prodigy"), "genius")

    def test_non_genius_pair_never_reaches_hidden(self):
        # 天才を1体しか含まない配合は、どのロールでも隠し才能（鬼才）にならない
        for roll in (0.0, 0.14, 0.2, 0.5, 0.99):
            with patch(RANDOM_PATH + ".random", return_value=roll):
                result = P.inherit_talent_id("genius", "common")
                self.assertNotEqual(result, "mastermind")
                self.assertFalse(P.get_talent(result).hidden)

    def test_mastermind_only_from_genius_pair(self):
        with patch(RANDOM_PATH + ".random", return_value=0.0):
            self.assertEqual(P.inherit_talent_id("genius", "genius"), "mastermind")
        # 天才同士でも当たらなければ天才のまま
        with patch(RANDOM_PATH + ".random", return_value=0.99):
            self.assertEqual(P.inherit_talent_id("genius", "genius"), "genius")


class SynthesisIndividualityTests(unittest.TestCase):
    def test_child_gets_individuality_and_message(self):
        player = Player("Breeder")
        player.add_monster_to_party("slime")
        player.add_monster_to_party("wolf")
        player.party_monsters[0].level = 5
        player.party_monsters[1].level = 5
        # 親の個性を固定し、変異なしで継承されることを確認
        player.party_monsters[0].personality_id = "hasty"
        player.party_monsters[0].talent_id = "prodigy"
        player.party_monsters[1].personality_id = "hasty"
        player.party_monsters[1].talent_id = "prodigy"

        with patch(RANDOM_PATH + ".random", return_value=0.99), \
             patch(RANDOM_PATH + ".choice", side_effect=lambda seq: seq[0]):
            ok, msg, child = player.synthesize_monster(0, 1)

        self.assertTrue(ok)
        self.assertIn(child.personality_id, P.ALL_PERSONALITIES)
        self.assertEqual(child.talent_id, "prodigy")  # 秀才×秀才・昇格なし→秀才
        self.assertIn("性格", msg)
        self.assertIn("才能", msg)


class WildIndividualityTests(unittest.TestCase):
    def test_wild_rolls_but_boss_is_left_alone(self):
        from monster_rpg.exploration import _roll_wild_individuality
        normal = ALL_MONSTERS["slime"].copy()
        with patch.object(Monster, "roll_individuality") as roll:
            _roll_wild_individuality(normal)
            roll.assert_called_once()

        boss = ALL_MONSTERS["slime"].copy()
        boss.is_boss = True
        with patch.object(Monster, "roll_individuality") as roll:
            _roll_wild_individuality(boss)
            roll.assert_not_called()

    def test_generate_enemy_party_assigns_valid_individuality(self):
        from monster_rpg.exploration import generate_enemy_party
        from monster_rpg.map_data import Location
        loc = Location(
            location_id="t", name="t", description="",
            enemy_pool={"slime": 50, "goblin": 50}, party_size=[1, 2],
            encounter_rate=1.0,
        )
        party = generate_enemy_party(loc)
        self.assertTrue(party)
        for m in party:
            self.assertIn(m.personality_id, P.ALL_PERSONALITIES)
            self.assertIn(m.talent_id, P.ALL_TALENTS)


class IndividualityPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_individuality.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user("indiv", "pw")

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_personality_and_talent_round_trip(self):
        player = Player("Saver", user_id=self.user_id)
        player.add_monster_to_party("slime")
        player.party_monsters[0].personality_id = "stubborn"
        player.party_monsters[0].talent_id = "mastermind"  # 隠し才能も保存される
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        lm = loaded.party_monsters[0]
        self.assertEqual(lm.personality_id, "stubborn")
        self.assertEqual(lm.talent_id, "mastermind")
        self.assertTrue(lm.talent.hidden)


if __name__ == "__main__":
    unittest.main()
