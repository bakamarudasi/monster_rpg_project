import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.battle import apply_skill_effect, process_status_effects, process_charge_state
from monster_rpg.skills.skills import Skill

class ChargeReleaseTests(unittest.TestCase):
    def test_charge_to_release_flow(self):
        attacker = Monster('Hero', hp=30, attack=10, defense=5)
        enemy = Monster('Slime', hp=30, attack=5, defense=2)
        original_def = attacker.defense
        charge_skill = Skill('Charge', power=0, skill_type='status',
                             effects=[{'type': 'charge', 'release_skill_id': 'tackle'}])
        apply_skill_effect(attacker, [attacker], charge_skill)
        self.assertTrue(any(e['name'] == 'charging' for e in attacker.status_effects))
        process_status_effects(attacker)
        triggered = process_charge_state(attacker, [attacker], [enemy])
        self.assertTrue(triggered)
        self.assertFalse(any(e['name'] == 'charging' for e in attacker.status_effects))
        self.assertEqual(attacker.defense, original_def)
        self.assertEqual(enemy.hp, enemy.max_hp - 21)

if __name__ == '__main__':
    unittest.main()
