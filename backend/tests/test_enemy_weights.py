import random
import unittest

from monster_rpg.map_data import load_locations, LOCATIONS

class EnemyWeightSelectionTests(unittest.TestCase):
    def test_weighted_selection_deterministic(self):
        load_locations()
        loc = LOCATIONS['forest_entrance']
        random.seed(0)
        self.assertEqual(loc.get_random_enemy_id(), 'slime')
        random.seed(1)
        self.assertEqual(loc.get_random_enemy_id(), 'goblin')

if __name__ == '__main__':
    unittest.main()
