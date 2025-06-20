import os
import unittest

from monster_rpg import database_setup
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.items.item_data import ALL_ITEMS
from monster_rpg.items.equipment import ALL_EQUIPMENT

class SaveLoadTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_game.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user1 = database_setup.create_user('alice', 'pw1')
        self.user2 = database_setup.create_user('bob', 'pw2')

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_load_party_and_items(self):
        player = Player('Tester', user_id=self.user1)
        player.add_monster_to_party('slime')
        player.add_monster_to_party('goblin')
        player.items.append(ALL_ITEMS['small_potion'])

        save_manager.save_game(player, self.db_path)
        loaded = save_manager.load_game(self.db_path, user_id=self.user1)

        self.assertIsNotNone(loaded)
        monster_ids = sorted(m.monster_id for m in loaded.party_monsters)
        self.assertEqual(monster_ids, ['goblin', 'slime'])
        self.assertEqual(len(loaded.items), 1)
        self.assertEqual(loaded.items[0].item_id, 'small_potion')

    def test_multiple_users_separate_saves(self):
        p1 = Player('A', user_id=self.user1)
        p1.add_monster_to_party('slime')
        save_manager.save_game(p1, self.db_path)

        p2 = Player('B', user_id=self.user2)
        p2.add_monster_to_party('goblin')
        save_manager.save_game(p2, self.db_path)

        l1 = save_manager.load_game(self.db_path, user_id=self.user1)
        l2 = save_manager.load_game(self.db_path, user_id=self.user2)

        self.assertEqual(len(l1.party_monsters), 1)
        self.assertEqual(l1.party_monsters[0].monster_id, 'slime')
        self.assertEqual(len(l2.party_monsters), 1)
        self.assertEqual(l2.party_monsters[0].monster_id, 'goblin')

    def test_exploration_progress_saved_and_loaded(self):
        player = Player('Explorer', user_id=self.user1)
        player.increase_exploration('forest_entrance', 40)
        save_manager.save_game(player, self.db_path)

        loaded = save_manager.load_game(self.db_path, user_id=self.user1)
        self.assertEqual(loaded.get_exploration('forest_entrance'), 40)

    def test_save_and_load_equipment(self):
        player = Player('EquipTester', user_id=self.user1)
        player.equipment_inventory.append(ALL_EQUIPMENT['bronze_sword'])
        save_manager.save_game(player, self.db_path)

        loaded = save_manager.load_game(self.db_path, user_id=self.user1)
        self.assertEqual(len(loaded.equipment_inventory), 1)
        self.assertEqual(loaded.equipment_inventory[0].equip_id, 'bronze_sword')

    def test_hp_mp_persist(self):
        player = Player('HPTester', user_id=self.user1)
        player.add_monster_to_party('slime')
        m = player.party_monsters[0]
        m.hp -= 2
        m.mp -= 1
        save_manager.save_game(player, self.db_path)

        loaded = save_manager.load_game(self.db_path, user_id=self.user1)
        lm = loaded.party_monsters[0]
        self.assertEqual(lm.hp, m.hp)
        self.assertEqual(lm.max_hp, m.max_hp)
        self.assertEqual(lm.mp, m.mp)
        self.assertEqual(lm.max_mp, m.max_mp)

if __name__ == '__main__':
    unittest.main()
