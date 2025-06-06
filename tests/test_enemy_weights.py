import os
import sys
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map_data import Location

class EnemyWeightsTests(unittest.TestCase):
    def test_weighted_enemy_selection(self):
        loc = Location(
            location_id="test",
            name="Test",
            description="",
            possible_enemies=["slime", "goblin"],
            enemy_weights={"slime": 0.8, "goblin": 0.2},
            encounter_rate=1.0,
        )
        random.seed(0)
        counts = {"slime": 0, "goblin": 0}
        for _ in range(200):
            eid = loc.get_random_enemy_id()
            counts[eid] += 1
        self.assertGreater(counts["slime"], counts["goblin"])

    def test_default_random_choice_used_when_no_weights(self):
        loc = Location(
            location_id="test2",
            name="Test2",
            description="",
            possible_enemies=["slime", "goblin"],
            encounter_rate=1.0,
        )
        with unittest.mock.patch('random.choice', return_value='slime') as mock_choice:
            self.assertEqual(loc.get_random_enemy_id(), 'slime')
            mock_choice.assert_called_once_with(loc.possible_enemies)

if __name__ == '__main__':
    unittest.main()
