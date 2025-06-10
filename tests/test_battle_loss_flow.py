import unittest
from unittest.mock import patch

from monster_rpg import main
from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS

class BattleLossFlowTest(unittest.TestCase):
    def setUp(self):
        self.hero = Player('Tester')
        self.hero.add_monster_to_party('slime')
        self.hero.current_location_id = 'village_square'

    def test_loss_triggers_handler(self):
        inputs = ['1', '1']
        with patch('monster_rpg.main.start_battle', return_value='lose'), \
             patch('monster_rpg.main.handle_battle_loss', return_value='exit') as mock_handler, \
             patch('monster_rpg.main.random.random', return_value=0.0), \
             patch('builtins.input', side_effect=inputs):
            main.game_loop(self.hero)
            self.assertTrue(mock_handler.called)

if __name__ == '__main__':
    unittest.main()
