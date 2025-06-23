import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app, Battle, active_battles
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.item_data import ALL_ITEMS

class BattleItemUseTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_item_battle.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        hero = Monster('Hero', hp=50, attack=5, defense=2, speed=10)
        hero.hp = 20
        player.party_monsters.append(hero)
        player.items.append(ALL_ITEMS['small_potion'])
        enemy = Monster('Slime', hp=10, attack=3, defense=1)
        battle_obj = Battle(player.party_monsters, [enemy], player)
        active_battles[self.user_id] = battle_obj

    def tearDown(self):
        active_battles.pop(self.user_id, None)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_item_use_consumes_inventory_and_heals(self):
        resp = self.client.post(
            f'/battle/{self.user_id}',
            json={'action': 'item', 'item_idx': 0, 'target_ally': 0}
        )
        self.assertEqual(resp.status_code, 200)
        battle_obj = active_battles[self.user_id]
        hero = battle_obj.player_party[0]
        self.assertEqual(len(battle_obj.player.items), 0)
        self.assertGreater(hero.hp, 20)

if __name__ == '__main__':
    unittest.main()
