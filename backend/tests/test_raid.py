import unittest
from types import SimpleNamespace

from monster_rpg.exploration import get_monster_instance_copy
from monster_rpg.services import raid_service
from monster_rpg.raid_data import RAID_BOSSES, RAID_MONSTERS, get_raid
from monster_rpg.items.equipment import Equipment, ALL_EQUIPMENT


def _player_with(n):
    mons = []
    for mid in ['slime', 'goblin', 'bat', 'wolf', 'dragon_pup',
                'phoenix_chick', 'orc_warrior', 'skeleton_archer',
                'elf_mage', 'imp', 'kraken', 'giant_golem'][:n]:
        m = get_monster_instance_copy(mid)
        if m:
            mons.append(m)
    return SimpleNamespace(party_monsters=mons[:3], reserve_monsters=mons[3:],
                           story_flags=set(), gold=0)


class RaidServiceTests(unittest.TestCase):
    def test_raid_bosses_are_dedicated_monsters(self):
        """レイドボスは専用レジストリの新モンスターで、ALL_MONSTERS には載らない。"""
        from monster_rpg.monsters import ALL_MONSTERS
        for defn in RAID_BOSSES:
            self.assertIn(defn['monster_id'], RAID_MONSTERS)
            self.assertNotIn(defn['monster_id'], ALL_MONSTERS)

    def test_all_bosses_build_with_high_hp_and_drops(self):
        for defn in RAID_BOSSES:
            boss = raid_service.build_raid_boss(defn)
            self.assertIsNotNone(boss, f"boss {defn['id']} failed to build")
            self.assertTrue(boss.is_boss)
            self.assertEqual(boss.hp, boss.max_hp)
            self.assertGreater(boss.max_hp, 1000)
            # レイド限定装備がドロップ表に含まれる
            drop_equip = [it for it, _ in boss.drop_items if isinstance(it, Equipment)]
            self.assertTrue(drop_equip, f"boss {defn['id']} has no equipment drop")

    def test_raid_equipment_registered(self):
        for eid in ('infernal_fang', 'abyssal_trident', 'celestial_aegis'):
            self.assertIn(eid, ALL_EQUIPMENT)

    def test_start_raid_nine_vs_one(self):
        player = _player_with(12)
        battle, err = raid_service.start_raid(player, 'celestial', list(range(9)))
        self.assertIsNone(err)
        self.assertEqual(len(battle.player_party), 9)
        self.assertEqual(len(battle.enemy_party), 1)
        self.assertTrue(battle.is_raid)
        self.assertEqual(battle.raid_id, 'celestial')

    def test_start_raid_clamps_to_max(self):
        player = _player_with(12)
        battle, err = raid_service.start_raid(player, 'ashen', list(range(12)))
        self.assertIsNone(err)
        self.assertEqual(len(battle.player_party), raid_service.MAX_RAID_PARTY)

    def test_start_raid_full_heals_members(self):
        player = _player_with(5)
        for m in player.party_monsters:
            m.hp = 1
        battle, err = raid_service.start_raid(player, 'ashen', [0, 1, 2])
        self.assertIsNone(err)
        for m in battle.player_party:
            self.assertEqual(m.hp, m.max_hp)

    def test_empty_selection_errors(self):
        player = _player_with(5)
        battle, err = raid_service.start_raid(player, 'ashen', [])
        self.assertIsNone(battle)
        self.assertIsNotNone(err)

    def test_unknown_raid_errors(self):
        player = _player_with(5)
        battle, err = raid_service.start_raid(player, 'nope', [0])
        self.assertIsNone(battle)
        self.assertIsNotNone(err)

    def test_get_raid(self):
        self.assertIsNotNone(get_raid('ashen'))
        self.assertIsNone(get_raid('does_not_exist'))

    def test_phase_triggers_on_hp_threshold(self):
        player = _player_with(3)
        battle, err = raid_service.start_raid(player, 'ashen', [0, 1, 2])
        self.assertIsNone(err)
        boss = battle.enemy_party[0]
        base_atk = boss.base_attack
        # 満タンでは発動しない
        raid_service.check_phases(battle)
        self.assertEqual(boss._raid_phase_done, 0)
        # HPを49%に → 50%フェーズ発動（攻撃強化＋ログ）
        boss.hp = int(boss.max_hp * 0.49)
        n_before = len(battle.log)
        raid_service.check_phases(battle)
        self.assertEqual(boss._raid_phase_done, 1)
        self.assertGreater(boss.base_attack, base_atk)
        self.assertTrue(any(e['type'] == 'boss' for e in battle.log[n_before:]))
        # 再呼び出しでは重複発動しない
        atk_after = boss.base_attack
        raid_service.check_phases(battle)
        self.assertEqual(boss.base_attack, atk_after)

    def test_ultimate_requires_sacrifices(self):
        from monster_rpg.items.item_data import ALL_ITEMS
        player = _player_with(3)
        player.items = []
        # 魂なし → 召喚失敗
        battle, err = raid_service.start_raid(player, 'omega', [0, 1, 2])
        self.assertIsNone(battle)
        self.assertIn('生贄', err)
        # 3つの魂を持たせる → 召喚成功＆消費される
        for sid in ('soul_ashen', 'soul_kraken', 'soul_celestial'):
            player.items.append(ALL_ITEMS[sid])
        battle, err = raid_service.start_raid(player, 'omega', [0, 1, 2])
        self.assertIsNone(err)
        self.assertEqual(len(battle.enemy_party), 1)
        self.assertEqual(battle.enemy_party[0].level, 99)
        # 魂は消費されている
        remaining = {getattr(it, 'item_id', None) for it in player.items}
        self.assertNotIn('soul_ashen', remaining)
        self.assertNotIn('soul_kraken', remaining)
        self.assertNotIn('soul_celestial', remaining)

    def test_base_raids_drop_souls(self):
        from monster_rpg.items.item_data import Item
        for rid, sid in (('ashen', 'soul_ashen'), ('kraken', 'soul_kraken'), ('celestial', 'soul_celestial')):
            defn = get_raid(rid)
            boss = raid_service.build_raid_boss(defn)
            soul_drops = [it for it, rate in boss.drop_items
                          if isinstance(it, Item) and it.item_id == sid and rate >= 1.0]
            self.assertTrue(soul_drops, f"{rid} should guarantee-drop {sid}")

    def test_phase_heal(self):
        player = _player_with(3)
        battle, _ = raid_service.start_raid(player, 'kraken', [0, 1, 2])
        boss = battle.enemy_party[0]
        boss.hp = int(boss.max_hp * 0.49)  # 50%フェーズに heal:0.15 がある
        raid_service.check_phases(battle)
        self.assertGreater(boss.hp, int(boss.max_hp * 0.49))


if __name__ == '__main__':
    unittest.main()
