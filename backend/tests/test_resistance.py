"""耐性システム（状態異常耐性・属性ダメージ耐性）のテスト。"""

import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.items.equipment import ALL_EQUIPMENT
from monster_rpg.skills.skill_actions import apply_effects, calculate_skill_damage
from monster_rpg.skills.skills import Skill


def _flame_skill():
    return Skill("Flame", power=20, skill_type="attack", effects=[{"type": "damage"}], category="物理")


class StatusResistTests(unittest.TestCase):
    def setUp(self):
        self.caster = Monster("C", hp=30, attack=10, defense=5)
        self.target = Monster("T", hp=30, attack=10, defense=5)

    def test_normal_target_gets_status(self):
        apply_effects(self.caster, self.target, [{"type": "status", "status": "burn"}], None, [])
        self.assertTrue(any(e["name"] == "burn" for e in self.target.status_effects))

    def test_immunity_blocks_status(self):
        self.target.status_resist = {"burn": 0.0}
        apply_effects(self.caster, self.target, [{"type": "status", "status": "burn"}], None, [])
        self.assertFalse(any(e["name"] == "burn" for e in self.target.status_effects))

    def test_equipment_grants_immunity(self):
        self.target.equip(ALL_EQUIPMENT["ward_of_purity"])  # 毒無効
        apply_effects(self.caster, self.target, [{"type": "status", "status": "poison"}], None, [])
        self.assertFalse(any(e["name"] == "poison" for e in self.target.status_effects))


class ElementResistTests(unittest.TestCase):
    def setUp(self):
        self.caster = Monster("Pyro", hp=30, attack=20, defense=5, element="火")

    def test_resist_halves_damage(self):
        normal = Monster("N", hp=300, attack=5, defense=5, element="無")
        resistant = Monster("R", hp=300, attack=5, defense=5, element="無")
        resistant.element_resist = {"火": 0.5}
        dn = calculate_skill_damage(self.caster, normal, _flame_skill())
        dr = calculate_skill_damage(self.caster, resistant, _flame_skill())
        self.assertEqual(dr, int(dn * 0.5))

    def test_immunity_zeroes_damage(self):
        immune = Monster("I", hp=300, attack=5, defense=5, element="無")
        immune.element_resist = {"火": 0.0}
        self.assertEqual(calculate_skill_damage(self.caster, immune, _flame_skill()), 0)

    def test_weakness_increases_damage(self):
        normal = Monster("N", hp=300, attack=5, defense=5, element="無")
        weak = Monster("W", hp=300, attack=5, defense=5, element="無")
        weak.element_resist = {"火": 1.5}
        self.assertGreater(
            calculate_skill_damage(self.caster, weak, _flame_skill()),
            calculate_skill_damage(self.caster, normal, _flame_skill()),
        )


class TemplateResistTests(unittest.TestCase):
    def test_fire_monster_resists_fire_and_burn(self):
        m = ALL_MONSTERS["lava_elemental"]
        self.assertEqual(m.element_damage_factor("火"), 0.5)
        self.assertEqual(m.status_resistance("burn"), 0.0)

    def test_undead_weak_to_light_immune_poison(self):
        m = ALL_MONSTERS["skeleton_archer"]
        self.assertGreater(m.element_damage_factor("光"), 1.0)
        self.assertEqual(m.status_resistance("poison"), 0.0)

    def test_construct_weak_to_thunder(self):
        m = ALL_MONSTERS["giant_golem"]
        self.assertGreater(m.element_damage_factor("雷"), 1.0)
        self.assertEqual(m.status_resistance("poison"), 0.0)

    def test_resistance_survives_copy(self):
        m = ALL_MONSTERS["lava_elemental"].copy()
        self.assertEqual(m.status_resistance("burn"), 0.0)


if __name__ == "__main__":
    unittest.main()
