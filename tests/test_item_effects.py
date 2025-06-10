import unittest

from monster_rpg.items import ALL_ITEMS, apply_item_effect


class DummyMonster:
    def __init__(self, hp=30, mp=20):
        self.name = "Dummy"
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.status_effects = []
        self.is_alive = True


class ItemEffectFunctionTests(unittest.TestCase):
    def test_heal_hp_effect(self):
        m = DummyMonster(hp=40)
        m.hp = 10
        result = apply_item_effect(ALL_ITEMS['small_potion'], m)
        self.assertTrue(result)
        self.assertEqual(m.hp, 40)

    def test_revive_effect(self):
        m = DummyMonster(hp=30)
        m.hp = 0
        m.is_alive = False
        result = apply_item_effect(ALL_ITEMS['revive_scroll'], m)
        self.assertTrue(result)
        self.assertTrue(m.is_alive)
        self.assertEqual(m.hp, m.max_hp // 2)

    def test_cure_status_effect(self):
        m = DummyMonster(hp=30)
        m.status_effects.append({'name': 'poison', 'remaining': 2})
        result = apply_item_effect(ALL_ITEMS['antidote'], m)
        self.assertTrue(result)
        self.assertFalse(any(e['name'] == 'poison' for e in m.status_effects))


if __name__ == '__main__':
    unittest.main()
