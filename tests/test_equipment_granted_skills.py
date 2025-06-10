import unittest

from monster_rpg.items.equipment import EquipmentInstance, BRONZE_SWORD
from monster_rpg.items.titles import TITLE_MAGICAL
from monster_rpg.skills.skills import ALL_SKILLS


class EquipmentGrantedSkillsTests(unittest.TestCase):
    def test_granted_skills_are_deepcopied(self):
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=TITLE_MAGICAL)
        skills = equip.granted_skills
        self.assertTrue(skills)
        original_power = ALL_SKILLS['fireball'].power
        skills[0].power += 10
        self.assertEqual(ALL_SKILLS['fireball'].power, original_power)
        self.assertIsNot(skills[0], ALL_SKILLS['fireball'])


if __name__ == '__main__':
    unittest.main()
