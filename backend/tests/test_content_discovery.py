"""コンテンツ発見性のテスト。

- 魔王枠が終盤エリアにボスとして出現する（＝目撃され図鑑に載る）
- 魔王枠は捕獲不可（scout_rate 0）＝合成でしか手に入らないプレステージ
- ショップで装備が買える（新装備の入手導線）
"""

import json
import os
import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.player import Player
from monster_rpg.items.equipment import EquipmentInstance

DEMON_LORDS = ["storm_sovereign", "gaia_colossus", "plague_monarch",
               "abyssal_tide_king", "thunder_emperor"]

_LOC_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "monster_rpg", "map", "locations.json")


class ContentDiscoveryTests(unittest.TestCase):
    def setUp(self):
        with open(_LOC_PATH, encoding="utf-8") as f:
            self.locations = json.load(f)

    def test_demon_lords_appear_as_bosses(self):
        placed = set()
        for loc in self.locations.values():
            for mid in (loc.get("enemy_pool") or {}):
                if mid in DEMON_LORDS:
                    placed.add(mid)
        for mid in DEMON_LORDS:
            self.assertIn(mid, placed, f"{mid} はどこかのエリアに出現して発見されるべき")

    def test_demon_lords_placed_in_endgame_only(self):
        # 魔王枠は高レベル帯(>=13)のエリアにのみ配置（序盤に弱体で湧かない）
        for loc in self.locations.values():
            lv = loc.get("avg_enemy_level", 0)
            for mid in (loc.get("enemy_pool") or {}):
                if mid in DEMON_LORDS:
                    self.assertGreaterEqual(lv, 13, f"{mid} が低レベル帯に配置されている")

    def test_demon_lords_uncatchable(self):
        for mid in DEMON_LORDS:
            self.assertEqual(ALL_MONSTERS[mid].scout_rate, 0)

    def test_demon_lords_have_own_image_filename(self):
        for mid in DEMON_LORDS:
            self.assertEqual(ALL_MONSTERS[mid].image_filename, f"{mid}.png")

    def test_shop_sells_equipment(self):
        p = Player("Shopper")
        p.gold = 9999
        self.assertTrue(p.buy_item("aegis_shield", 1200))
        bought = [e for e in p.equipment_inventory
                  if isinstance(e, EquipmentInstance) and e.base_item.equip_id == "aegis_shield"]
        self.assertTrue(bought, "守護の大盾がショップ購入で手に入るべき")


if __name__ == "__main__":
    unittest.main()
