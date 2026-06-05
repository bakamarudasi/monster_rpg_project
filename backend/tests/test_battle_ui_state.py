"""バトルUI向けの状態（バリア量・フィールド残量）がレスポンスに乗るかのテスト。"""

import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app, Battle, active_battles
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster
from monster_rpg import elements
from monster_rpg.web.battle import _restore_field


class BattleUIStateTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_ui.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('uitester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        self.hero = Monster('Hero', hp=40, attack=8, defense=3)
        player.party_monsters.append(self.hero)
        enemy = Monster('Slime', hp=30, attack=3, defense=1)
        self.battle = Battle(player.party_monsters, [enemy], player)
        active_battles[self.user_id] = self.battle
        elements.clear_field()

    def tearDown(self):
        active_battles.pop(self.user_id, None)
        elements.clear_field()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_battle_json_exposes_shield_and_field(self):
        self.hero.shield = 35
        elements.set_field('火', 1.5, 3, '業火の地')
        resp = self.client.get(f'/battle-json/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        hp = resp.get_json()['hp_values']
        self.assertEqual(hp['player'][0]['shield'], 35)
        self.assertIsNotNone(hp['field'])
        self.assertEqual(hp['field']['element'], '火')
        self.assertEqual(hp['field']['remaining'], 3)

    def test_battle_json_exposes_individuality(self):
        from monster_rpg.monsters.personality import IV_STATS
        self.hero.personality_id = 'clever'           # かしこい
        self.hero.ivs = {s: 31 for s in IV_STATS}      # 才能ランクが common 以外になる
        # ターンを進めて手番（turn_order）を確定させる
        for _ in range(100):
            if self.battle.turn_order:
                break
            self.battle.advance_turn()
        resp = self.client.get(f'/battle-json/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        units = resp.get_json()['hp_values']['turn_order_monsters']
        hero = next(u for u in units if u['name'] == 'Hero')
        self.assertEqual(hero['personality']['name'], 'かしこい')
        self.assertIn('effect', hero['personality'])
        self.assertNotEqual(hero['talent']['id'], 'common')
        self.assertIn('trait', hero)

    def test_battle_json_exposes_combat_stats(self):
        for _ in range(100):
            if self.battle.turn_order:
                break
            self.battle.advance_turn()
        units = self.client.get(f'/battle-json/{self.user_id}').get_json()['hp_values']['turn_order_monsters']
        hero = next(u for u in units if u['name'] == 'Hero')
        for key in ('magic', 'magic_defense', 'critical_rate', 'evasion_rate'):
            self.assertIn(key, hero)

    def test_restore_field_round_trip(self):
        elements.set_field('氷', 1.5, 4, 'ブリザード')
        saved = {'field': elements.get_field()}
        elements.clear_field()
        self.assertIsNone(elements.get_field())
        _restore_field(saved)
        restored = elements.get_field()
        self.assertEqual(restored['element'], '氷')
        self.assertEqual(restored['remaining'], 4)

    def test_restore_field_clears_when_absent(self):
        elements.set_field('火', 1.5, 2, 'x')
        _restore_field({})  # 'field' キー無し → クリアされる
        self.assertIsNone(elements.get_field())


if __name__ == '__main__':
    unittest.main()
