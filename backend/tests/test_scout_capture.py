"""スカウト（捕獲）の駆け引きと戦闘中アイテムのテスト。

- HPを削るほどスカウト成功率が上がる
- 行動不能系の状態異常でさらに上がる（その他の弱体でも少し上がる）
- 成功率には上限がある／scout_rate 0 や図鑑未登録種は常に 0
- 蘇生アイテムは倒れた味方にだけ使える
- 戦闘UIへ渡すアイテム一覧は戦闘で使える物だけ（元の位置 idx 付き）
"""
import unittest

from monster_rpg.battle import (
    Battle,
    scout_chance,
    SCOUT_CHANCE_CAP,
    SCOUT_BIND_STATUS_BONUS,
    SCOUT_DEBUFF_STATUS_BONUS,
    apply_status,
)
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.player import Player
from monster_rpg.items.item_data import ALL_ITEMS
from monster_rpg.services import battle_service


def make_slime(scout_rate=0.25):
    m = Monster('Slime', hp=100, attack=5, defense=2, monster_id='slime',
                scout_rate=scout_rate)
    return m


class ScoutChanceTests(unittest.TestCase):
    def test_full_hp_equals_base_rate(self):
        m = make_slime(0.25)
        self.assertAlmostEqual(scout_chance(m), 0.25)

    def test_chance_rises_as_hp_drops(self):
        m = make_slime(0.25)
        full = scout_chance(m)
        m.hp = 50
        half = scout_chance(m)
        m.hp = 1
        near_death = scout_chance(m)
        self.assertGreater(half, full)
        self.assertGreater(near_death, half)
        # 瀕死でおよそ3倍（HP1/100 → 倍率 1 + 2*0.99）
        self.assertAlmostEqual(near_death, 0.25 * (1.0 + 2.0 * 0.99), places=4)

    def test_bind_status_bonus(self):
        m = make_slime(0.25)
        base = scout_chance(m)
        apply_status(m, 'sleep')
        self.assertAlmostEqual(scout_chance(m), base * SCOUT_BIND_STATUS_BONUS)

    def test_debuff_status_bonus(self):
        m = make_slime(0.25)
        base = scout_chance(m)
        apply_status(m, 'poison')
        self.assertAlmostEqual(scout_chance(m), base * SCOUT_DEBUFF_STATUS_BONUS)

    def test_chance_is_capped(self):
        m = make_slime(0.9)
        m.hp = 1
        apply_status(m, 'sleep')
        self.assertEqual(scout_chance(m), SCOUT_CHANCE_CAP)

    def test_zero_rate_stays_zero(self):
        m = make_slime(0)
        m.hp = 1
        self.assertEqual(scout_chance(m), 0.0)

    def test_unregistered_species_is_zero(self):
        m = Monster('???', hp=100, attack=5, defense=2,
                    monster_id='not_in_dex', scout_rate=0.5)
        self.assertEqual(scout_chance(m), 0.0)


class BattleReviveItemTests(unittest.TestCase):
    def _battle_with_items(self, items):
        player = Player('Tester')
        hero = Monster('Hero', hp=50, attack=5, defense=2, speed=10, monster_id='slime')
        fallen = Monster('Fallen', hp=40, attack=5, defense=2, speed=8, monster_id='slime')
        fallen.hp = 0
        fallen.is_alive = False
        player.party_monsters.extend([hero, fallen])
        player.items.extend(items)
        enemy = Monster('Enemy', hp=30, attack=3, defense=1, monster_id='slime')
        battle = Battle(player.party_monsters, [enemy], player)
        battle.current_actor = hero
        return battle, fallen

    def test_revive_item_on_fainted_ally(self):
        battle, fallen = self._battle_with_items([ALL_ITEMS['revive_scroll']])
        battle.process_player_action({'type': 'item', 'item_idx': 0, 'target_ally': 1})
        self.assertTrue(fallen.is_alive)
        self.assertGreater(fallen.hp, 0)
        self.assertEqual(len(battle.player.items), 0)

    def test_revive_item_rejected_on_living_ally(self):
        battle, _ = self._battle_with_items([ALL_ITEMS['revive_scroll']])
        battle.process_player_action({'type': 'item', 'item_idx': 0, 'target_ally': 0})
        self.assertEqual(len(battle.player.items), 1)  # 消費されない

    def test_heal_item_rejected_on_fainted_ally(self):
        battle, fallen = self._battle_with_items([ALL_ITEMS['small_potion']])
        battle.process_player_action({'type': 'item', 'item_idx': 0, 'target_ally': 1})
        self.assertFalse(fallen.is_alive)
        self.assertEqual(len(battle.player.items), 1)


class BattleItemListTests(unittest.TestCase):
    def test_filters_to_battle_usable_with_original_index(self):
        player = Player('Tester')
        player.items.extend([
            ALL_ITEMS['magic_stone'],     # 素材（使用不可）
            ALL_ITEMS['small_potion'],    # 回復
            ALL_ITEMS['power_seed'],      # 種（戦闘外専用）
            ALL_ITEMS['revive_scroll'],   # 蘇生
        ])
        items = battle_service.battle_items(player)
        self.assertEqual([(it['name'], it['idx']) for it in items],
                         [('スモールポーション', 1), ('リバイブスクロール', 3)])
        targets = {it['name']: it['target'] for it in items}
        self.assertEqual(targets['スモールポーション'], 'ally')
        self.assertEqual(targets['リバイブスクロール'], 'fainted')

    def test_empty_for_no_player(self):
        self.assertEqual(battle_service.battle_items(None), [])


if __name__ == '__main__':
    unittest.main()
