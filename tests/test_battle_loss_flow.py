import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main
from player import Player
from monsters.monster_data import ALL_MONSTERS

class BattleLossFlowTest(unittest.TestCase):
    def setUp(self):
        self.hero = Player('Tester')
        self.hero.add_monster_to_party('slime')
        self.hero.current_location_id = 'village_square'

    def test_loss_triggers_handler(self):
        inputs = ['1', '1']
        with patch('main.start_battle', return_value='lose'), \
             patch('main.handle_battle_loss', return_value='exit') as mock_handler, \
             patch('main.random.random', return_value=0.0), \
             patch('builtins.input', side_effect=inputs):
            main.game_loop(self.hero)
            self.assertTrue(mock_handler.called)

if __name__ == '__main__':
    unittest.main()
