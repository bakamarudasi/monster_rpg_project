import random
import unittest

from monster_rpg.battle import award_experience
from monster_rpg.items.equipment import ALL_EQUIPMENT, EquipmentInstance
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.player import Player

class EquipmentDropTests(unittest.TestCase):
    def test_drop_equipment_added_to_player_inventory(self):
        enemy = Monster('Enemy', hp=30, attack=10, defense=5, level=1,
                        drop_items=[(ALL_EQUIPMENT['bronze_sword'], 1.0)])
        enemy.is_alive = False
        ally = Monster('Ally', hp=30, attack=10, defense=5)
        player = Player('Tester')
        player.party_monsters.append(ally)
        random.seed(0)
        award_experience([ally], [enemy], player)
        self.assertEqual(len(player.equipment_inventory), 1)
        equip = player.equipment_inventory[0]
        self.assertIsInstance(equip, EquipmentInstance)
        self.assertEqual(equip.base_item.equip_id, 'bronze_sword')
        self.assertIsNotNone(equip.title)
        self.assertEqual(equip.title.title_id, 'glass_cannon')

if __name__ == '__main__':
    unittest.main()
