import unittest

import os

from monster_rpg.player import Player
from monster_rpg import save_manager
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

    def test_item_item_fusion(self):
        player = Player('Tester')
        player.items.append(ALL_ITEMS['magic_stone'])
        player.items.append(ALL_ITEMS['dragon_scale'])
        success, msg, result = player.synthesize_items('magic_stone', 'dragon_scale')
        self.assertTrue(success)
        from monster_rpg.items.equipment import EquipmentInstance
        self.assertIsInstance(result, EquipmentInstance)
        self.assertEqual(len(player.items), 0)
        self.assertEqual(len(player.equipment_inventory), 1)


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
        player.items.append(ALL_ITEMS['magic_stone'])
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_endpoint_creates_monster_and_updates_book(self):
        resp = self.client.post(
            f'/synthesize_action/{self.user_id}',
            json={
                'base_type': 'monster',
                'base_id': 0,
                'material_type': 'item',
                'material_id': 'dragon_scale',
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['name'], ALL_MONSTERS['dragon_pup'].name)

    def test_item_item_endpoint(self):
        resp = self.client.post(
            f'/synthesize_action/{self.user_id}',
            json={
                'base_type': 'item',
                'base_id': 'magic_stone',
                'material_type': 'item',
                'material_id': 'dragon_scale',
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        from monster_rpg.items.equipment import ALL_EQUIPMENT
        self.assertTrue(data['name'].endswith(ALL_EQUIPMENT['bronze_sword'].name))

        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual(len(loaded.equipment_inventory), 1)

if __name__ == '__main__':
    unittest.main()
