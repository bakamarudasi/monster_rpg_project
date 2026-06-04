"""新規追加した「魔王枠」S級モンスターの検証。

- 合成レシピで正しく生成されること
- S級でボスAI（skill_sequence）を持つこと
- 進化では到達できない＝プレステージ（合成限定）であること
"""

import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.evolution_rules import EVOLUTION_RULES, get_evolution_branches
from monster_rpg.synthesis_manager import resolve_synthesis_result
from monster_rpg.skills.skills import ALL_SKILLS


DEMON_LORDS = {
    ("storm_djinn", "thunderlord_roc"): "storm_sovereign",
    ("iron_juggernaut", "obsidian_titan"): "gaia_colossus",
    ("blighted_knight", "venom_naga"): "plague_monarch",
    ("coral_hydra", "void_leviathan"): "abyssal_tide_king",
    ("nameless_kingling", "thunderlord_roc"): "thunder_emperor",
}

SIGNATURE_SKILLS = ["tempest_judgment", "continental_crush", "pandemic", "maelstrom", "ragnarok_bolt"]


class DemonLordTests(unittest.TestCase):
    def test_all_exist(self):
        for mid in DEMON_LORDS.values():
            self.assertIn(mid, ALL_MONSTERS)
        for sid in SIGNATURE_SKILLS:
            self.assertIn(sid, ALL_SKILLS)

    def test_recipes_produce_demon_lords(self):
        for (a, b), expected in DEMON_LORDS.items():
            res, _ = resolve_synthesis_result(ALL_MONSTERS[a], ALL_MONSTERS[b])
            self.assertEqual(res, expected, f"{a}+{b}")

    def test_are_s_rank_bosses(self):
        for mid in DEMON_LORDS.values():
            m = ALL_MONSTERS[mid]
            self.assertEqual(m.rank, "S")
            self.assertTrue(m.skill_sequence, f"{mid} はボス台本を持つべき")

    def test_not_reachable_by_evolution(self):
        targets = set()
        for src in EVOLUTION_RULES:
            for br in get_evolution_branches(src):
                targets.add(br.get("evolves_to"))
                targets.add(br.get("awaken_into"))
        for mid in DEMON_LORDS.values():
            self.assertNotIn(mid, targets, f"{mid} は進化で到達できてはいけない")

    def test_fill_missing_elements(self):
        # 風/土/毒/水/雷 のS級が埋まった
        elems = {ALL_MONSTERS[mid].element for mid in DEMON_LORDS.values()}
        self.assertEqual(elems, {"風", "土", "毒", "水", "雷"})


if __name__ == "__main__":
    unittest.main()
