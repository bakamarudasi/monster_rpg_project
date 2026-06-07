"""敵の手番が確実に消化されることのテスト（ターン進行リファクタの回帰防止）。"""

import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.web.battle import active_battles
from monster_rpg.battle import Battle
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster


class RunUntilPlayerTurnTests(unittest.TestCase):
    def test_stops_on_living_player(self):
        hero = Monster('Hero', hp=100, attack=10, defense=5, speed=8)
        foe = Monster('Foe', hp=100, attack=20, defense=5, speed=20)
        battle = Battle([hero], [foe], Player('P'))
        battle.run_until_player_turn()
        self.assertIn(battle.current_actor, battle.player_party)
        self.assertTrue(battle.current_actor.is_alive)

    def test_enemy_acts_within_a_few_turns(self):
        hero = Monster('Hero', hp=500, attack=1, defense=5, speed=8)
        foe = Monster('Foe', hp=500, attack=20, defense=5, speed=20)
        battle = Battle([hero], [foe], Player('P'))
        for _ in range(5):
            battle.run_until_player_turn()
            if battle.finished:
                break
            battle.process_player_action({'type': 'attack', 'target_enemy': 0})
        self.assertLess(hero.hp, hero.max_hp)   # 敵が確実に反撃している


class EnemyTurnEndpointTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_enemy_turns.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.hero = Monster('Hero', hp=200, attack=10, defense=5, speed=8, monster_id='slime')
        self.foe = Monster('Foe', hp=300, attack=20, defense=5, speed=16, monster_id='goblin')
        player = Player('Tester', user_id=self.user_id)
        player.party_monsters = [self.hero]
        active_battles[self.user_id] = Battle([self.hero], [self.foe], player)

    def tearDown(self):
        active_battles.pop(self.user_id, None)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_enemy_attacks_back_after_player_action(self):
        before = self.hero.hp
        resp = self.client.post(f'/battle/{self.user_id}', json={'action': 'attack', 'target_enemy': 0})
        self.assertEqual(resp.status_code, 200)
        # プレイヤーの行動後、敵が反撃してHPが減っている
        self.assertLess(self.hero.hp, before)
        log = [m.get('message', '') for m in resp.get_json()['log']]
        self.assertTrue(any(m.startswith('Foe の攻撃') for m in log))


if __name__ == '__main__':
    unittest.main()
