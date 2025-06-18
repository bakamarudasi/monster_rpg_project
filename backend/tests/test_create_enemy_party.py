import random
import unittest

from monster_rpg.map_data import Location
from monster_rpg.monsters import Monster

class CreateEnemyPartyTests(unittest.TestCase):
    def test_party_generation_deterministic(self):
        loc = Location(
            location_id="test",
            name="test",
            description="",
            enemy_pool={"slime": 70, "goblin": 30},
            party_size=[1, 2],
            encounter_rate=1.0,
        )
        random.seed(0)
        party = loc.create_enemy_party()
        self.assertIsNotNone(party)
        self.assertTrue(1 <= len(party) <= 2)
        self.assertTrue(all(isinstance(m, Monster) for m in party))
        self.assertEqual([m.monster_id for m in party], ["slime", "goblin"])

if __name__ == "__main__":
    unittest.main()
