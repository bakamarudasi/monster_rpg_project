import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from player import Player
from items.item_data import ALL_ITEMS

class ItemMonsterSynthesisTests(unittest.TestCase):
    def test_monster_item_fusion(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.items.append(ALL_ITEMS['dragon_scale'])

        success, msg, child = player.synthesize_monster_with_item(0, 'dragon_scale')
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.monster_id, 'dragon_pup')
        self.assertEqual(len(player.items), 0)
        self.assertEqual(player.party_monsters[0].monster_id, 'dragon_pup')

if __name__ == '__main__':
    unittest.main()
