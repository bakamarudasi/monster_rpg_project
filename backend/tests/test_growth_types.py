import unittest
import io
from contextlib import redirect_stdout

from monster_rpg.monsters.monster_class import (
    Monster,
    GROWTH_TYPE_POWER,
    GROWTH_TYPE_MAGIC,
    GROWTH_TYPE_DEFENSE,
    GROWTH_TYPE_SPEED,
    get_status_gains_power,
    get_status_gains_magic,
    get_status_gains_defense,
    get_status_gains_speed,
)

class GrowthTypeLevelUpTests(unittest.TestCase):
    def test_power_growth_attack_increase(self):
        m = Monster('Power', hp=20, attack=5, defense=5, mp=10, growth_type=GROWTH_TYPE_POWER)
        start_attack = m.attack
        buf = io.StringIO()
        with redirect_stdout(buf):
            m.level_up()
        output = buf.getvalue()
        gain = get_status_gains_power(2)['attack']
        self.assertEqual(m.attack - start_attack, gain)
        self.assertIn(f'攻撃力が {gain}', output)

    def test_magic_growth_mp_and_magic_increase(self):
        m = Monster('Mage', hp=20, attack=5, defense=5, mp=10, growth_type=GROWTH_TYPE_MAGIC)
        start_mp = m.max_mp
        start_magic = m.magic
        buf = io.StringIO()
        with redirect_stdout(buf):
            m.level_up()
        output = buf.getvalue()
        gains = get_status_gains_magic(2)
        self.assertEqual(m.max_mp - start_mp, gains['mp'])
        self.assertEqual(m.magic - start_magic, gains['magic'])
        self.assertIn(f'最大MPが {gains["mp"]}', output)
        self.assertIn(f'魔力が {gains["magic"]}', output)

    def test_defense_growth_defense_increase(self):
        m = Monster('Tank', hp=20, attack=5, defense=5, mp=10, growth_type=GROWTH_TYPE_DEFENSE)
        start_def = m.defense
        buf = io.StringIO()
        with redirect_stdout(buf):
            m.level_up()
        output = buf.getvalue()
        gain = get_status_gains_defense(2)['defense']
        self.assertEqual(m.defense - start_def, gain)
        self.assertIn(f'防御力が {gain}', output)

    def test_speed_growth_speed_increase(self):
        m = Monster('Swift', hp=20, attack=5, defense=5, mp=10, growth_type=GROWTH_TYPE_SPEED)
        start_speed = m.speed
        buf = io.StringIO()
        with redirect_stdout(buf):
            m.level_up()
        output = buf.getvalue()
        gain = get_status_gains_speed(2)['speed']
        self.assertEqual(m.speed - start_speed, gain)
        self.assertIn(f'素早さが {gain}', output)

if __name__ == '__main__':
    unittest.main()
