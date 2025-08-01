import os
import unittest

from monster_rpg import database_setup
from monster_rpg.web_main import app
from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.items.item_data import ALL_ITEMS


class RequiredItemMovementTests(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_required.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user("tester", "pw")
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_block_without_item(self):
        player = Player("Tester", user_id=self.user_id)
        player.current_location_id = "sky_isle"
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

        resp = self.client.post(
            f"/move/{self.user_id}", data={"dest": "sky_isle_inner_sanctum"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("celestial_feather", resp.get_data(as_text=True))
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual(loaded.current_location_id, "sky_isle")

    def test_move_with_item(self):
        player = Player("Tester", user_id=self.user_id)
        player.current_location_id = "sky_isle"
        player.items.append(ALL_ITEMS["celestial_feather"])
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

        resp = self.client.post(
            f"/move/{self.user_id}", data={"dest": "sky_isle_inner_sanctum"}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.headers["Location"].endswith(f"/play/{self.user_id}"))
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertEqual(loaded.current_location_id, "sky_isle_inner_sanctum")


if __name__ == "__main__":
    unittest.main()
