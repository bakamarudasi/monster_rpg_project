import unittest
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skill_actions import apply_effects
from monster_rpg.battle import apply_skill_effect
from monster_rpg.skills.skills import ALL_SKILLS, Skill


class SkillActionIntegrationTests(unittest.TestCase):
    def test_status_mapping_poison(self):
        target = Monster('Target', hp=20, attack=5, defense=2)
        skill = Skill('Poison', power=0, skill_type='status', effects=[{'type': 'status', 'status': 'poison'}])
        apply_effects(target, target, skill.effects, skill)
        self.assertTrue(any(e['name'] == 'poison' for e in target.status_effects))

    def test_brave_song_uses_buff_function(self):
        m1 = Monster('Hero', hp=30, attack=10, defense=10)
        m2 = Monster('Ally', hp=30, attack=12, defense=12)
        allies = [m1, m2]
        skill = ALL_SKILLS['brave_song']
        apply_skill_effect(m1, [m1], skill, all_allies=allies)
        self.assertEqual(m1.attack, 15)
        self.assertEqual(m2.attack, 17)

    def test_damage_scaling_uses_correct_stats(self):
        warrior = Monster('Warrior', hp=30, attack=20, defense=5)
        warrior.magic = 5
        mage = Monster('Mage', hp=30, attack=5, defense=5)
        mage.magic = 20
        target1 = Monster('Target1', hp=50, attack=5, defense=5)
        target2 = Monster('Target2', hp=50, attack=5, defense=5)

        phys_skill = Skill('Slash', power=10, skill_type='attack', effects=[{'type': 'damage'}], category='物理')
        mag_skill = Skill('Bolt', power=10, skill_type='attack', effects=[{'type': 'damage'}], category='魔法')

        apply_skill_effect(warrior, [target1], phys_skill)
        apply_skill_effect(mage, [target2], phys_skill)
        self.assertGreater(target2.hp, target1.hp)

        target3 = Monster('Target3', hp=50, attack=5, defense=5)
        target4 = Monster('Target4', hp=50, attack=5, defense=5)
        apply_skill_effect(warrior, [target3], mag_skill)
        apply_skill_effect(mage, [target4], mag_skill)
        self.assertGreater(target3.hp, target4.hp)

    def test_hp_cost_percent_handler(self):
        m = Monster('Hero', hp=50, attack=10, defense=5)
        ctx = apply_effects(m, m, [{'type': 'hp_cost_percent', 'percent': 0.2}])
        self.assertEqual(m.hp, 40)
        self.assertIn('last_hp_cost', ctx)
        self.assertEqual(ctx['last_hp_cost'], 10)

    def test_blood_saber_skill(self):
        hero = Monster('Hero', hp=50, attack=15, defense=5)
        enemy = Monster('Enemy', hp=40, attack=5, defense=2)
        skill = ALL_SKILLS['blood_saber']
        apply_skill_effect(hero, [enemy], skill)
        self.assertEqual(hero.hp, 45)
        self.assertLess(enemy.hp, 40)

    def test_last_wish_skill(self):
        hero = Monster('Hero', hp=30, attack=15, defense=5)
        enemy = Monster('Enemy', hp=40, attack=5, defense=2)
        skill = ALL_SKILLS['last_wish']
        apply_skill_effect(hero, [enemy], skill)
        self.assertFalse(hero.is_alive)
        self.assertEqual(hero.hp, 0)
        self.assertLess(enemy.hp, 40)


if __name__ == '__main__':
    unittest.main()
