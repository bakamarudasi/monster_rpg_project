import os
import unittest
import random

from monster_rpg import database_setup
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.items.equipment import (
    EquipmentInstance,
    BRONZE_SWORD,
    create_titled_equipment,
)
from monster_rpg.items.item_data import ALL_ITEMS


class EquipmentSynthesisTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_synth.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('synth', 'pw')

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_disassemble_equipment_gives_material(self):
        player = Player('Tester', user_id=self.user_id)
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=None)
        player.equipment_inventory.append(equip)
        success = player.disassemble_equipment(equip.instance_id)
        self.assertTrue(success)
        self.assertEqual(len(player.equipment_inventory), 0)
        self.assertEqual(len(player.items), 1)
        self.assertEqual(player.items[0].item_id, 'weapon_core_common')

    def test_limit_break_fails_without_material_and_keeps_item(self):
        player = Player('Tester', user_id=self.user_id)
        player.equipment_inventory.append(BRONZE_SWORD)
        self.assertFalse(player.limit_break_equipment(BRONZE_SWORD.equip_id))
        self.assertEqual(len(player.equipment_inventory), 1)
        self.assertIs(player.equipment_inventory[0], BRONZE_SWORD)
        self.assertNotIsInstance(player.equipment_inventory[0], EquipmentInstance)

    def test_limit_break_persists(self):
        player = Player('Tester', user_id=self.user_id)
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=None)
        player.equipment_inventory.append(equip)
        player.items.extend([ALL_ITEMS['weapon_core_common'] for _ in range(5)])
        self.assertTrue(player.limit_break_equipment(equip.instance_id))
        save_manager.save_game(player, self.db_path, user_id=self.user_id)
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual(loaded.equipment_inventory[0].synthesis_rank, 1)
        self.assertGreater(loaded.equipment_inventory[0].stat_multiplier, 1.0)

    def test_sub_stat_slots_persist_and_limit(self):
        random.seed(0)
        player = Player('Tester', user_id=self.user_id)
        equip = create_titled_equipment('bronze_sword')
        player.equipment_inventory.append(equip)
        initial_slots = len(equip.random_bonuses.get('sub_stats', []))
        self.assertEqual(equip.sub_stat_slots, initial_slots)
        player.items.extend([ALL_ITEMS['weapon_core_common'] for _ in range(20)])
        player.items.extend([ALL_ITEMS['weapon_core_rare'] for _ in range(10)])
        self.assertTrue(player.limit_break_equipment(equip.instance_id))
        self.assertTrue(player.limit_break_equipment(equip.instance_id))
        self.assertTrue(player.limit_break_equipment(equip.instance_id))
        self.assertLessEqual(
            len(equip.random_bonuses.get('sub_stats', [])), equip.sub_stat_slots
        )
        save_manager.save_game(player, self.db_path, user_id=self.user_id)
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        loaded_equip = loaded.equipment_inventory[0]
        self.assertEqual(loaded_equip.sub_stat_slots, equip.sub_stat_slots)
        self.assertEqual(
            len(loaded_equip.random_bonuses.get('sub_stats', [])),
            len(equip.random_bonuses.get('sub_stats', [])),
        )


if __name__ == '__main__':
    unittest.main()
