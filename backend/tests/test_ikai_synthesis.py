"""位階配合（DQM準拠の汎用フォールバック）のテスト。

レシピにも家系ルールにも当たらない任意の2体が必ず配合でき、＋値を伸ばせること、
通常配合の天井がA止まりであること、候補選択（result_choice）が効くことを担保する。
"""

import unittest
from unittest.mock import patch

from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.synthesis_rules import (
    RANK_VALUES,
    GENERIC_MAX_RANK_VALUE,
    synthesis_candidates,
    family_ladder,
)


def _rv(rank):
    return RANK_VALUES.get(str(rank).upper(), 0)


# 乱数（大当たり/レア抽選）が結果種族を上書きしないよう固定する
def _no_random():
    return patch('monster_rpg.synthesis_manager.random.random', return_value=0.99)


class IkaiSynthesisTests(unittest.TestCase):
    def test_non_recipe_pair_now_breeds(self):
        """レシピも家系ルールも無い組み合わせ（以前は「何も生まれない」）が配合できる。"""
        p = Player('T')
        p.add_monster_to_party('wolf')             # beast / C
        p.add_monster_to_party('skeleton_archer')  # undead / C
        with _no_random():
            ok, _msg, child = p.synthesize_monster(0, 1)
        self.assertTrue(ok)
        self.assertIsNotNone(child)

    def test_plus_value_accrues_on_generic_breeding(self):
        """＋値はレシピの有無に関わらず振れる（ユーザー要件の核）。"""
        p = Player('T')
        p.add_monster_to_party('wolf')
        p.add_monster_to_party('skeleton_archer')
        with _no_random():
            ok, _msg, child = p.synthesize_monster(0, 1)
        self.assertTrue(ok)
        self.assertGreaterEqual(child.plus_value, 1)

    def test_result_choice_is_respected(self):
        """位階配合では候補の中からプレイヤーが結果を選べる。"""
        _key, cands = synthesis_candidates(
            ALL_MONSTERS['wolf'], ALL_MONSTERS['skeleton_archer']
        )
        self.assertIn('wraith_knight', cands)  # undead 系統で1つ上
        p = Player('T')
        p.add_monster_to_party('wolf')
        p.add_monster_to_party('skeleton_archer')
        with _no_random():
            ok, _msg, child = p.synthesize_monster(0, 1, result_choice='wraith_knight')
        self.assertTrue(ok)
        self.assertEqual(child.monster_id, 'wraith_knight')

    def test_generic_breeding_caps_at_A(self):
        """サブA級どうしの通常配合はS級を生まない（位階の天井＝A）。"""
        recipe_key, cands = synthesis_candidates(
            ALL_MONSTERS['thunder_eagle'], ALL_MONSTERS['obsidian_gargoyle']  # both A, no recipe
        )
        self.assertIsNone(recipe_key)
        for cid in cands:
            self.assertLessEqual(_rv(ALL_MONSTERS[cid].rank), GENERIC_MAX_RANK_VALUE)

    def test_family_ladder_excludes_S(self):
        """どの系統の位階ラダーにもS級は含まれない（通常配合で昇れない）。"""
        for fam in {m.family for m in ALL_MONSTERS.values() if m.family}:
            for t in family_ladder(fam):
                self.assertLessEqual(_rv(t.rank), GENERIC_MAX_RANK_VALUE)

    def test_existing_recipe_still_overrides(self):
        """既存の特殊レシピは位階配合に優先（単一結果・選択不可）。"""
        recipe_key, cands = synthesis_candidates(
            ALL_MONSTERS['slime'], ALL_MONSTERS['wolf']
        )
        self.assertIsNotNone(recipe_key)
        self.assertEqual(cands, ['water_wolf'])

    def test_preview_exposes_selectable_candidates(self):
        """preview が候補一覧と選択可フラグを返す。"""
        p = Player('T')
        p.add_monster_to_party('wolf')
        p.add_monster_to_party('skeleton_archer')
        pv = p.preview_synthesis(0, 1)
        self.assertTrue(pv['ok'])
        self.assertTrue(pv['selectable'])
        ids = [c['id'] for c in pv['candidates']]
        self.assertIn('wraith_knight', ids)


if __name__ == '__main__':
    unittest.main()
