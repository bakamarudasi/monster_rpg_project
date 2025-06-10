import unittest

from monster_rpg.battle import determine_turn_order
from monster_rpg.monsters.monster_class import Monster

class TurnOrderTests(unittest.TestCase):
    def test_determine_turn_order_by_speed(self):
        m1 = Monster('Fast', hp=10, attack=5, defense=3, speed=10)
        m2 = Monster('Slow', hp=10, attack=5, defense=3, speed=4)
        m3 = Monster('Mid', hp=10, attack=5, defense=3, speed=7)
        order = determine_turn_order([m1, m2], [m3])
        self.assertEqual([m.name for m in order], ['Fast', 'Mid', 'Slow'])

if __name__ == '__main__':
    unittest.main()
