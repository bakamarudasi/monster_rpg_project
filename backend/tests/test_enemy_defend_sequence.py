from monster_rpg.battle import enemy_take_action
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS


def test_enemy_defends_when_hp_low():
    hero = Monster('Hero', hp=50, attack=10, defense=5)
    enemy = Monster('Enemy', hp=40, attack=5, defense=2)
    enemy.hp = 10
    players = [hero]
    enemies = [enemy]
    enemy_take_action(enemy, players, enemies)
    assert any(e['name'] == 'defending' for e in enemy.status_effects)


def test_enemy_skill_sequence(monkeypatch):
    hero = Monster('Hero', hp=50, attack=10, defense=5)
    boss = Monster(
        'Boss', hp=40, attack=10, defense=5,
        skills=[ALL_SKILLS['heal'], ALL_SKILLS['tackle']],
        skill_sequence=['heal', 'tackle']
    )
    players = [hero]
    enemies = [boss]

    monkeypatch.setattr('random.random', lambda: 1.0)

    boss.hp = 20
    enemy_take_action(boss, players, enemies)
    assert boss.hp > 20

    enemy_take_action(boss, players, enemies)
    assert hero.hp < 50
