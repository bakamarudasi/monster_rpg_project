"""魔法防御（魔防）のテスト。"""

import unittest

from monster_rpg.monsters.monster_class import (
    Monster,
    GROWTH_TYPE_MAGIC,
    GROWTH_TYPE_DEFENSE,
)
from monster_rpg.skills.skills import ALL_SKILLS
from monster_rpg.skills.skill_actions import calculate_skill_damage
from monster_rpg import elements


class MagicDefenseStatTests(unittest.TestCase):
    def test_equals_physical_defense_at_creation(self):
        m = Monster('X', hp=20, attack=8, defense=12, speed=5)
        self.assertEqual(m.magic_defense, m.defense)   # Lv1 は同値＝従来バランス

    def test_diverges_by_growth_type(self):
        mage = Monster('Mage', hp=20, attack=8, defense=12, magic=8, growth_type=GROWTH_TYPE_MAGIC)
        tank = Monster('Tank', hp=20, attack=8, defense=12, growth_type=GROWTH_TYPE_DEFENSE)
        mage.advance_to_level(30)
        tank.advance_to_level(30)
        self.assertGreater(mage.magic_defense, mage.defense)   # 術者は魔法に強い
        self.assertGreater(tank.defense, tank.magic_defense)   # 物理盾は魔法に弱い

    def test_copy_preserves_magic_defense(self):
        m = Monster('X', hp=20, attack=8, defense=12, magic=8, growth_type=GROWTH_TYPE_MAGIC)
        m.advance_to_level(20)
        c = m.copy()
        self.assertEqual(c.magic_defense, m.magic_defense)


class MagicDamageUsesMagicDefenseTests(unittest.TestCase):
    def setUp(self):
        elements.clear_field()
        self.mag_skill = next(s for s in ALL_SKILLS.values() if getattr(s, 'category', None) == '魔法')

    def tearDown(self):
        elements.clear_field()

    def test_magic_damage_scales_with_magic_defense_not_physical(self):
        caster = Monster('C', hp=20, attack=5, defense=5, magic=60, element=None)
        # A: 物理防御は高いが魔防0  /  B: 物理防御0だが魔防は高い
        low_mdef = Monster('A', hp=999, attack=1, defense=100, element=None)
        low_mdef.magic_defense = 0
        high_mdef = Monster('B', hp=999, attack=1, defense=0, element=None)
        high_mdef.magic_defense = 100
        dmg_low = calculate_skill_damage(caster, low_mdef, self.mag_skill)
        dmg_high = calculate_skill_damage(caster, high_mdef, self.mag_skill)
        # 魔防が低い方が多く食らう＝物理防御ではなく魔防で軽減されている
        self.assertGreater(dmg_low, dmg_high)


if __name__ == '__main__':
    unittest.main()
