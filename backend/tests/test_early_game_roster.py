"""序盤ロスター拡充の検証。

- 新序盤モンスターは低ランク(E/D)
- それぞれ序盤エリア(avg_lv<=5)に出現する
- 低ランク総数が十分（序盤の単調さ対策）
"""

import json
import os
import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS

NEW_EARLY = ["cinder_kit", "dawn_chick", "breeze_sprite", "bubble_jelly", "frost_pixie",
             "thunder_pup", "venom_spider", "shade_imp", "lumen_moth", "pebble_knight"]

_LOC_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "monster_rpg", "map", "locations.json")


class EarlyGameRosterTests(unittest.TestCase):
    def setUp(self):
        with open(_LOC_PATH, encoding="utf-8") as f:
            self.locations = json.load(f)

    def test_new_monsters_are_low_rank(self):
        for mid in NEW_EARLY:
            self.assertIn(ALL_MONSTERS[mid].rank, ("E", "D"), mid)

    def test_each_new_monster_in_early_area(self):
        early = set()
        for loc in self.locations.values():
            if loc.get("avg_enemy_level", 99) <= 5:
                early.update(loc.get("enemy_pool") or {})
        for mid in NEW_EARLY:
            self.assertIn(mid, early, f"{mid} は序盤エリアに出現すべき")

    def test_low_rank_pool_is_healthy(self):
        low = [m for m in ALL_MONSTERS.values() if m.rank in ("E", "D")]
        self.assertGreaterEqual(len(low), 20, "序盤(E/D)の層が薄い")

    def test_new_monsters_have_own_art_filename(self):
        for mid in NEW_EARLY:
            self.assertEqual(ALL_MONSTERS[mid].image_filename, f"{mid}.png")


if __name__ == "__main__":
    unittest.main()
