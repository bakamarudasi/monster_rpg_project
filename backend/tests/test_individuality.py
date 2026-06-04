"""個体の個性（性格・個体値・才能）のテスト。

ポケモン個体値モデル:
- 性格＝派生4ステの±倍率（バランス型は無変化＝後方互換）
- 個体値＝ステ別0〜31の隠し数値。レベルアップ取得量（成長率）に効く
- 才能＝個体値から導出する総合評価ランク（鬼才＝実質5V・隠し）
- 鑑定で個体値の数値を開示
- 配合は個体値をステごとに親から継承（厳選ループ）
"""

import os
import unittest
from unittest.mock import patch

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.monsters import personality as P
from monster_rpg.player import Player
from monster_rpg import database_setup, save_manager

PMOD = "monster_rpg.monsters.personality"
MC_RANDOM = "monster_rpg.monsters.monster_class.random.random"
NO_AWAKEN = 0.99


def _wolf(ivs=None):
    m = ALL_MONSTERS["wolf"].copy()
    m.base_magic = 20
    if ivs is not None:
        m.ivs = dict(ivs)
    return m


class DefaultsAndPersonalityTests(unittest.TestCase):
    def test_defaults_are_neutral_and_compatible(self):
        m = _wolf()
        self.assertEqual(m.personality_id, P.DEFAULT_PERSONALITY_ID)
        self.assertEqual(m.ivs, {s: 0 for s in P.IV_STATS})
        self.assertFalse(m.iv_appraised)
        self.assertEqual(m.talent.id, "common")
        # バランス型＋0個体値はステ無変化（従来どおり）
        self.assertEqual(m.attack, m.base_attack)
        self.assertEqual(m.magic, m.base_magic)

    def test_personality_still_shapes_derived_stats(self):
        m = _wolf()
        base_atk, base_mag = m.base_attack, m.base_magic
        m.personality_id = "brave"  # 攻撃↑ 魔力↓
        self.assertEqual(m.attack, int(base_atk * 1.10))
        self.assertEqual(m.magic, int(base_mag * 0.90))

    def test_ivs_do_not_act_as_flat_multiplier(self):
        # 個体値は倍率ではなく成長率なので、レベルを上げない限りステは変わらない
        m = _wolf({s: 31 for s in P.IV_STATS})
        self.assertEqual(m.attack, m.base_attack)


class IVGrowthTests(unittest.TestCase):
    def test_perfect_ivs_grow_more_than_zero(self):
        perfect = _wolf({s: 31 for s in P.IV_STATS})
        zero = _wolf({s: 0 for s in P.IV_STATS})
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            perfect.advance_to_level(50)
            zero.advance_to_level(50)
        self.assertGreater(perfect.base_attack, zero.base_attack)
        self.assertGreater(perfect.base_speed, zero.base_speed)
        self.assertGreater(perfect.max_hp, zero.max_hp)

    def test_zero_iv_growth_is_unchanged_baseline(self):
        # 0個体値は従来のレベルアップ結果と完全一致（成長率に手を入れていないのと同じ）
        zero = ALL_MONSTERS["slime"].copy()
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            zero.advance_to_level(20)
        # もう一体、明示的に ivs を 0 にしても同じ
        zero2 = ALL_MONSTERS["slime"].copy()
        zero2.ivs = P.zero_ivs()
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            zero2.advance_to_level(20)
        self.assertEqual(zero.base_attack, zero2.base_attack)
        self.assertEqual(zero.max_hp, zero2.max_hp)

    def test_ivs_persist_through_evolution(self):
        m = ALL_MONSTERS["dragon_pup"].copy()
        ivs = {s: 20 for s in P.IV_STATS}
        m.ivs = dict(ivs)
        m.personality_id = "hasty"
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            m.advance_to_level(11)
        self.assertEqual(m.monster_id, "ashen_drake")  # 進化済み
        self.assertEqual(m.ivs, ivs)                    # 個体値は維持
        self.assertEqual(m.personality_id, "hasty")     # 性格も維持


class TalentDerivationTests(unittest.TestCase):
    def test_talent_thresholds(self):
        self.assertEqual(P.talent_from_ivs({s: 0 for s in P.IV_STATS}).id, "common")
        self.assertEqual(P.talent_from_ivs({s: 16 for s in P.IV_STATS}).id, "hardworking")
        self.assertEqual(P.talent_from_ivs({s: 22 for s in P.IV_STATS}).id, "prodigy")
        self.assertEqual(P.talent_from_ivs({s: 27 for s in P.IV_STATS}).id, "genius")
        self.assertEqual(P.talent_from_ivs({s: 31 for s in P.IV_STATS}).id, "mastermind")

    def test_mastermind_is_hidden_and_near_perfect(self):
        t = P.talent_from_ivs({s: 31 for s in P.IV_STATS})
        self.assertTrue(t.hidden)
        # 30 では届かない（鬼才＝ほぼ5V）
        self.assertEqual(P.talent_from_ivs({s: 30 for s in P.IV_STATS}).id, "genius")

    def test_judge_labels(self):
        self.assertEqual(P.iv_judge_label(31), "さいこう")
        self.assertEqual(P.iv_judge_label(30), "すばらしい")
        self.assertEqual(P.iv_judge_label(26), "すごくいい")
        self.assertEqual(P.iv_judge_label(16), "まあまあ")
        self.assertEqual(P.iv_judge_label(1), "ふつう")
        self.assertEqual(P.iv_judge_label(0), "苦手")


class RollAndAppraiseTests(unittest.TestCase):
    def test_roll_assigns_valid_ivs_and_personality(self):
        m = ALL_MONSTERS["slime"].copy()
        for _ in range(200):
            m.roll_individuality()
            self.assertIn(m.personality_id, P.ALL_PERSONALITIES)
            self.assertEqual(set(m.ivs.keys()), set(P.IV_STATS))
            for v in m.ivs.values():
                self.assertTrue(0 <= v <= P.IV_MAX)

    def test_summary_hides_ivs_until_appraised(self):
        m = _wolf({s: 31 for s in P.IV_STATS})
        s = m.individuality_summary()
        self.assertFalse(s["appraised"])
        self.assertNotIn("ivs", s)
        # 才能ランクと性格は未鑑定でも見える
        self.assertEqual(s["talent"]["name"], "鬼才")
        self.assertIn("personality", s)
        m.appraise()
        s2 = m.individuality_summary()
        self.assertTrue(s2["appraised"])
        self.assertEqual(s2["ivs"]["attack"]["value"], 31)
        self.assertEqual(s2["ivs"]["attack"]["label"], "さいこう")
        self.assertEqual(s2["iv_total"], 31 * len(P.IV_STATS))

    def test_copy_preserves_individuality(self):
        m = ALL_MONSTERS["slime"].copy()
        m.ivs = {s: 10 for s in P.IV_STATS}
        m.ivs["attack"] = 31
        m.personality_id = "hasty"
        m.iv_appraised = True
        m.trait_id = "fast_learner"
        c = m.copy()
        self.assertEqual(c.ivs, m.ivs)
        self.assertEqual(c.personality_id, "hasty")
        self.assertTrue(c.iv_appraised)
        self.assertEqual(c.trait_id, "fast_learner")


class IVInheritanceTests(unittest.TestCase):
    def test_inherits_three_stats_from_parents(self):
        p1 = {s: 31 for s in P.IV_STATS}
        p2 = {s: 0 for s in P.IV_STATS}
        with patch(PMOD + ".random.shuffle", lambda x: None), \
             patch(PMOD + ".random.choice", side_effect=lambda seq: seq[0]), \
             patch(PMOD + ".random_iv", return_value=-1):
            child = P.inherit_ivs(p1, p2, inherit_count=3)
        inherited = [s for s, v in child.items() if v == 31]   # 親1由来
        fresh = [s for s, v in child.items() if v == -1]        # 新規ロール
        self.assertEqual(len(inherited), 3)
        self.assertEqual(len(fresh), 2)

    def test_destiny_knot_inherits_five(self):
        p1 = {s: 31 for s in P.IV_STATS}
        p2 = {s: 0 for s in P.IV_STATS}
        with patch(PMOD + ".random.shuffle", lambda x: None), \
             patch(PMOD + ".random.choice", side_effect=lambda seq: seq[0]), \
             patch(PMOD + ".random_iv", return_value=-1):
            child = P.inherit_ivs(p1, p2, inherit_count=5)
        # 5継承＝全ステ親由来、新規ロールは無し
        self.assertTrue(all(v == 31 for v in child.values()))

    def test_power_item_forces_specific_stat_from_parent(self):
        p1 = {s: 31 for s in P.IV_STATS}
        p2 = {s: 7 for s in P.IV_STATS}
        child = P.inherit_ivs(p1, p2, inherit_count=3, power_stats={"attack": 2})
        self.assertEqual(child["attack"], 7)  # 親2から確定継承


class SynthesisAndWildTests(unittest.TestCase):
    def test_child_inherits_ivs_and_message(self):
        player = Player("Breeder")
        player.add_monster_to_party("slime")
        player.add_monster_to_party("wolf")
        player.party_monsters[0].ivs = {s: 31 for s in P.IV_STATS}
        player.party_monsters[1].ivs = {s: 31 for s in P.IV_STATS}
        ok, msg, child = player.synthesize_monster(0, 1)
        self.assertTrue(ok)
        self.assertEqual(set(child.ivs.keys()), set(P.IV_STATS))
        # 両親が完全individ値なら、継承された3ステは必ず31
        self.assertGreaterEqual(sum(1 for v in child.ivs.values() if v == 31), 3)
        self.assertIn("性格", msg)
        self.assertIn("才能", msg)

    def test_wild_rolls_ivs_but_boss_left_alone(self):
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


class PersistenceTests(unittest.TestCase):
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

    def test_ivs_appraisal_and_growth_round_trip(self):
        player = Player("Saver", user_id=self.user_id)
        player.add_monster_to_party("slime")
        m = player.party_monsters[0]
        # 進化（slime→water_wolf は ヒール が条件）を止め、再構築経路を一致させる
        m.skills = [s for s in m.skills if getattr(s, "name", "") != "ヒール"]
        m.ivs = {s: 31 for s in P.IV_STATS}
        m.personality_id = "stubborn"
        m.iv_appraised = True
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            m.advance_to_level(30)
        self.assertEqual(m.monster_id, "slime")  # 進化していないこと
        saved_attack, saved_hp = m.base_attack, m.max_hp
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        lm = loaded.party_monsters[0]
        self.assertEqual(lm.ivs, {s: 31 for s in P.IV_STATS})
        self.assertEqual(lm.personality_id, "stubborn")
        self.assertTrue(lm.iv_appraised)
        self.assertEqual(lm.talent.id, "mastermind")
        # 個体値由来の成長が再構築される（再レベルアップで base/HP が一致）
        self.assertEqual(lm.base_attack, saved_attack)
        self.assertEqual(lm.max_hp, saved_hp)
        # 0個体値の同種より明確に強い（＝個体値が効いている）
        weak = ALL_MONSTERS["slime"].copy()
        weak.skills = [s for s in weak.skills if getattr(s, "name", "") != "ヒール"]
        with patch(MC_RANDOM, return_value=NO_AWAKEN):
            weak.advance_to_level(30)
        self.assertGreater(lm.base_attack, weak.base_attack)
        self.assertGreater(lm.max_hp, weak.max_hp)


class BreedingItemTests(unittest.TestCase):
    def test_everstone_forces_parent_nature(self):
        # 変異が起きるロール(0.0)でも、かわらずのいし指定があれば親の性格で確定
        with patch(PMOD + ".random.random", return_value=0.0):
            self.assertEqual(P.inherit_personality_id("brave", "clever", everstone_parent=1), "brave")
            self.assertEqual(P.inherit_personality_id("brave", "clever", everstone_parent=2), "clever")

    def test_parse_breeding_respects_ownership(self):
        from monster_rpg.services import synthesis_service as ss
        from monster_rpg.items.item_data import ALL_ITEMS
        player = Player("B")
        player.items.append(ALL_ITEMS["destiny_knot"])
        player.items.append(ALL_ITEMS["power_bracer"])
        data = {"breeding": {"destiny_knot": True, "everstone_parent": 1,
                             "power": {"power_bracer": 2, "power_anklet": 1}}}
        b = ss._parse_breeding(player, data)
        self.assertEqual(b.get("inherit_count"), P.DESTINY_KNOT_INHERIT_COUNT)
        self.assertEqual(b.get("power_stats"), {"attack": 2})   # bracer所持/anklet未所持
        self.assertNotIn("everstone_parent", b)                 # かわらずのいし未所持

    def test_destiny_knot_breeding_inherits_all_from_perfect_parents(self):
        player = Player("B")
        player.add_monster_to_party("slime")
        player.add_monster_to_party("wolf")
        player.party_monsters[0].ivs = {s: 31 for s in P.IV_STATS}
        player.party_monsters[1].ivs = {s: 31 for s in P.IV_STATS}
        ok, _msg, child = player.synthesize_monster(0, 1, breeding={"inherit_count": 5})
        self.assertTrue(ok)
        # 両親5V＋5継承なら全ステ親由来＝全て31
        self.assertTrue(all(v == 31 for v in child.ivs.values()))
        self.assertEqual(child.talent.id, "mastermind")

    def test_power_item_breeding_forces_stat(self):
        player = Player("B")
        player.add_monster_to_party("slime")
        player.add_monster_to_party("wolf")
        player.party_monsters[0].ivs = {s: 0 for s in P.IV_STATS}
        player.party_monsters[1].ivs = {s: 0 for s in P.IV_STATS}
        player.party_monsters[1].ivs["attack"] = 31  # 触媒(親2)の攻撃だけ31
        ok, _msg, child = player.synthesize_monster(
            0, 1, breeding={"power_stats": {"attack": 2}}
        )
        self.assertTrue(ok)
        self.assertEqual(child.ivs["attack"], 31)  # 確定継承


class AppraiseRouteTests(unittest.TestCase):
    def setUp(self):
        from monster_rpg.web_main import app
        self.db_path = "test_appraise.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user("ap", "pw")
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        player = Player("Ap", user_id=self.user_id)
        player.add_monster_to_party("slime")
        player.party_monsters[0].ivs = {s: 31 for s in P.IV_STATS}
        player.gold = 100
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_appraise_costs_gold_and_reveals_ivs(self):
        resp = self.client.post(f"/appraise/{self.user_id}", json={"monster_idx": 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["gold"], 50)  # 100 - 50
        self.assertTrue(data["individuality"]["appraised"])
        self.assertEqual(data["individuality"]["ivs"]["attack"]["value"], 31)
        # 永続化されている
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertTrue(loaded.party_monsters[0].iv_appraised)

    def test_appraise_insufficient_gold(self):
        player = save_manager.load_game(self.db_path, user_id=self.user_id)
        player.gold = 10
        save_manager.save_game(player, self.db_path, user_id=self.user_id)
        resp = self.client.post(f"/appraise/{self.user_id}", json={"monster_idx": 0})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.get_json()["success"])

    def test_appraise_already_done_is_free(self):
        self.client.post(f"/appraise/{self.user_id}", json={"monster_idx": 0})
        resp = self.client.post(f"/appraise/{self.user_id}", json={"monster_idx": 0})
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data.get("already"))
        self.assertEqual(data["gold"], 50)  # 二重課金されない


if __name__ == "__main__":
    unittest.main()
