import os
import unittest

from monster_rpg import database_setup
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.web_main import app

class PartyFormationTests(unittest.TestCase):
    def setUp(self):
        self.player = Player('Tester')
        for mid in ('slime', 'goblin', 'wolf'):
            if mid in ALL_MONSTERS:
                self.player.add_monster_to_party(mid)

    def test_move_monster(self):
        ids_before = [m.monster_id for m in self.player.party_monsters]
        self.assertEqual(ids_before, ['slime', 'goblin', 'wolf'])
        self.player.move_monster(0, 2)
        ids_after = [m.monster_id for m in self.player.party_monsters]
        self.assertEqual(ids_after, ['goblin', 'wolf', 'slime'])

class FormationRouteTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_formation.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        for mid in ('slime', 'goblin', 'wolf'):
            if mid in ALL_MONSTERS:
                player.add_monster_to_party(mid)
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_post_reorders_party(self):
        resp = self.client.post(
            f'/formation/{self.user_id}',
            data={'order': '[1,2,0]', 'reserve': '[]'}
        )
        self.assertEqual(resp.status_code, 200)
        player = save_manager.load_game(self.db_path, user_id=self.user_id)
        ids = [m.monster_id for m in player.party_monsters]
        self.assertEqual(ids, ['goblin', 'wolf', 'slime'])

    def test_reset_formation(self):
        resp = self.client.post(f'/formation/{self.user_id}', data={'reset': '1'})
        self.assertEqual(resp.status_code, 200)
        player = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual([m.monster_id for m in player.party_monsters], ['slime'])
        self.assertEqual(
            [m.monster_id for m in player.reserve_monsters],
            ['wolf', 'goblin']
        )

if __name__ == '__main__':
    unittest.main()
