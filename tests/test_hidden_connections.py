import os
import unittest
from unittest.mock import patch

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg.map_data import LOCATIONS

class HiddenConnectionsTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_hidden.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        player.current_location_id = 'deep_forest'
        player.increase_exploration('deep_forest', 90)
        player.save_game(self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_connections_unlocked_at_100(self):
        loc = LOCATIONS['deep_forest']
        self.assertNotIn('さらに奥へ', loc.connections)
        with patch('monster_rpg.web_main.random.randint', return_value=20), \
             patch('monster_rpg.web_main.random.random', return_value=1.0):
            self.client.post(f'/explore/{self.user_id}')
        self.assertIn('さらに奥へ', loc.connections)

if __name__ == '__main__':
    unittest.main()
