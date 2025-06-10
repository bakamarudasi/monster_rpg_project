import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS

class SynthesisInheritanceTests(unittest.TestCase):
    def test_skill_and_stat_inheritance(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.add_monster_to_party('wolf')

        player.party_monsters[0].level = 5
        player.party_monsters[1].level = 5

        success, msg, child = player.synthesize_monster(0, 1)
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.monster_id, 'water_wolf')

        # Child should inherit heal from slime
        skill_names = [s.name for s in child.skills]
        self.assertIn('ヒール', skill_names)

        # Stats should receive a bonus
        template = ALL_MONSTERS['water_wolf']
        self.assertGreater(child.max_hp, template.max_hp)
        self.assertGreater(child.attack, template.attack)

if __name__ == '__main__':
    unittest.main()
