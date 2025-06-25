import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS

class FamilyFusionTests(unittest.TestCase):
    def test_family_field_loaded(self):
        self.assertEqual(ALL_MONSTERS['slime'].family, 'slime')
        self.assertEqual(ALL_MONSTERS['goblin'].family, 'beast')

    def test_family_based_fusion(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.add_monster_to_party('celestial_dragon')

        success, msg, child = player.synthesize_monster(0, 1)
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.monster_id, 'dragon_pup')

if __name__ == '__main__':
    unittest.main()
