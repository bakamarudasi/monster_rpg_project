import unittest
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skill_actions import SKILL_EFFECT_MAP, buff_atk_def_up
from monster_rpg.battle import apply_skill_effect
from monster_rpg.skills.skills import ALL_SKILLS, Skill


class SkillActionIntegrationTests(unittest.TestCase):
    def test_status_mapping_poison(self):
        target = Monster('Target', hp=20, attack=5, defense=2)
        skill = Skill('Poison', power=0, skill_type='status', effect='poison')
        SKILL_EFFECT_MAP['poison'](None, target, skill)
        self.assertTrue(any(e['name'] == 'poison' for e in target.status_effects))

    def test_brave_song_uses_buff_function(self):
        m1 = Monster('Hero', hp=30, attack=10, defense=10)
        m2 = Monster('Ally', hp=30, attack=12, defense=12)
        allies = [m1, m2]
        skill = ALL_SKILLS['brave_song']
        called = []
        original = SKILL_EFFECT_MAP['atk_def_up']

        def wrapper(caster, target, skill_obj, **kwargs):
            called.append(target)
            return original(caster, target, skill_obj, **kwargs)

        SKILL_EFFECT_MAP['atk_def_up'] = wrapper
        try:
            apply_skill_effect(m1, [m1], skill, all_allies=allies)
        finally:
            SKILL_EFFECT_MAP['atk_def_up'] = original
        self.assertEqual(len(called), 2)


if __name__ == '__main__':
    unittest.main()
