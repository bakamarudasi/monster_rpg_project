"""ロスター全体の整合性ガード（リグレッション防止）。

- すべてのモンスターに図鑑の説明文(description)がある
- 進化先・出現プールの参照が全て実在する
- 中盤追加モンスターが想定どおり配置されている
"""

import json
import os
import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA
from monster_rpg.monsters.evolution_rules import EVOLUTION_RULES, get_evolution_branches

_LOC_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "monster_rpg", "map", "locations.json")
MID_BATCH = ["gust_wisp", "tempest_hawk", "granite_ogre", "dust_djinn", "flame_imp",
             "magma_serpent", "wraith_knight", "bone_drake", "reef_guardian", "glacier_pixie"]


class RosterIntegrityTests(unittest.TestCase):
    def test_every_monster_has_description(self):
        missing = [mid for mid in ALL_MONSTERS
                   if not (MONSTER_BOOK_DATA.get(mid) and (MONSTER_BOOK_DATA[mid].description or "").strip())]
        self.assertEqual(missing, [], f"説明文が無いモンスター: {missing}")

    def test_evolution_targets_exist(self):
        bad = []
        for src in EVOLUTION_RULES:
            for br in get_evolution_branches(src):
                for t in (br.get("evolves_to"), br.get("awaken_into")):
                    if t and t not in ALL_MONSTERS:
                        bad.append((src, t))
        self.assertEqual(bad, [], f"進化先が存在しない: {bad}")

    def test_enemy_pool_references_exist(self):
        with open(_LOC_PATH, encoding="utf-8") as f:
            locations = json.load(f)
        bad = []
        for k, v in locations.items():
            for mid in (v.get("enemy_pool") or {}):
                if mid not in ALL_MONSTERS:
                    bad.append((k, mid))
        self.assertEqual(bad, [], f"出現プールに不明なモンスター: {bad}")

    def test_mid_batch_is_mid_rank_and_placed(self):
        with open(_LOC_PATH, encoding="utf-8") as f:
            locations = json.load(f)
        placed = set()
        for v in locations.values():
            placed.update(v.get("enemy_pool") or {})
        for mid in MID_BATCH:
            self.assertIn(ALL_MONSTERS[mid].rank, ("C", "B"), mid)
            self.assertIn(mid, placed, f"{mid} がどのエリアにも配置されていない")


if __name__ == "__main__":
    unittest.main()
