import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS

class MonsterBookTests(unittest.TestCase):
    def test_record_captured(self):
        player = Player('Tester')
        self.assertNotIn('slime', player.monster_book.captured)
        player.add_monster_to_party('slime')
        self.assertIn('slime', player.monster_book.captured)
        self.assertIn('slime', player.monster_book.seen)

if __name__ == '__main__':
    unittest.main()
