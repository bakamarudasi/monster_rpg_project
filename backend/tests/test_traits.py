"""固有特性（trait）の効果テスト。"""

import unittest
from unittest.mock import patch

from monster_rpg import battle
from monster_rpg.battle import calculate_damage
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill
from monster_rpg.skills.skill_actions import calculate_skill_damage


def mk(**kw):
    base = dict(hp=60, attack=10, defense=5)
    base.update(kw)
    return Monster('X', **base)


def magic_skill(power=20):
    return Skill('FB', power=power, category='魔法', skill_type='magic', target='enemy')


class NewStatTraitTests(unittest.TestCase):
    def test_critical_master_boosts_crit_rate(self):
        m = mk()
        before = m.critical_rate
        m.trait_id = 'critical_master'
        self.assertEqual(m.critical_rate - before, 15)

    def test_evasive_boosts_evasion_rate(self):
        m = mk()
        m.trait_id = 'evasive'
        self.assertEqual(m.evasion_rate, 15)

    def test_magic_ward_reduces_magic_damage(self):
        caster = mk(magic=40)
        plain = mk(defense=0)
        plain.magic_defense = 0
        warded = mk(defense=0)
        warded.magic_defense = 0
        warded.trait_id = 'magic_ward'
        self.assertLess(
            calculate_skill_damage(caster, warded, magic_skill()),
            calculate_skill_damage(caster, plain, magic_skill()),
        )

    def test_mana_leech_restores_mp_on_magic_hit(self):
        leecher = mk(magic=40)
        leecher.trait_id = 'mana_leech'
        leecher.max_mp = 50
        leecher.mp = 0
        target = mk(defense=0)
        target.magic_defense = 0
        calculate_skill_damage(leecher, target, magic_skill())
        self.assertGreater(leecher.mp, 0)

    def test_mana_leech_only_for_caster_not_physical(self):
        leecher = mk(attack=40)
        leecher.trait_id = 'mana_leech'
        leecher.max_mp = 50
        leecher.mp = 0
        target = mk(defense=0)
        phys = Skill('Slash', power=10, category='物理', skill_type='attack', target='enemy')
        calculate_skill_damage(leecher, target, phys)
        self.assertEqual(leecher.mp, 0)   # 物理ではMP回復しない


if __name__ == '__main__':
    unittest.main()
