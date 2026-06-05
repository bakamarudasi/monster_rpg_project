"""装備の能力表示（新ステ含む）とパーティ画面の回帰テスト。"""

import os
import json
import re
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.web.utils import save_player
from monster_rpg.player import Player
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.items.equipment import ALL_EQUIPMENT, EquipmentInstance, equipment_stat_summary


class EquipmentStatSummaryTests(unittest.TestCase):
    def test_summary_includes_new_stats(self):
        keys = {s['key'] for s in equipment_stat_summary(ALL_EQUIPMENT['keen_blade'])}
        self.assertIn('critical_rate', keys)
        robe = {s['key'] for s in equipment_stat_summary(ALL_EQUIPMENT['warding_robe'])}
        self.assertIn('magic_defense', robe)
        cloak = {s['key'] for s in equipment_stat_summary(ALL_EQUIPMENT['drifter_cloak'])}
        self.assertIn('evasion_rate', cloak)

    def test_zero_stats_omitted_and_percent_marked(self):
        summary = equipment_stat_summary(ALL_EQUIPMENT['keen_blade'])
        crit = next(s for s in summary if s['key'] == 'critical_rate')
        self.assertTrue(crit['display'].endswith('%'))
        # defense は keen_blade に無いので出ない
        self.assertNotIn('defense', {s['key'] for s in summary})


class PartyPageTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_equip_display.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        player.party_monsters = [ALL_MONSTERS['slime'].copy()]
        player.equipment_inventory = [
            EquipmentInstance(base_item=ALL_EQUIPMENT['keen_blade'], title=None),
            EquipmentInstance(base_item=ALL_EQUIPMENT['warding_robe'], title=None),
        ]
        save_player(player, self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _party_data(self):
        html = self.client.get(f'/party/{self.user_id}').get_data(as_text=True)
        return json.loads(re.search(r'id="party-data"[^>]*>(.*?)</script>', html, re.S).group(1))

    def test_party_page_renders(self):
        # 以前は url_for('appraise') で 500 になっていた回帰
        self.assertEqual(self.client.get(f'/party/{self.user_id}').status_code, 200)

    def test_equipment_list_exposes_stats(self):
        data = self._party_data()
        by_name = {e['name']: e for e in data['equipment_list']}
        keen = {s['key'] for s in by_name['鋭刃の剣']['stats']}
        self.assertIn('critical_rate', keen)

    def test_equip_response_includes_new_monster_stats(self):
        data = self._party_data()
        eqid = next(e['id'] for e in data['equipment_list'] if e['name'] == '鋭刃の剣')
        resp = self.client.post(f'/equip/{self.user_id}',
                                json={'equip_id': eqid, 'monster_idx': 0, 'slot': 'weapon'}).get_json()
        for key in ('magic', 'magic_defense', 'critical_rate', 'evasion_rate'):
            self.assertIn(key, resp['monster_stats'])
        self.assertEqual(resp['monster_stats']['critical_rate'], 10)   # 装備の会心が反映


if __name__ == '__main__':
    unittest.main()
