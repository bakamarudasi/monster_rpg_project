import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.items.item_data import ALL_ITEMS
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg import trading

class TradeTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_trade.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists('monster_rpg_save.db'):
            os.remove('monster_rpg_save.db')
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.seller_id = database_setup.create_user('seller', 'pw1')
        self.buyer_id = database_setup.create_user('buyer', 'pw2')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        seller = Player('Seller', user_id=self.seller_id)
        seller.items.append(ALL_ITEMS['small_potion'])
        seller.add_monster_to_party('slime')
        seller.add_monster_to_party('goblin')
        seller.move_to_reserve(0)
        mon = seller.reserve_monsters[0]
        mon.gain_exp(mon.calculate_exp_to_next_level())
        save_manager.save_game(seller, self.db_path, user_id=self.seller_id)

        buyer = Player('Buyer', user_id=self.buyer_id, gold=200)
        buyer.add_monster_to_party('goblin')
        save_manager.save_game(buyer, self.db_path, user_id=self.buyer_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_trade_flow(self):
        resp = self.client.post(f'/market/list_item/{self.seller_id}', json={'item_idx': 0, 'price': 30})
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(f'/market/list_monster/{self.seller_id}', json={'reserve_idx': 0, 'price': 80})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/market/listings')
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        item_listing = next(l for l in data if l['item_type'] == 'item')
        monster_listing = next(l for l in data if l['item_type'] == 'monster')

        resp = self.client.post(f'/market/buy/{self.buyer_id}/{item_listing["id"]}')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(f'/market/buy/{self.buyer_id}/{monster_listing["id"]}')
        self.assertEqual(resp.status_code, 200)

        buyer = save_manager.load_game(self.db_path, user_id=self.buyer_id)
        self.assertEqual(len(buyer.items), 1)
        self.assertEqual(buyer.items[0].item_id, 'small_potion')
        self.assertTrue(any(m.monster_id == 'slime' for m in buyer.party_monsters))
        slime = next(m for m in buyer.party_monsters if m.monster_id == 'slime')
        self.assertGreaterEqual(slime.level, 2)

    def test_cannot_buy_own_listing(self):
        resp = self.client.post(
            f'/market/list_item/{self.seller_id}',
            json={'item_idx': 0, 'price': 25}
        )
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/market/listings')
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        listing_id = data[0]['id']

        resp = self.client.post(f'/market/buy/{self.seller_id}/{listing_id}')
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get('/market/listings')
        self.assertEqual(len(resp.get_json()), 1)

        seller = save_manager.load_game(self.db_path, user_id=self.seller_id)
        self.assertEqual(seller.gold, 50)
        self.assertEqual(len(seller.items), 0)
