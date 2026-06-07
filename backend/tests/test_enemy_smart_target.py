"""敵AIが新ステ（防御・魔防・回避）を踏まえて賢く狙うことのテスト。"""

import unittest

from monster_rpg.battle import _pick_damage_target, enemy_take_action
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill


class PickDamageTargetTests(unittest.TestCase):
    def test_physical_targets_lowest_defense(self):
        attacker = Monster('E', hp=30, attack=20, defense=5)
        tanky = Monster('Tank', hp=40, attack=5, defense=18)
        squishy = Monster('Squish', hp=40, attack=5, defense=2)
        self.assertIs(_pick_damage_target(attacker, [tanky, squishy]), squishy)

    def test_physical_avoids_high_evasion(self):
        attacker = Monster('E', hp=30, attack=20, defense=5)
        dodgy = Monster('Dodgy', hp=40, attack=5, defense=2)
        dodgy._stat_bonuses['evasion_rate'] = 60
        plain = Monster('Plain', hp=40, attack=5, defense=2)
        self.assertIs(_pick_damage_target(attacker, [dodgy, plain]), plain)

    def test_magic_targets_lowest_magic_defense(self):
        caster = Monster('M', hp=30, attack=5, defense=5, magic=30)
        aegis = Monster('Aegis', hp=40, attack=5, defense=2)
        aegis.magic_defense = 30
        frail = Monster('Frail', hp=40, attack=5, defense=2)
        frail.magic_defense = 2
        fb = Skill('FB', power=10, category='魔法', skill_type='magic', target='enemy')
        self.assertIs(_pick_damage_target(caster, [aegis, frail], fb), frail)


class EnemyAttackTargetingTests(unittest.TestCase):
    def test_attacker_hits_low_defense_over_low_hp(self):
        # 低HPだが超高防御の相手より、削りやすい相手を優先する
        attacker = Monster('Atk', hp=40, attack=20, defense=5, ai_role='attacker')
        armored = Monster('Armored', hp=10, attack=5, defense=100)   # ほぼ通らない
        soft = Monster('Soft', hp=45, attack=5, defense=2)
        enemy_take_action(attacker, [armored, soft], [attacker])
        self.assertEqual(armored.hp, 10)     # 硬い相手は殴らない
        self.assertLess(soft.hp, 45)         # 削れる相手を狙う


if __name__ == '__main__':
    unittest.main()
