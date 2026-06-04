"""モンスターのロック（合成保護・永続化）のテスト。"""

import os
import unittest

from monster_rpg import database_setup, save_manager
from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.synthesis_manager import synthesize_monster


class LockGuardTests(unittest.TestCase):
    def test_synthesis_blocks_locked_parent(self):
        p = Player("A")
        a = ALL_MONSTERS["slime"].copy()
        a.locked = True
        b = ALL_MONSTERS["wolf"].copy()
        p.party_monsters = [a, b]
        ok, msg, _ = synthesize_monster(p, 0, 1)
        self.assertFalse(ok)
        self.assertIn("ロック", msg)
        self.assertEqual(len(p.party_monsters), 2)  # 素材は消費されない

    def test_synthesis_allowed_when_unlocked(self):
        p = Player("A")
        p.party_monsters = [ALL_MONSTERS["slime"].copy(), ALL_MONSTERS["wolf"].copy()]
        ok, _, child = synthesize_monster(p, 0, 1)
        self.assertTrue(ok)
        self.assertIsNotNone(child)


class LockPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.db = "test_lock.db"
        if os.path.exists(self.db):
            os.remove(self.db)
        database_setup.DATABASE_NAME = self.db
        database_setup.initialize_database()
        self.uid = database_setup.create_user("lk", "p")

    def tearDown(self):
        if os.path.exists(self.db):
            os.remove(self.db)

    def test_lock_survives_save_load(self):
        p = Player("A", user_id=self.uid)
        locked = ALL_MONSTERS["dragon_pup"].copy()
        locked.locked = True
        p.party_monsters.append(locked)
        p.reserve_monsters.append(ALL_MONSTERS["slime"].copy())  # 未ロック
        save_manager.save_game(p, self.db, user_id=self.uid)

        loaded = save_manager.load_game(self.db, user_id=self.uid)
        self.assertTrue(loaded.party_monsters[0].locked)
        self.assertFalse(loaded.reserve_monsters[0].locked)


if __name__ == "__main__":
    unittest.main()
