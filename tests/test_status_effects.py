import unittest

from monster_rpg import battle
from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill

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

    def test_various_statuses_expire(self):
        statuses = [
            "fear",
            "blind",
            "slow",
            "silence",
            "curse",
            "stun",
            "sleep",
            "confuse",
        ]
        for status in statuses:
            target = Monster("T", hp=20, attack=5, defense=2, speed=10)
            original_speed = target.speed
            attacker = Monster("E", hp=20, attack=5, defense=2)
            skill = Skill("tmp", power=0, cost=0, skill_type="status", effect=status, target="enemy")
            apply_skill_effect(attacker, [target], skill)
            self.assertTrue(any(e["name"] == status for e in target.status_effects))
            duration = battle.STATUS_DEFINITIONS[status]["duration"]
            for _ in range(duration):
                process_status_effects(target)
            self.assertFalse(any(e["name"] == status for e in target.status_effects))
            if status == "slow":
                self.assertEqual(target.speed, original_speed)

if __name__ == '__main__':
    unittest.main()
