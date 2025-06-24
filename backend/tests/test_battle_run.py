import os
import unittest
from unittest.mock import patch

from monster_rpg import database_setup
from monster_rpg.web_main import app, Battle, active_battles
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster

class BattleRunTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_run.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
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

    def test_run_success_message(self):
        with patch('random.random', return_value=0.0):
            resp = self.client.post(f'/battle/{self.user_id}', json={'action': 'run'})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['finished'])
        messages = [e['message'] for e in data['log']]
        self.assertIn('うまく逃げ切れた！', messages)
        self.assertNotIn(self.user_id, active_battles)

if __name__ == '__main__':
    unittest.main()
