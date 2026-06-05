"""装備で会心率・回避率・魔防・魔力が付与されること（ドロップ・称号）のテスト。"""

import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.equipment import (
    EquipmentInstance, ALL_EQUIPMENT, RANDOM_STAT_CONFIG, CRAFTING_RECIPES,
)
from monster_rpg.items.titles import TITLE_GUARDIANS, TITLE_SAGES

NEW_ITEMS = ['keen_blade', 'warding_robe', 'drifter_cloak', 'rune_amulet']


def _base():
    return next(iter(ALL_EQUIPMENT.values()))


class TitleStatTests(unittest.TestCase):
    def test_guardians_title_grants_magic_defense(self):
        m = Monster('M', hp=20, attack=8, defense=10, speed=5)
        before = m.magic_defense
        m.equip(EquipmentInstance(base_item=_base(), title=TITLE_GUARDIANS))
        self.assertEqual(m.magic_defense - before, 5)   # 守護の: 魔防+5

    def test_sages_title_grants_magic(self):
        m = Monster('M', hp=20, attack=8, defense=10, speed=5, magic=10)
        m.equip(EquipmentInstance(base_item=_base(), title=TITLE_SAGES))
        self.assertEqual(m.magic, 15)                   # 賢者の: 魔力+5


class RandomDropPoolTests(unittest.TestCase):
    def _sub_stats(self, category):
        pools = RANDOM_STAT_CONFIG['random_stat_pools_by_category'][category]
        return {e['stat'] for e in pools['sub_stat_pool']}

    def test_weapon_can_roll_crit_and_magic(self):
        subs = self._sub_stats('weapon')
        self.assertIn('critical_rate', subs)
        self.assertIn('magic', subs)

    def test_armor_can_roll_magic_defense_and_evasion(self):
        subs = self._sub_stats('armor')
        self.assertIn('magic_defense', subs)
        self.assertIn('evasion_rate', subs)


class RandomBonusAppliesTests(unittest.TestCase):
    def test_random_magic_defense_sub_stat_is_read(self):
        # 副ステに magic_defense を持つ装備を直接組み、Monster が読むことを確認
        inst = EquipmentInstance(
            base_item=_base(),
            title=None,
            random_bonuses={'sub_stats': [{'stat': 'magic_defense', 'amount': 12}]},
        )
        m = Monster('M', hp=20, attack=8, defense=10, speed=5)
        before = m.magic_defense
        m.equip(inst)
        self.assertEqual(m.magic_defense - before, 12)


class NewStatItemTests(unittest.TestCase):
    def test_items_registered_with_expected_stats(self):
        for eid in NEW_ITEMS:
            self.assertIn(eid, ALL_EQUIPMENT)
        self.assertEqual(ALL_EQUIPMENT['keen_blade'].critical_rate, 10)
        self.assertEqual(ALL_EQUIPMENT['warding_robe'].magic_defense, 12)
        self.assertEqual(ALL_EQUIPMENT['drifter_cloak'].evasion_rate, 12)

    def test_base_item_stats_apply_when_equipped(self):
        m = Monster('M', hp=20, attack=8, defense=10, speed=5)
        before = m.critical_rate
        m.equip(EquipmentInstance(base_item=ALL_EQUIPMENT['keen_blade'], title=None))
        self.assertEqual(m.critical_rate - before, 10)

    def test_items_have_craft_recipes(self):
        for eid in NEW_ITEMS:
            self.assertIn(eid, CRAFTING_RECIPES)

    def test_items_sold_in_a_shop(self):
        from monster_rpg import map_data
        map_data.load_locations()
        sold = set()
        for loc in map_data.LOCATIONS.values():
            sold |= set(getattr(loc, 'shop_items', None) or {})
        for eid in NEW_ITEMS:
            self.assertIn(eid, sold)

    def test_can_buy_new_item(self):
        from monster_rpg import map_data
        from monster_rpg.services import shop_service
        from monster_rpg.player import Player
        map_data.load_locations()
        loc = next(l for l in map_data.LOCATIONS.values()
                   if 'keen_blade' in (getattr(l, 'shop_items', None) or {}))
        player = Player('Buyer')
        player.gold = 2000
        ok, _ = shop_service.buy_item(player, loc, 'keen_blade')
        self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()
