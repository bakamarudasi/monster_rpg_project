import pytest
from monster_rpg.battle import enemy_take_action
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS


def test_taunt_forces_attack(monkeypatch):
    hero = Monster('Hero', hp=40, attack=5, defense=2)
    enemy = Monster('Enemy', hp=30, attack=10, defense=5, skills=[ALL_SKILLS['heal']], ai_role='healer')
    enemy.apply_status('taunt', 1)
    players = [hero]
    enemies = [enemy]
    monkeypatch.setattr('random.random', lambda: 0.0)
    monkeypatch.setattr('random.choice', lambda seq: seq[0])
    enemy_take_action(enemy, players, enemies)
    assert hero.hp < 40


def test_cant_attack_prevents_attack(monkeypatch):
    hero = Monster('Hero', hp=40, attack=5, defense=2)
    enemy = Monster('Goblin', hp=30, attack=8, defense=3, ai_role='attacker')
    enemy.apply_status('cant_attack', 1)
    players = [hero]
    enemies = [enemy]
    monkeypatch.setattr('random.random', lambda: 1.0)
    enemy_take_action(enemy, players, enemies)
    assert hero.hp == 40
