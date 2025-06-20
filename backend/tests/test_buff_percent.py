import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.skills.skills import ALL_SKILLS


class BuffPercentTests(unittest.TestCase):
    def test_apply_buff_percent(self):
        m = Monster('Hero', hp=30, attack=10, defense=5)
        m.apply_buff_percent('attack', 0.5, 2)
        self.assertEqual(m.attack, 15)
        self.assertTrue(any(e['name'] == 'buff_percent_attack' for e in m.status_effects))
        for _ in range(2):
            process_status_effects(m)
        self.assertEqual(m.attack, 10)
        self.assertFalse(m.status_effects)

    def test_demonize_skill(self):
        m = Monster('Hero', hp=30, attack=10, defense=5)
        skill = ALL_SKILLS['demonize']
        apply_skill_effect(m, [m], skill)
        self.assertEqual(m.attack, 15)
        for _ in range(skill.duration):
            process_status_effects(m)
        self.assertEqual(m.attack, 10)


if __name__ == '__main__':
    unittest.main()
