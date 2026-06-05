"""ステータス画面に性格・才能・特性が表示されることのテスト。"""

import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg.web.utils import save_player
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.personality import IV_STATS


class StatusIndividualityTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_status_individuality.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        player = Player('Tester', user_id=self.user_id)
        mon = ALL_MONSTERS['slime'].copy()
        mon.personality_id = 'brave'              # ちからじまん
        mon.ivs = {s: 28 for s in IV_STATS}        # 比率 ~0.90 → 天才
        player.party_monsters.append(mon)
        save_player(player, self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_status_shows_personality_and_talent(self):
        resp = self.client.get(f'/status/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('ちからじまん', html)   # 性格
        self.assertIn('天才', html)            # 才能
        self.assertIn('ri-pers', html)         # 性格バッジが描画されている
        self.assertIn('ri-talent', html)       # 才能バッジが描画されている

    def test_common_talent_hidden_but_personality_shown(self):
        # 凡才（個体値0）は才能バッジを出さないが、性格は常に出る
        player = Player('Tester', user_id=self.user_id)
        mon = ALL_MONSTERS['slime'].copy()
        mon.personality_id = 'clever'             # かしこい
        mon.ivs = {s: 0 for s in IV_STATS}         # 凡才
        player.party_monsters = [mon]
        save_player(player, self.user_id)

        html = self.client.get(f'/status/{self.user_id}').get_data(as_text=True)
        self.assertIn('かしこい', html)        # 性格は出る
        self.assertNotIn('凡才', html)         # common はバッジを出さない


if __name__ == '__main__':
    unittest.main()
