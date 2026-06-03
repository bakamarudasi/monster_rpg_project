"""覚醒進化（分岐・条件・覚醒抽選）のテスト。"""

import types
import unittest
from unittest.mock import patch

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters import evolution_rules
from monster_rpg.monsters.evolution_rules import get_evolution_branches
from monster_rpg.player import Player
from monster_rpg.services import evolution_service

# random をこの値に固定 → 覚醒しない / する
NO_AWAKEN = 0.99
FORCE_AWAKEN = 0.0
RANDOM_PATH = 'monster_rpg.monsters.monster_class.random.random'


def _mon(monster_id, level):
    m = ALL_MONSTERS[monster_id].copy()
    m.level = level
    return m


class EvolutionRulesTests(unittest.TestCase):
    def test_normalizer_handles_dict_list_none(self):
        self.assertEqual(evolution_rules._normalize(None), [])
        self.assertEqual(evolution_rules._normalize({'a': 1}), [{'a': 1}])
        self.assertEqual(evolution_rules._normalize([{'a': 1}]), [{'a': 1}])

    def test_branches_for_known_monster(self):
        branches = get_evolution_branches('dragon_pup')
        self.assertTrue(branches)
        self.assertEqual(branches[0]['evolves_to'], 'ashen_drake')


class EvolutionBehaviorTests(unittest.TestCase):
    def test_evolves_at_level_without_awaken(self):
        m = _mon('dragon_pup', 10)
        with patch(RANDOM_PATH, return_value=NO_AWAKEN):
            res = m._try_evolution(log=[], verbose=True)
        self.assertEqual(m.monster_id, 'ashen_drake')
        self.assertFalse(m.is_rare)
        self.assertIsNotNone(res)
        self.assertFalse(res['awakened'])

    def test_does_not_evolve_below_level(self):
        m = _mon('dragon_pup', 9)
        self.assertIsNone(m._try_evolution(log=[], verbose=True))
        self.assertEqual(m.monster_id, 'dragon_pup')

    def test_requires_skill_negative_gate(self):
        m = _mon('slime', 5)
        m.skills = [s for s in m.skills if getattr(s, 'name', '') != 'ヒール']
        self.assertIsNone(m._try_evolution(log=[], verbose=False))
        self.assertEqual(m.monster_id, 'slime')

    def test_requires_skill_positive(self):
        m = _mon('slime', 5)
        m.skills.append(types.SimpleNamespace(name='ヒール'))
        with patch(RANDOM_PATH, return_value=NO_AWAKEN):
            res = m._try_evolution(log=[], verbose=False)
        self.assertEqual(m.monster_id, 'water_wolf')
        self.assertIsNotNone(res)

    def test_awakening_makes_rare_and_logs(self):
        m = _mon('dragon_pup', 10)
        log = []
        with patch(RANDOM_PATH, return_value=FORCE_AWAKEN):
            res = m._try_evolution(log=log, verbose=True)
        self.assertEqual(m.monster_id, 'ashen_drake')
        self.assertTrue(m.is_rare)
        self.assertTrue(res['awakened'])
        self.assertTrue(res['became_rare'])
        self.assertTrue(any('覚醒' in e['message'] for e in log))

    def test_awaken_into_upgrades_target(self):
        patched = {'dragon_pup': [{'level': 10, 'evolves_to': 'ashen_drake',
                                   'awaken_chance': 1.0, 'awaken_into': 'shadow_panther'}]}
        m = _mon('dragon_pup', 10)
        with patch.dict(evolution_rules.EVOLUTION_RULES, patched, clear=False), \
             patch(RANDOM_PATH, return_value=FORCE_AWAKEN):
            m._try_evolution(log=[], verbose=False)
        self.assertEqual(m.monster_id, 'shadow_panther')
        self.assertTrue(m.is_rare)

    def test_requires_equipment_negative_gate(self):
        patched = {'wolf': [{'level': 7, 'evolves_to': 'shadow_panther',
                             'requires_equipment': 'weapon'}]}
        with patch.dict(evolution_rules.EVOLUTION_RULES, patched, clear=False):
            bare = _mon('wolf', 7)
            self.assertIsNone(bare._try_evolution(log=[], verbose=False))
            self.assertEqual(bare.monster_id, 'wolf')


class EvolutionServiceTests(unittest.TestCase):
    def test_can_evolve_and_evolve(self):
        p = Player('E')
        p.party_monsters.append(_mon('dragon_pup', 10))
        self.assertTrue(evolution_service.can_evolve(p.party_monsters[0]))
        with patch(RANDOM_PATH, return_value=NO_AWAKEN):
            ok, data = evolution_service.evolve(p, 0)
        self.assertTrue(ok)
        self.assertEqual(data['name'], ALL_MONSTERS['ashen_drake'].name)
        self.assertFalse(data['awakened'])
        self.assertEqual(p.party_monsters[0].monster_id, 'ashen_drake')

    def test_evolve_not_ready_below_level(self):
        p = Player('E')
        p.party_monsters.append(_mon('dragon_pup', 5))
        self.assertFalse(evolution_service.can_evolve(p.party_monsters[0]))
        ok, data = evolution_service.evolve(p, 0)
        self.assertFalse(ok)
        self.assertEqual(p.party_monsters[0].monster_id, 'dragon_pup')


if __name__ == '__main__':
    unittest.main()
