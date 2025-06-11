import unittest

from monster_rpg.monsters.monster_loader import load_monsters
from monster_rpg.monsters.monster_class import RANK_D


class MonsterLoaderTests(unittest.TestCase):
    def test_default_load(self):
        monsters, book = load_monsters()
        # dictionaries should contain slime and goblin
        self.assertIn('slime', monsters)
        self.assertIn('goblin', monsters)
        self.assertIn('slime', book)
        self.assertIn('goblin', book)

        # validate attributes from JSON
        self.assertEqual(monsters['slime'].name, 'スライム')
        self.assertEqual(monsters['goblin'].rank, RANK_D)


if __name__ == '__main__':
    unittest.main()
