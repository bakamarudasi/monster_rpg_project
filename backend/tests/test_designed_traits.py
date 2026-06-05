"""ボス/強敵に固定付与された特性のテスト。"""

import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.personality import ALL_TRAITS


class DesignedTraitTests(unittest.TestCase):
    def test_boss_has_designed_trait(self):
        queen = ALL_MONSTERS['poison_queen']
        self.assertEqual(queen.trait.id, 'afflictor')   # 腐毒の女王＝状態異常の達人
        self.assertTrue(queen._designed_trait)

    def test_designed_trait_survives_wild_roll(self):
        # ヴァンパイアロード（非ボスの強敵）は野生化(roll_individuality)しても吸血を保つ
        vl = ALL_MONSTERS['vampire_lord'].copy()
        vl.roll_individuality()
        self.assertEqual(vl.trait.id, 'lifesteal')
        self.assertTrue(vl._designed_trait)

    def test_copy_preserves_designed_flag(self):
        m = ALL_MONSTERS['phoenix_chick'].copy()
        self.assertTrue(m._designed_trait)
        self.assertEqual(m.trait.id, 'endure')

    def test_ordinary_monster_has_no_designed_trait(self):
        slime = ALL_MONSTERS['slime'].copy()
        self.assertFalse(slime._designed_trait)

    def test_all_designed_traits_are_valid(self):
        designed = [m for m in ALL_MONSTERS.values() if m._designed_trait]
        self.assertGreater(len(designed), 10)   # それなりの数を仕込んでいる
        for m in designed:
            self.assertIn(m.trait_id, ALL_TRAITS, f'{m.name} の特性が不正')


if __name__ == '__main__':
    unittest.main()
