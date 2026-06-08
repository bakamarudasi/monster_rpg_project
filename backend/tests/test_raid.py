import unittest
from types import SimpleNamespace

from monster_rpg.exploration import get_monster_instance_copy
from monster_rpg.services import raid_service
from monster_rpg.raid_data import RAID_BOSSES, get_raid


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
    def test_all_bosses_build_with_high_hp(self):
        for defn in RAID_BOSSES:
            boss = raid_service.build_raid_boss(defn)
            self.assertIsNotNone(boss, f"boss {defn['id']} failed to build")
            self.assertTrue(boss.is_boss)
            self.assertEqual(boss.hp, boss.max_hp)
            # 強化倍率がかかって元テンプレより高HPであること
            base = get_monster_instance_copy(defn['base'])
            self.assertGreater(boss.max_hp, base.max_hp)

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
        # わざとダメージ状態にする
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


if __name__ == '__main__':
    unittest.main()
