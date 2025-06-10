import unittest

from monster_rpg.battle import apply_skill_effect, process_status_effects
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS

class PartyBuffTests(unittest.TestCase):
    def test_brave_song_buff_applies_to_all_allies(self):
        m1 = Monster('Hero', hp=30, attack=10, defense=10)
        m2 = Monster('Ally', hp=30, attack=12, defense=12)
        allies = [m1, m2]
        skill = ALL_SKILLS['brave_song']
        apply_skill_effect(m1, [m1], skill, all_allies=allies)
        self.assertEqual(m1.attack, 15)
        self.assertEqual(m2.attack, 17)
        # effect should wear off after duration turns
        for _ in range(skill.duration):
            for m in allies:
                process_status_effects(m)
        self.assertEqual(m1.attack, 10)
        self.assertEqual(m2.attack, 12)

if __name__ == '__main__':
    unittest.main()
