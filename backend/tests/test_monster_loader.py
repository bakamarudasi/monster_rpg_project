import unittest

from monster_rpg.monsters.monster_data import load_monsters
from monster_rpg.monsters.monster_class import (
    RANK_D,
    GROWTH_TYPE_POWER,
    GROWTH_TYPE_MAGIC,
)


class MonsterLoaderTests(unittest.TestCase):
    def test_default_load(self):
        monsters, book = load_monsters()
        # dictionaries should contain slime and goblin
        self.assertIn('slime', monsters)
        self.assertIn('goblin', monsters)
        self.assertIn('slime', book)
        self.assertIn('goblin', book)

        # validate attributes from JSON
        self.assertEqual(monsters['slime'].name, 'スライム')
        self.assertEqual(monsters['goblin'].rank, RANK_D)
        self.assertEqual(monsters['orc_warrior'].growth_type, GROWTH_TYPE_POWER)
        self.assertEqual(monsters['elf_mage'].growth_type, GROWTH_TYPE_MAGIC)
        self.assertEqual(monsters['slime'].family, 'slime')
        self.assertEqual(monsters['goblin'].family, 'beast')

    def test_skill_sets_provide_skills_and_learnset(self):
        monsters, _ = load_monsters()
        goblin = monsters['goblin']
        # starting skills from skill set
        skill_names = [s.name for s in goblin.skills]
        self.assertIn('ファイアボール', skill_names)

        # copy to level up
        g = goblin.copy()
        # gain enough exp to reach level 3
        for _ in range(2):
            exp_needed = g.calculate_exp_to_next_level()
            g.gain_exp(exp_needed)

        learned_names = [s.name for s in g.skills]
        self.assertIn('パワーアップ', learned_names)


if __name__ == '__main__':
    unittest.main()
