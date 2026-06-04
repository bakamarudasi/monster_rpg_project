"""ボス演出（is_boss フラグ・登場演出）のテスト。"""

import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.battle import start_atb_battle


class BossFlagTests(unittest.TestCase):
    def test_sequence_and_demon_lords_are_bosses(self):
        for mid in ["fallen_deity", "match_ember", "tale_devourer",
                    "storm_sovereign", "thunder_emperor"]:
            self.assertTrue(ALL_MONSTERS[mid].is_boss, mid)

    def test_regular_monsters_are_not_bosses(self):
        for mid in ["slime", "goblin", "wolf", "cinder_kit", "gust_wisp", "vampire_lord"]:
            self.assertFalse(ALL_MONSTERS[mid].is_boss, mid)

    def test_is_boss_survives_copy(self):
        self.assertTrue(ALL_MONSTERS["fallen_deity"].copy().is_boss)
        self.assertFalse(ALL_MONSTERS["slime"].copy().is_boss)

    def test_at_least_a_dozen_bosses(self):
        bosses = [m for m in ALL_MONSTERS.values() if m.is_boss]
        self.assertGreaterEqual(len(bosses), 12)


class BossIntroTests(unittest.TestCase):
    def test_boss_intro_logged_when_boss_present(self):
        # 敵生成をボス1体に差し替え、start_new_battle が登場演出ログ(type=boss)を出すか
        from monster_rpg.services import battle_service as bs
        from monster_rpg.map_data import load_locations
        load_locations()
        player = Player("勇者")
        player.add_monster_to_party("slime")
        player.current_location_id = "field_near_village"
        boss = ALL_MONSTERS["storm_sovereign"].copy()
        orig = bs.generate_enemy_party
        bs.generate_enemy_party = lambda loc, p=None: [boss]
        try:
            battle, err = bs.start_new_battle(player)
        finally:
            bs.generate_enemy_party = orig
        self.assertIsNotNone(battle)
        self.assertTrue(any(e.get("type") == "boss" for e in battle.log),
                        "ボス登場演出ログが出ていない")


if __name__ == "__main__":
    unittest.main()
