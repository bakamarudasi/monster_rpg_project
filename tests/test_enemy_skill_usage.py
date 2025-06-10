from monster_rpg.battle import enemy_take_action
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS


def test_enemy_heals_when_using_skill(monkeypatch):
    hero = Monster('Hero', hp=50, attack=10, defense=5, speed=5)
    enemy = Monster('Enemy', hp=30, attack=5, defense=2, speed=5,
                    skills=[ALL_SKILLS['heal']])
    enemy.hp = 10
    players = [hero]
    enemies = [enemy]

    monkeypatch.setattr('random.random', lambda: 0.0)
    monkeypatch.setattr('random.choice', lambda seq: seq[0])

    enemy_take_action(enemy, players, enemies)

    assert enemy.hp > 10
