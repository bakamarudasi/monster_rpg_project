import random
import unittest

from monster_rpg.battle import calculate_damage
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.equipment import ALL_EQUIPMENT

class DamageCalculationTests(unittest.TestCase):
    def test_elemental_multiplier(self):
        attacker = Monster('Fire', hp=30, attack=20, defense=5, element='火')
        defender = Monster('Wind', hp=30, attack=10, defense=5, element='風')
        random.seed(0)
        dmg = calculate_damage(attacker, defender)
        self.assertEqual(dmg, 22)  # (20-5)=15 *1.5 -> 22.5 -> int 22

    def test_critical_hit(self):
        attacker = Monster('Any', hp=30, attack=20, defense=5, element='火')
        defender = Monster('Other', hp=30, attack=10, defense=5, element='火')
        random.seed(31)  # first random < 0.1
        dmg = calculate_damage(attacker, defender)
        self.assertEqual(dmg, 30)  # (20-5)=15 *1 *2 -> 30

    def test_equipment_modifies_damage(self):
        attacker = Monster('Hero', hp=30, attack=10, defense=3)
        defender = Monster('Monster', hp=30, attack=10, defense=3)
        random.seed(2)
        base_dmg = calculate_damage(attacker, defender)

        attacker.equip(ALL_EQUIPMENT['bronze_sword'])
        defender.equip(ALL_EQUIPMENT['leather_armor'])
        random.seed(2)
        equipped_dmg = calculate_damage(attacker, defender)

        self.assertGreater(equipped_dmg, base_dmg)

if __name__ == '__main__':
    unittest.main()
