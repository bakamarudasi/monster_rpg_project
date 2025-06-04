import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from battle import determine_turn_order
from monsters.monster_class import Monster

class TurnOrderTests(unittest.TestCase):
    def test_determine_turn_order_by_speed(self):
        m1 = Monster('Fast', hp=10, attack=5, defense=3, speed=10)
        m2 = Monster('Slow', hp=10, attack=5, defense=3, speed=4)
        m3 = Monster('Mid', hp=10, attack=5, defense=3, speed=7)
        order = determine_turn_order([m1, m2], [m3])
        self.assertEqual([m.name for m in order], ['Fast', 'Mid', 'Slow'])

if __name__ == '__main__':
    unittest.main()
