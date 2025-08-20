import unittest
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skill_actions import apply_effects

class DamageEffectNoSkillTests(unittest.TestCase):
    def test_damage_effect_without_skill_uses_log(self):
        attacker = Monster('Hero', hp=50, attack=10, defense=5)
        target = Monster('Slime', hp=30, attack=5, defense=2)
        log = []
        apply_effects(attacker, target, [{'type': 'damage', 'amount': 10}], None, log)
        expected_damage = max(1, 10 - target.defense)
        self.assertEqual(target.hp, 30 - expected_damage)
        self.assertTrue(any('damage' in entry['message'] for entry in log))

if __name__ == '__main__':
    unittest.main()
