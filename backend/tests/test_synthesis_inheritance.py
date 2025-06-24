import unittest

import os

from monster_rpg.player import Player
from monster_rpg import save_manager
from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg import database_setup
from monster_rpg.web_main import app

class SynthesisInheritanceTests(unittest.TestCase):
    def test_skill_and_stat_inheritance(self):
        player = Player('Tester')
        player.add_monster_to_party('slime')
        player.add_monster_to_party('wolf')

        player.party_monsters[0].level = 5
        player.party_monsters[1].level = 5

        success, msg, child = player.synthesize_monster(0, 1)
        self.assertTrue(success)
        self.assertIsNotNone(child)
        self.assertEqual(child.monster_id, 'water_wolf')

        # Child should inherit heal from slime
        skill_names = [s.name for s in child.skills]
        self.assertIn('ヒール', skill_names)

        # Stats should receive a bonus
        template = ALL_MONSTERS['water_wolf']
        self.assertGreater(child.max_hp, template.max_hp)
        self.assertGreater(child.attack, template.attack)


class SynthesisRouteTests(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_fusion.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        database_setup.DATABASE_NAME = self.db_path
        database_setup.initialize_database()
        self.user_id = database_setup.create_user('tester', 'pw')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        player = Player('Tester', user_id=self.user_id)
        player.add_monster_to_party('slime')
        player.add_monster_to_party('wolf')
        save_manager.save_game(player, self.db_path, user_id=self.user_id)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_endpoint_uses_monster_material(self):
        resp = self.client.post(
            f'/synthesize_action/{self.user_id}',
            json={
                'base_type': 'monster',
                'base_id': 0,
                'material_type': 'monster',
                'material_id': 1,
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['name'], ALL_MONSTERS['water_wolf'].name)
        loaded = save_manager.load_game(self.db_path, user_id=self.user_id)
        self.assertIn('water_wolf', loaded.monster_book.captured)

if __name__ == '__main__':
    unittest.main()
