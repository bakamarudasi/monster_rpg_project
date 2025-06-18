import pytest
from monster_rpg.battle import enemy_take_action
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS


def test_healer_role_heals_low_hp_ally(monkeypatch):
    healer = Monster('Healer', hp=40, attack=5, defense=5, skills=[ALL_SKILLS['heal']], ai_role='healer')
    ally = Monster('Ally', hp=50, attack=5, defense=5)
    ally.hp = 20
    players = [Monster('Hero', hp=60, attack=10, defense=5)]
    enemies = [healer, ally]

    monkeypatch.setattr('random.random', lambda: 1.0)
    enemy_take_action(healer, players, enemies)
    assert ally.hp > 20


def test_attacker_role_targets_lowest_hp(monkeypatch):
    attacker = Monster('Attacker', hp=40, attack=10, defense=5, ai_role='attacker')
    p1 = Monster('P1', hp=50, attack=8, defense=5)
    p2 = Monster('P2', hp=30, attack=8, defense=5)
    players = [p1, p2]
    enemies = [attacker]

    monkeypatch.setattr('random.random', lambda: 1.0)
    monkeypatch.setattr('random.choice', lambda seq: seq[0])
    enemy_take_action(attacker, players, enemies)
    assert p2.hp < 30
    assert p1.hp == 50


def test_debuffer_role_uses_debuff(monkeypatch):
    debuffer = Monster('Debuffer', hp=40, attack=5, defense=5, skills=[ALL_SKILLS['slow']], ai_role='debuffer')
    p1 = Monster('Strong', hp=40, attack=15, defense=5)
    p2 = Monster('Weak', hp=40, attack=5, defense=5)
    players = [p1, p2]
    enemies = [debuffer]

    monkeypatch.setattr('random.random', lambda: 1.0)
    start_mp = debuffer.mp
    enemy_take_action(debuffer, players, enemies)
    assert debuffer.mp < start_mp
