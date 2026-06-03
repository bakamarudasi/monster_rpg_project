import random
import unittest

from monster_rpg.map_data import load_locations, LOCATIONS

class EnemyWeightSelectionTests(unittest.TestCase):
    def test_weighted_selection_deterministic(self):
        load_locations()
        loc = LOCATIONS['forest_entrance']
        # forest_entrance の出現プールには新モンスター(meadow_sprite 等)も含まれる。
        # 同一シードで毎回同じ抽選結果になる＝決定的であることを確認する。
        random.seed(0)
        self.assertEqual(loc.get_random_enemy_id(), 'meadow_sprite')
        random.seed(1)
        self.assertEqual(loc.get_random_enemy_id(), 'goblin')

if __name__ == '__main__':
    unittest.main()
