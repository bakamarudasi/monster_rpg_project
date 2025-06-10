import unittest

from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS, Skill

class StatusEffectTests(unittest.TestCase):
    def test_poison_damage(self):
        target = Monster('Target', hp=20, attack=5, defense=2)
        attacker = Monster('Enemy', hp=20, attack=5, defense=2)
        skill = Skill('TestPoison', power=0, cost=0, skill_type='status',
                      effect='poison', target='enemy', duration=1)
        apply_skill_effect(attacker, [target], skill)
        self.assertTrue(any(e['name'] == 'poison' for e in target.status_effects))
        process_status_effects(target)
        self.assertEqual(target.hp, 18)

if __name__ == '__main__':
    unittest.main()
