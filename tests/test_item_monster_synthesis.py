import unittest

import os

from monster_rpg.player import Player
from monster_rpg.items.item_data import ALL_ITEMS
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg import database_setup
from monster_rpg.web_main import app

class ItemMonsterSynthesisTests(unittest.TestCase):
    def test_monster_item_fusion(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.items.append(ALL_ITEMS['dragon_scale'])

        success, msg, child = player.synthesize_monster_with_item(0, 'dragon_scale')
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.monster_id, 'dragon_pup')
        self.assertEqual(len(player.items), 0)
        self.assertEqual(player.party_monsters[0].monster_id, 'dragon_pup')


class ItemMonsterSynthesisRouteTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_item_fusion.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        player.add_monster_to_party('slime')
        player.items.append(ALL_ITEMS['dragon_scale'])
        player.save_game(self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_endpoint_creates_monster_and_updates_book(self):
        resp = self.client.post(
            f'/synthesize_action/{self.user_id}',
            json={
                'base_monster_index': 0,
                'material_type': 'item',
                'material_id': 'dragon_scale',
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['new_monster_name'], ALL_MONSTERS['dragon_pup'].name)

        loaded = Player.load_game(self.db_path, user_id=self.user_id)
        self.assertIn('dragon_pup', loaded.monster_book.captured)

if __name__ == '__main__':
    unittest.main()
