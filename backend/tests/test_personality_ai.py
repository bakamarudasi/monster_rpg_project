"""性格に応じたオート戦闘AIのテスト。"""

import types
import unittest

from monster_rpg.monsters.monster_data import ALL_MONSTERS
from monster_rpg.monsters.personality_ai import choose_auto_action, auto_style
from monster_rpg.battle import Battle
from monster_rpg.player import Player


def _skill(target="enemy", cost=5, heal=False, name="x"):
    effects = [{"type": "heal", "stat": "hp", "amount": 10}] if heal else [{"type": "damage"}]
    return types.SimpleNamespace(target=target, cost=cost, effects=effects, name=name, scope="single")


def _mon(personality, skills=None, mp=50, hp=100, max_hp=100):
    m = ALL_MONSTERS["wolf"].copy()
    m.personality_id = personality
    m.skills = list(skills or [])
    m.mp, m.max_mp = mp, max(mp, 50)
    m.hp, m.max_hp = hp, max_hp
    m.is_alive = True
    return m


def _enemies():
    e0 = ALL_MONSTERS["wolf"].copy(); e0.hp = 50; e0.is_alive = True
    e1 = ALL_MONSTERS["wolf"].copy(); e1.hp = 10; e1.is_alive = True  # 最も弱った敵 = index 1
    return [e0, e1]


class AutoStyleTests(unittest.TestCase):
    def test_personality_maps_to_style(self):
        self.assertEqual(auto_style(_mon("brave")), "aggressive")
        self.assertEqual(auto_style(_mon("clever")), "caster")
        self.assertEqual(auto_style(_mon("stubborn")), "guardian")
        self.assertEqual(auto_style(_mon("hasty")), "striker")
        self.assertEqual(auto_style(_mon("balanced")), "balanced")


class ChooseAutoActionTests(unittest.TestCase):
    def test_balanced_attacks_first_enemy(self):
        actor = _mon("balanced")
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act, {"type": "attack", "target_enemy": 0})

    def test_striker_attacks_weakest_enemy(self):
        actor = _mon("hasty")
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act, {"type": "attack", "target_enemy": 1})

    def test_caster_uses_offensive_skill_on_weakest(self):
        actor = _mon("clever", skills=[_skill(target="enemy", cost=8)])
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act["type"], "skill")
        self.assertEqual(act["skill"], 0)
        self.assertEqual(act["target_enemy"], 1)

    def test_caster_without_skill_falls_back_to_attack(self):
        actor = _mon("clever", skills=[])
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act["type"], "attack")

    def test_caster_skips_unaffordable_skill(self):
        actor = _mon("quiet", skills=[_skill(target="enemy", cost=999)], mp=5)
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act["type"], "attack")

    def test_aggressive_uses_big_move(self):
        actor = _mon("brave", skills=[_skill(target="enemy", cost=10)])
        act = choose_auto_action(actor, [actor], _enemies())
        self.assertEqual(act["type"], "skill")
        self.assertEqual(act["target_enemy"], 1)

    def test_guardian_heals_hurt_ally(self):
        actor = _mon("stubborn", skills=[_skill(target="ally", cost=6, heal=True)])
        hurt = _mon("balanced", hp=10, max_hp=100)
        act = choose_auto_action(actor, [actor, hurt], _enemies())
        self.assertEqual(act["type"], "skill")
        self.assertEqual(act["skill"], 0)
        self.assertEqual(act["target_ally"], 1)

    def test_guardian_attacks_when_no_one_hurt(self):
        actor = _mon("stubborn", skills=[_skill(target="ally", cost=6, heal=True)])
        healthy = _mon("balanced", hp=100, max_hp=100)
        act = choose_auto_action(actor, [actor, healthy], _enemies())
        self.assertEqual(act["type"], "attack")

    def test_no_alive_enemies_returns_attack(self):
        actor = _mon("brave")
        dead = ALL_MONSTERS["wolf"].copy(); dead.is_alive = False
        act = choose_auto_action(actor, [actor], [dead])
        self.assertEqual(act, {"type": "attack", "target_enemy": -1})


class AutoActionIntegrationTests(unittest.TestCase):
    def test_chosen_attack_is_engine_compatible(self):
        actor = _mon("hasty")
        enemy = ALL_MONSTERS["slime"].copy(); enemy.is_alive = True
        battle = Battle([actor], [enemy], Player("X"))
        battle.current_actor = actor
        before = enemy.hp
        action = choose_auto_action(actor, battle.player_party, battle.enemy_party)
        battle.process_player_action(action)
        self.assertLess(enemy.hp, before)  # ちゃんと攻撃が通る


if __name__ == "__main__":
    unittest.main()
