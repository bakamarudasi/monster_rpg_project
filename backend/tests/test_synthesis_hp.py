import unittest

from monster_rpg.player import Player


class SynthesisHPTests(unittest.TestCase):
    def test_child_hp_full_after_synthesis(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.add_monster_to_party('wolf')

        success, msg, child = player.synthesize_monster(0, 1)
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.hp, child.max_hp)


if __name__ == '__main__':
    unittest.main()
