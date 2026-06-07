"""会心率・回避率（死にステの実装）と会心の個体差のテスト。"""

import unittest
from unittest.mock import patch

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.monsters.personality import IV_STATS
from monster_rpg.items.equipment import EquipmentInstance, ALL_EQUIPMENT
from monster_rpg.items.titles import TITLE_ASSASSINS, TITLE_NIMBLE
from monster_rpg import battle


def _base_equip():
    return next(iter(ALL_EQUIPMENT.values()))


class CriticalRateTests(unittest.TestCase):
    def test_scales_with_speed_and_talent(self):
        slow = Monster('Slow', hp=30, attack=10, defense=3, speed=10)
        fast = Monster('Fast', hp=30, attack=10, defense=3, speed=160)
        fast.ivs = {s: 31 for s in IV_STATS}   # 鬼才
        self.assertEqual(slow.critical_rate, 0)
        self.assertGreater(fast.critical_rate, slow.critical_rate)

    def test_equipment_critical_rate_is_read(self):
        m = Monster('Geared', hp=30, attack=10, defense=3, speed=10)
        before = m.critical_rate
        m.equip(EquipmentInstance(base_item=_base_equip(), title=TITLE_ASSASSINS))
        self.assertEqual(m.critical_rate - before, 5)   # 暗殺者の: 会心+5

    def test_critical_applies_in_damage(self):
        atk = Monster('A', hp=10, attack=30, defense=1)
        target = Monster('T', hp=999, attack=1, defense=10)
        # 回避率0なので random は会心判定の1回だけ。0.0 → 必ず会心。
        with patch('monster_rpg.battle.random.random', return_value=0.0):
            dmg = battle.calculate_damage(atk, target, [])
        base = max(1, atk.total_attack() - target.total_defense())
        self.assertEqual(dmg, base * battle.CRITICAL_HIT_MULTIPLIER)


class EvasionRateTests(unittest.TestCase):
    def test_equipment_evasion_rate_is_read(self):
        m = Monster('Geared', hp=30, attack=10, defense=3, speed=10)
        m.equip(EquipmentInstance(base_item=_base_equip(), title=TITLE_NIMBLE))
        self.assertEqual(m.evasion_rate, 5)             # 身かわしの: 回避+5

    def test_evasion_causes_miss(self):
        atk = Monster('A', hp=10, attack=30, defense=1)
        dodger = Monster('D', hp=999, attack=1, defense=1)
        dodger._stat_bonuses['evasion_rate'] = 50
        with patch('monster_rpg.battle.random.random', return_value=0.0):
            dmg = battle.calculate_damage(atk, dodger, [])
        self.assertEqual(dmg, 0)                         # 回避成立

    def test_no_evasion_by_default_hits(self):
        atk = Monster('A', hp=10, attack=30, defense=1)
        target = Monster('T', hp=999, attack=1, defense=1)
        self.assertEqual(target.evasion_rate, 0)
        with patch('monster_rpg.battle.random.random', return_value=0.99):
            dmg = battle.calculate_damage(atk, target, [])
        self.assertGreater(dmg, 0)                       # 既定は必中


if __name__ == '__main__':
    unittest.main()
