import unittest

from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS
from monster_rpg.skills.skill_actions import SKILL_EFFECT_MAP


class SkillActionsTests(unittest.TestCase):
    def test_speed_up_via_skill_actions(self):
        self.assertIn('speed_up', SKILL_EFFECT_MAP)
        m = Monster('Hero', hp=20, attack=5, defense=5, speed=10)
        skill = ALL_SKILLS['speed_up']
        apply_skill_effect(m, [m], skill, all_allies=[m])
        self.assertEqual(m.speed, 15)
        for _ in range(skill.duration):
            process_status_effects(m)
        self.assertEqual(m.speed, 10)


if __name__ == '__main__':
    unittest.main()
