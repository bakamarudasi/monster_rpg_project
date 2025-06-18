import unittest

from monster_rpg.battle import determine_turn_order
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.equipment import EquipmentInstance, BRONZE_SWORD
from monster_rpg.items.titles import TITLE_GALE

class TurnOrderTests(unittest.TestCase):
    def test_determine_turn_order_by_speed(self):
        m1 = Monster('Fast', hp=10, attack=5, defense=3, speed=10)
        m2 = Monster('Slow', hp=10, attack=5, defense=3, speed=4)
        m3 = Monster('Mid', hp=10, attack=5, defense=3, speed=7)
        order = determine_turn_order([m1, m2], [m3])
        self.assertEqual([m.name for m in order], ['Fast', 'Mid', 'Slow'])

    def test_title_speed_bonus_affects_turn_order(self):
        boosted = Monster('Boosted', hp=10, attack=5, defense=3, speed=5)
        normal = Monster('Normal', hp=10, attack=5, defense=3, speed=5)
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=TITLE_GALE)
        boosted.equip(equip)
        order = determine_turn_order([boosted], [normal])
        self.assertEqual(order[0], boosted)

if __name__ == '__main__':
    unittest.main()
