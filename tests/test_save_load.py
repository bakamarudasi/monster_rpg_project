import os
import unittest

import database_setup
from player import Player
from monsters.monster_data import ALL_MONSTERS
from items.item_data import ALL_ITEMS

class SaveLoadTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_game.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_load_party_and_items(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.add_monster_to_party('goblin')
        player.items.append(ALL_ITEMS['small_potion'])

        player.save_game(self.db_path)
        loaded = Player.load_game(self.db_path)

        self.assertIsNotNone(loaded)
        monster_ids = sorted(m.monster_id for m in loaded.party_monsters)
        self.assertEqual(monster_ids, ['goblin', 'slime'])
        self.assertEqual(len(loaded.items), 1)
        self.assertEqual(loaded.items[0].item_id, 'small_potion')

if __name__ == '__main__':
    unittest.main()
