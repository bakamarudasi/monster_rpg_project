import unittest

from monster_rpg.monsters.monster_data import load_monsters
from monster_rpg.monsters.monster_data import ALL_MONSTERS


class MonsterDataConsistencyTests(unittest.TestCase):
    def test_json_and_python_monster_lists_match(self):
        loaded, _ = load_monsters()
        self.assertEqual(set(loaded.keys()), set(ALL_MONSTERS.keys()))
        for mid, monster in loaded.items():
            self.assertEqual(monster.name, ALL_MONSTERS[mid].name)


if __name__ == "__main__":
    unittest.main()
