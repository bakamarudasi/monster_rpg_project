import unittest

from monster_rpg.player import Player
from monster_rpg.monsters.synthesis_rules import RANK_VALUES

class RankFamilySynthesisTests(unittest.TestCase):
    def test_rank_affects_family_fusion(self):
        # Low rank parents
        p_low = Player('Low')
        p_low.add_monster_to_party('slime')
        p_low.add_monster_to_party('goblin')
        success_low, _, child_low = p_low.synthesize_monster(0, 1)
        self.assertTrue(success_low)

        # High rank parents (same families)
        p_high = Player('High')
        p_high.add_monster_to_party('slime')
        p_high.add_monster_to_party('shadow_panther')
        success_high, _, child_high = p_high.synthesize_monster(0, 1)
        self.assertTrue(success_high)

        self.assertGreater(RANK_VALUES[child_high.rank], RANK_VALUES[child_low.rank])

if __name__ == '__main__':
    unittest.main()
