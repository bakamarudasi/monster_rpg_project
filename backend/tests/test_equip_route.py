import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.items.equipment import ALL_EQUIPMENT

class EquipRouteTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_equip.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        player.add_monster_to_party('slime')
        player.equipment_inventory.append(ALL_EQUIPMENT['bronze_sword'])
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_equip_to_monster(self):
        resp = self.client.post(f'/equip/{self.user_id}', json={'equip_id': 'bronze_sword', 'monster_idx': 0})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual(len(loaded.equipment_inventory), 0)
        self.assertIn('weapon', data['monster_equipment'])
        self.assertEqual(data['monster_equipment']['weapon'], ALL_EQUIPMENT['bronze_sword'].name)

if __name__ == '__main__':
    unittest.main()
