import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app, Battle, active_battles
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster

class BattleViewJsonTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_web.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        hero = Monster('Hero', hp=20, attack=5, defense=2)
        player.party_monsters.append(hero)
        enemy = Monster('Slime', hp=10, attack=3, defense=1)
        battle_obj = Battle(player.party_monsters, [enemy], player)
        active_battles[self.user_id] = battle_obj

    def tearDown(self):
        active_battles.pop(self.user_id, None)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_post_returns_json(self):
        resp = self.client.post(f'/battle/{self.user_id}', data={'action': 'attack', 'target_enemy': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('hp_values', data)
        self.assertIn('status_effects', data['hp_values']['player'][0])
        self.assertIn('status_effects', data['hp_values']['enemy'][0])
        self.assertIn('log', data)
        self.assertIn('finished', data)

    def test_post_accepts_json_payload(self):
        resp = self.client.post(
            f'/battle/{self.user_id}',
            json={'action': 'attack', 'target_enemy': 0}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('hp_values', data)
        self.assertIn('status_effects', data['hp_values']['enemy'][0])
        self.assertIn('status_effects', data['hp_values']['player'][0])
        self.assertIn('log', data)
        self.assertIn('finished', data)

if __name__ == '__main__':
    unittest.main()
