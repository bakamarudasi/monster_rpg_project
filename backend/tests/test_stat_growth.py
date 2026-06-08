"""MP・魔力の成長と、魔法型の初期魔力に関するテスト（レベル/ステータス処理の見直し）。"""

import unittest

from monster_rpg.monsters.monster_class import (
    Monster,
    MAX_LEVEL,
    GROWTH_TYPE_AVERAGE,
    GROWTH_TYPE_SPEED,
    GROWTH_TYPE_POWER,
    GROWTH_TYPE_MAGIC,
    get_status_gains_average,
    get_status_gains_speed,
)
from monster_rpg.monsters.monster_data import ALL_MONSTERS


class MpGrowthTests(unittest.TestCase):
    def test_mp_grows_for_non_magic_type(self):
        m = Monster('Swift', hp=20, mp=10, attack=8, defense=5, speed=5,
                    growth_type=GROWTH_TYPE_SPEED)
        before = m.max_mp
        m.level_up(verbose=False)
        self.assertEqual(m.max_mp - before, get_status_gains_speed(2)['mp'])
        self.assertGreater(m.max_mp, before)

    def test_mp_grows_for_average_type(self):
        m = Monster('Avg', hp=20, mp=10, attack=8, defense=5, speed=5,
                    growth_type=GROWTH_TYPE_AVERAGE)
        before = m.max_mp
        m.advance_to_level(10)
        self.assertGreater(m.max_mp, before)


class MagicGrowthTests(unittest.TestCase):
    def test_magic_grows_for_all_types(self):
        for gt in (GROWTH_TYPE_AVERAGE, GROWTH_TYPE_SPEED, GROWTH_TYPE_POWER, GROWTH_TYPE_MAGIC):
            m = Monster('M', hp=20, mp=10, attack=8, defense=5, speed=5, growth_type=gt)
            start = m.magic
            m.advance_to_level(15)
            self.assertGreater(m.magic, start, f'{gt} の魔力が伸びていない')

    def test_magic_type_outgrows_physical_in_magic(self):
        mage = Monster('Mage', hp=20, mp=10, attack=8, defense=5, speed=5, magic=8,
                       growth_type=GROWTH_TYPE_MAGIC)
        bruiser = Monster('Bruiser', hp=20, mp=10, attack=8, defense=5, speed=5,
                          growth_type=GROWTH_TYPE_POWER)
        mage.advance_to_level(20)
        bruiser.advance_to_level(20)
        self.assertGreater(mage.magic, bruiser.magic)


class MagicTypeBaseMagicTests(unittest.TestCase):
    def test_magic_type_templates_start_with_magic(self):
        magic_mons = [m for m in ALL_MONSTERS.values() if m.growth_type == GROWTH_TYPE_MAGIC]
        self.assertTrue(magic_mons, '魔法型モンスターが存在しない')
        # 魔法型は Lv1 から術者として機能する（初期魔力 > 0）
        for m in magic_mons:
            self.assertGreater(m.magic, 0, f'{m.name} の初期魔力が0')

    def test_non_magic_type_starts_without_magic(self):
        non_magic = next(m for m in ALL_MONSTERS.values() if m.growth_type != GROWTH_TYPE_MAGIC)
        self.assertEqual(non_magic.magic, 0)


class LevelCapTests(unittest.TestCase):
    def test_advance_to_level_caps_at_max(self):
        m = Monster('T', hp=20, mp=10, attack=8, defense=5)
        m.advance_to_level(MAX_LEVEL + 50)
        self.assertEqual(m.level, MAX_LEVEL)

    def test_gain_exp_does_not_exceed_cap(self):
        m = Monster('T', hp=20, mp=10, attack=8, defense=5)
        m.advance_to_level(MAX_LEVEL)
        m.gain_exp(10 ** 9, verbose=False)
        self.assertEqual(m.level, MAX_LEVEL)
        self.assertEqual(m.exp, 0)
        self.assertIsNone(m.calculate_exp_to_next_level())

    def test_below_cap_still_levels(self):
        # S級は真の最大(MAX_LEVEL)まで経験値で伸びる
        m = Monster('T', hp=20, mp=10, attack=8, defense=5, rank='S')
        m.advance_to_level(MAX_LEVEL - 1)
        m.gain_exp(10 ** 9, verbose=False)
        self.assertEqual(m.level, MAX_LEVEL)

    def test_rank_level_cap(self):
        # ランクが低いほどレベル上限が低い（DQM式の成長限界）
        d = Monster('D', hp=20, mp=10, attack=8, defense=5, rank='D')
        d.gain_exp(10 ** 9, verbose=False)
        self.assertEqual(d.level, d.level_cap)
        self.assertLess(d.level, MAX_LEVEL)
        # ＋値で上限が伸びる
        d2 = Monster('D2', hp=20, mp=10, attack=8, defense=5, rank='D')
        base_cap = d2.level_cap
        d2.plus_value = 3
        self.assertGreater(d2.level_cap, base_cap)


if __name__ == '__main__':
    unittest.main()
