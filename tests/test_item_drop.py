import os
import sys
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from battle import award_experience
from items.item_data import ALL_ITEMS
from monsters.monster_class import Monster
from player import Player

class ItemDropTests(unittest.TestCase):
    def test_drop_item_added_to_player(self):
        enemy = Monster('Enemy', hp=30, attack=10, defense=5, level=1,
                        drop_items=[(ALL_ITEMS['small_potion'], 1.0)])
        enemy.is_alive = False
        ally = Monster('Ally', hp=30, attack=10, defense=5)
        player = Player('Tester')
        player.party_monsters.append(ally)
        random.seed(0)
        award_experience([ally], [enemy], player)
        self.assertEqual(len(player.items), 1)
        self.assertEqual(player.items[0].item_id, 'small_potion')

if __name__ == '__main__':
    unittest.main()
