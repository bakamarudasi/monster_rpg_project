import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from battle import award_experience
from monsters.monster_class import Monster

class ExperienceDistributionTests(unittest.TestCase):
    def test_experience_split_with_remainder(self):
        p1 = Monster('M1', hp=20, attack=5, defense=5)
        p2 = Monster('M2', hp=20, attack=5, defense=5)
        p3 = Monster('M3', hp=20, attack=5, defense=5)
        p3.is_alive = False
        enemy = Monster('E', hp=55, attack=5, defense=5, level=1)
        enemy.is_alive = False
        award_experience([p1, p2, p3], [enemy], None)
        self.assertEqual(p1.exp, 11)
        self.assertEqual(p2.exp, 10)
        self.assertEqual(p3.exp, 0)

if __name__ == '__main__':
    unittest.main()
