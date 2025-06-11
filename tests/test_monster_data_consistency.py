import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.monster_loader import load_monsters


class MonsterDataConsistencyTests(unittest.TestCase):
    def test_all_monsters_match_json(self):
        loaded_monsters, _ = load_monsters()
        self.assertEqual(set(ALL_MONSTERS.keys()), set(loaded_monsters.keys()))
        for mid in ALL_MONSTERS:
            self.assertEqual(ALL_MONSTERS[mid].name, loaded_monsters[mid].name)


if __name__ == "__main__":
    unittest.main()
