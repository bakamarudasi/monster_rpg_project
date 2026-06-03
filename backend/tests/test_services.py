"""サービス層（shop / equipment / synthesis）のユニットテスト。

HTTP を介さず Player と各サービス関数を直接呼び、(success, message) 契約と
副作用（所持金・在庫・パーティ）を検証する。永続化はサービスの責務外なので DB 不要。
"""

import types
import unittest

from monster_rpg.player import Player
from monster_rpg.items.equipment import EquipmentInstance, BRONZE_SWORD
from monster_rpg.items.item_data import ALL_ITEMS
from monster_rpg.services import shop_service, equipment_service, synthesis_service


def _loc(**kw):
    """shop_service が参照する最小の Location スタブ。"""
    base = dict(shop_items={}, shop_monsters={}, inn_cost=10)
    base.update(kw)
    return types.SimpleNamespace(**base)


class ShopServiceTests(unittest.TestCase):
    def test_buy_item_success_returns_real_message(self):
        p = Player('S'); p.gold = 500
        ok, msg = shop_service.buy_item(p, _loc(shop_items={'elixir': 300}), 'elixir')
        self.assertTrue(ok)
        self.assertIn('エリクサー', msg)        # ダミーでなく実アイテム名
        self.assertEqual(p.gold, 200)
        self.assertEqual(len(p.items), 1)

    def test_buy_item_not_sold_here(self):
        p = Player('S'); p.gold = 500
        ok, msg = shop_service.buy_item(p, _loc(shop_items={}), 'elixir')
        self.assertFalse(ok)
        self.assertEqual(p.gold, 500)
        self.assertEqual(msg, '購入できなかった。')

    def test_buy_item_insufficient_gold(self):
        p = Player('S'); p.gold = 10
        ok, _ = shop_service.buy_item(p, _loc(shop_items={'elixir': 300}), 'elixir')
        self.assertFalse(ok)
        self.assertEqual(p.gold, 10)
        self.assertEqual(len(p.items), 0)

    def test_buy_monster_success(self):
        p = Player('S'); p.gold = 500
        ok, _ = shop_service.buy_monster(p, _loc(shop_monsters={'slime': 100}), 'slime')
        self.assertTrue(ok)
        self.assertEqual(len(p.party_monsters), 1)
        self.assertEqual(p.gold, 400)

    def test_rest_at_inn_heals_and_charges(self):
        p = Player('S'); p.gold = 100
        p.add_monster_to_party('slime'); p.party_monsters[0].hp = 1
        ok, _ = shop_service.rest_at_inn(p, _loc(inn_cost=60))
        self.assertTrue(ok)
        self.assertEqual(p.gold, 40)
        self.assertEqual(p.party_monsters[0].hp, p.party_monsters[0].max_hp)

    def test_rest_at_inn_insufficient_gold(self):
        p = Player('S'); p.gold = 10
        ok, msg = shop_service.rest_at_inn(p, _loc(inn_cost=60))
        self.assertFalse(ok)
        self.assertEqual(p.gold, 10)
        self.assertEqual(msg, 'お金が足りない。')


class EquipmentServiceTests(unittest.TestCase):
    def _player_with_sword(self):
        p = Player('E')
        equip = EquipmentInstance(base_item=BRONZE_SWORD, title=None)
        p.equipment_inventory.append(equip)
        return p, equip

    def test_equip_returns_view_data(self):
        p, equip = self._player_with_sword()
        p.add_monster_to_party('slime')
        ok, data = equipment_service.equip(p, 0, equip.instance_id, 'weapon')
        self.assertTrue(ok)
        self.assertEqual(set(data), {'equipment_inventory', 'monster_equipment', 'monster_stats'})
        self.assertEqual(set(data['monster_stats']), {'attack', 'defense', 'speed'})
        self.assertEqual(len(data['equipment_inventory']), 0)   # 在庫から外れた
        self.assertTrue(data['monster_equipment'])               # モンスターに装着

    def test_disassemble_returns_real_message_and_material(self):
        p, equip = self._player_with_sword()
        ok, msg = equipment_service.disassemble(p, equip.instance_id)
        self.assertTrue(ok)
        self.assertIn('分解', msg)                                # 実メッセージ
        self.assertEqual(len(p.equipment_inventory), 0)
        self.assertEqual(len(p.items), 1)

    def test_disassemble_unknown_id(self):
        p, _ = self._player_with_sword()
        ok, msg = equipment_service.disassemble(p, 'no-such-id')
        self.assertFalse(ok)
        self.assertEqual(msg, 'その装備を所持していない。')
        self.assertEqual(len(p.equipment_inventory), 1)           # 在庫は無傷

    def test_limit_break_without_material_fails(self):
        p, equip = self._player_with_sword()
        ok, msg = equipment_service.limit_break(p, equip.instance_id)
        self.assertFalse(ok)
        self.assertEqual(msg, '素材が足りない。')

    def test_enhance_entries_shape(self):
        p, equip = self._player_with_sword()
        entries = equipment_service.enhance_entries(p)
        self.assertEqual(len(entries), 1)
        e = entries[0]
        for key in ('instance_id', 'name', 'slot', 'level', 'maxed', 'cost', 'material', 'rank'):
            self.assertIn(key, e)
        self.assertEqual(e['instance_id'], equip.instance_id)


class SynthesisServiceTests(unittest.TestCase):
    def test_invalid_types_is_validation_error(self):
        p = Player('Y')
        outcome = synthesis_service.perform_synthesis(p, {
            'base_type': 'x', 'base_id': 'a', 'material_type': 'y', 'material_id': 'b',
        })
        self.assertFalse(outcome.success)
        self.assertTrue(outcome.is_validation_error)
        self.assertEqual(outcome.to_dict(), {'success': False, 'error': 'invalid types'})

    def test_item_item_synthesis_returns_equipment(self):
        p = Player('Y')
        p.items.append(ALL_ITEMS['magic_stone'])
        p.items.append(ALL_ITEMS['dragon_scale'])
        outcome = synthesis_service.perform_synthesis(p, {
            'base_type': 'item', 'base_id': 'magic_stone',
            'material_type': 'item', 'material_id': 'dragon_scale',
        })
        self.assertTrue(outcome.success)
        self.assertEqual(outcome.result_type, 'equipment')
        self.assertTrue(outcome.to_dict()['success'])

    def test_preview_invalid_index(self):
        p = Player('Y')
        preview, err = synthesis_service.preview_synthesis(p, {'base_id': 'a', 'material_id': 'b'})
        self.assertEqual(err, 'invalid index')
        self.assertIsNone(preview)


if __name__ == '__main__':
    unittest.main()
