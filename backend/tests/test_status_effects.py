import unittest

from monster_rpg import battle
from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill
from unittest.mock import patch

class StatusEffectTests(unittest.TestCase):
    def test_poison_damage(self):
        target = Monster('Target', hp=20, attack=5, defense=2)
        attacker = Monster('Enemy', hp=20, attack=5, defense=2)
        skill = Skill(
            'TestPoison',
            power=0,
            cost=0,
            skill_type='status',
            target='enemy',
            duration=1,
            effects=[{'type': 'status', 'status': 'poison', 'duration': 1}],
        )
        apply_skill_effect(attacker, [target], skill)
        self.assertTrue(any(e['name'] == 'poison' for e in target.status_effects))
        process_status_effects(target)
        self.assertEqual(target.hp, 18)

    def test_status_applies_with_chance(self):
        attacker = Monster('Enemy', hp=20, attack=5, defense=2)
        target = Monster('T', hp=20, attack=5, defense=2)
        skill = Skill(
            'Temp',
            power=0,
            skill_type='status',
            effects=[{'type': 'status', 'status': 'paralyze', 'chance': 0.5}],
        )
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.3):
            apply_skill_effect(attacker, [target], skill)
        self.assertTrue(any(e['name'] == 'paralyze' for e in target.status_effects))
        target2 = Monster('T2', hp=20, attack=5, defense=2)
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.8):
            apply_skill_effect(attacker, [target2], skill)
        self.assertFalse(any(e['name'] == 'paralyze' for e in target2.status_effects))

    def test_spore_poison_damage_fraction(self):
        attacker = Monster('Shroom', hp=20, attack=5, defense=2)
        target = Monster('Victim', hp=32, attack=5, defense=2)
        skill = Skill(
            'PoisonSpore',
            power=0,
            skill_type='status',
            effects=[{'type': 'status', 'status': 'spore_poison', 'chance': 1.0}],
        )
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.0):
            apply_skill_effect(attacker, [target], skill)
        dmg = max(1, target.max_hp // 16)
        for _ in range(3):
            process_status_effects(target)
        self.assertEqual(target.hp, target.max_hp - dmg * 3)

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
            "taunt",
            "cant_attack",
        ]
        for status in statuses:
            target = Monster("T", hp=20, attack=5, defense=2, speed=10)
            original_speed = target.speed
            attacker = Monster("E", hp=20, attack=5, defense=2)
            skill = Skill(
                "tmp",
                power=0,
                cost=0,
                skill_type="status",
                target="enemy",
                effects=[{'type': 'status', 'status': status}],
            )
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
