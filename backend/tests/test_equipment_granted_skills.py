import copy
import unittest

from monster_rpg.items.equipment import EquipmentInstance, BRONZE_SWORD, ALL_EQUIPMENT
from monster_rpg.items.titles import TITLE_MAGICAL
from monster_rpg.skills.skills import ALL_SKILLS
from monster_rpg.monsters.monster_class import Monster


class EquipmentGrantedSkillsTests(unittest.TestCase):
    def test_granted_skills_are_deepcopied(self):
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=TITLE_MAGICAL)
        skills = equip.granted_skills
        self.assertTrue(skills)
        original_power = ALL_SKILLS['fireball'].power
        skills[0].power += 10
        self.assertEqual(ALL_SKILLS['fireball'].power, original_power)
        self.assertIsNot(skills[0], ALL_SKILLS['fireball'])


class BaseEquipmentGrantsSkillTests(unittest.TestCase):
    def test_base_equipment_grants_skill(self):
        shield = ALL_EQUIPMENT['aegis_shield']
        names = [s.name for s in shield.granted_skills]
        self.assertIn(ALL_SKILLS['barrier'].name, names)

    def test_equipping_adds_skill_to_total_skills(self):
        m = Monster('Knight', hp=40, attack=10, defense=5)
        self.assertNotIn(ALL_SKILLS['barrier'].name, [s.name for s in m.total_skills])
        m.equip(ALL_EQUIPMENT['aegis_shield'])
        self.assertIn(ALL_SKILLS['barrier'].name, [s.name for s in m.total_skills])

    def test_no_duplicate_with_innate_skill(self):
        # 既に fireball を覚えているモンスターが炎刃の剣(fireball付与)を装備しても重複しない
        m = Monster('Mage', hp=40, attack=10, defense=5,
                    skills=[copy.deepcopy(ALL_SKILLS['fireball'])])
        m.equip(ALL_EQUIPMENT['flame_blade'])
        count = sum(1 for s in m.total_skills if s.name == ALL_SKILLS['fireball'].name)
        self.assertEqual(count, 1)

    def test_instance_dedupes_base_and_title(self):
        # 素装備(炎刃=fireball)＋ fireball を付与するタイトルでも1つに集約される
        inst = EquipmentInstance(base_item=ALL_EQUIPMENT['flame_blade'], title=TITLE_MAGICAL)
        count = sum(1 for s in inst.granted_skills if s.name == ALL_SKILLS['fireball'].name)
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
