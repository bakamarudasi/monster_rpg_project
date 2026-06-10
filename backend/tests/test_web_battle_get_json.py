import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app, Battle, active_battles
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster

class BattleGetJsonTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_web.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        hero = Monster('Hero', hp=20, attack=5, defense=2)
        player.party_monsters.append(hero)
        enemy = Monster('Slime', hp=10, attack=3, defense=1)
        battle_obj = Battle(player.party_monsters, [enemy], player)
        active_battles[self.user_id] = battle_obj

    def tearDown(self):
        active_battles.pop(self.user_id, None)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_get_returns_json(self):
        resp = self.client.get(f'/battle-json/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('hp_values', data)
        self.assertIn('status_effects', data['hp_values']['player'][0])
        self.assertIn('status_effects', data['hp_values']['enemy'][0])
        self.assertIn('log', data)
        self.assertIn('finished', data)
        self.assertIn('current_actor', data)
        if data['current_actor']:
            self.assertIn('skills', data['current_actor'])

    def test_get_returns_items(self):
        """JSON応答に戦闘で使えるアイテムが含まれる（アイテムタブが消えない回帰防止）。

        素材など戦闘で使えない物は除外され、使える物は元のインベントリ位置
        （idx）付きで返る。
        """
        from monster_rpg.items.item_data import ALL_ITEMS
        player = active_battles[self.user_id].player
        player.items.append(ALL_ITEMS['magic_stone'])    # 素材 → 除外される
        player.items.append(ALL_ITEMS['small_potion'])   # 回復 → 含まれる
        resp = self.client.get(f'/battle-json/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('items', data)
        potion = next((it for it in data['items'] if it.get('name') == 'スモールポーション'), None)
        self.assertIsNotNone(potion)
        self.assertEqual(potion['idx'], 1)
        self.assertFalse(any(it.get('name') == '魔石' for it in data['items']))

    def test_get_returns_404_without_active_battle(self):
        active_battles.pop(self.user_id, None)
        resp = self.client.get(f'/battle-json/{self.user_id}')
        self.assertEqual(resp.status_code, 404)
        data = resp.get_json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get('error'), 'no_active_battle')

if __name__ == '__main__':
    unittest.main()
