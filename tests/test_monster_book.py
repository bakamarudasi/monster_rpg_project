import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from player import Player
from monsters.monster_data import ALL_MONSTERS

class MonsterBookTests(unittest.TestCase):
    def test_record_captured(self):
        player = Player('Tester')
        self.assertNotIn('slime', player.monster_book.captured)
        player.add_monster_to_party('slime')
        self.assertIn('slime', player.monster_book.captured)
        self.assertIn('slime', player.monster_book.seen)

if __name__ == '__main__':
    unittest.main()
