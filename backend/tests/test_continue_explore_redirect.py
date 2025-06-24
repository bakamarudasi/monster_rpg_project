import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg import save_manager

class ContinueExploreRedirectTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_continue.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_continue_explore_redirect(self):
        resp = self.client.post(f'/battle/{self.user_id}', data={'continue_explore': '1'})
        self.assertEqual(resp.status_code, 307)
        self.assertTrue(resp.headers['Location'].endswith(f'/explore/{self.user_id}'))

if __name__ == '__main__':
    unittest.main()
