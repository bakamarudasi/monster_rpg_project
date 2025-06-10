import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS

class PartyFormationTests(unittest.TestCase):
    def setUp(self):
        self.player = Player('Tester')
        for mid in ('slime', 'goblin', 'wolf'):
            if mid in ALL_MONSTERS:
                self.player.add_monster_to_party(mid)

    def test_move_monster(self):
        ids_before = [m.monster_id for m in self.player.party_monsters]
        self.assertEqual(ids_before, ['slime', 'goblin', 'wolf'])
        self.player.move_monster(0, 2)
        ids_after = [m.monster_id for m in self.player.party_monsters]
        self.assertEqual(ids_after, ['goblin', 'wolf', 'slime'])

if __name__ == '__main__':
    unittest.main()
