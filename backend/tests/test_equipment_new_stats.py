"""装備で会心率・回避率・魔防・魔力が付与されること（ドロップ・称号）のテスト。"""

import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.equipment import (
    EquipmentInstance, ALL_EQUIPMENT, RANDOM_STAT_CONFIG,
)
from monster_rpg.items.titles import TITLE_GUARDIANS, TITLE_SAGES


def _base():
    return next(iter(ALL_EQUIPMENT.values()))


class TitleStatTests(unittest.TestCase):
    def test_guardians_title_grants_magic_defense(self):
        m = Monster('M', hp=20, attack=8, defense=10, speed=5)
        before = m.magic_defense
        m.equip(EquipmentInstance(base_item=_base(), title=TITLE_GUARDIANS))
        self.assertEqual(m.magic_defense - before, 5)   # 守護の: 魔防+5

    def test_sages_title_grants_magic(self):
        m = Monster('M', hp=20, attack=8, defense=10, speed=5, magic=10)
        m.equip(EquipmentInstance(base_item=_base(), title=TITLE_SAGES))
        self.assertEqual(m.magic, 15)                   # 賢者の: 魔力+5


class RandomDropPoolTests(unittest.TestCase):
    def _sub_stats(self, category):
        pools = RANDOM_STAT_CONFIG['random_stat_pools_by_category'][category]
        return {e['stat'] for e in pools['sub_stat_pool']}

    def test_weapon_can_roll_crit_and_magic(self):
        subs = self._sub_stats('weapon')
        self.assertIn('critical_rate', subs)
        self.assertIn('magic', subs)

    def test_armor_can_roll_magic_defense_and_evasion(self):
        subs = self._sub_stats('armor')
        self.assertIn('magic_defense', subs)
        self.assertIn('evasion_rate', subs)


class RandomBonusAppliesTests(unittest.TestCase):
    def test_random_magic_defense_sub_stat_is_read(self):
        # 副ステに magic_defense を持つ装備を直接組み、Monster が読むことを確認
        inst = EquipmentInstance(
            base_item=_base(),
            title=None,
            random_bonuses={'sub_stats': [{'stat': 'magic_defense', 'amount': 12}]},
        )
        m = Monster('M', hp=20, attack=8, defense=10, speed=5)
        before = m.magic_defense
        m.equip(inst)
        self.assertEqual(m.magic_defense - before, 12)


if __name__ == '__main__':
    unittest.main()
