# exploration.py
import random
from monsters import Monster, ALL_MONSTERS
from map_data import Location


def show_exploration_progress(progress: int) -> None:
    """表示用の簡易プログレスバーを描画する"""
    bar_length = 20
    filled = int(bar_length * progress / 100)
    bar = "#" * filled + "-" * (bar_length - filled)
    print(f"探索度: [{bar}] {progress}%")


def get_monster_instance_copy(monster_id_or_object: Monster | str) -> Monster | None:
    """モンスターの新しいインスタンス（コピー）を返します。"""
    if isinstance(monster_id_or_object, str):
        monster_id = monster_id_or_object.lower()
        if monster_id in ALL_MONSTERS:
            new_monster = ALL_MONSTERS[monster_id].copy()
            if new_monster:
                new_monster.hp = new_monster.max_hp
                new_monster.is_alive = True
            return new_monster
        else:
            print(f"エラー: モンスターID '{monster_id}' は存在しません。")
            return None
    elif isinstance(monster_id_or_object, Monster):
        new_monster = monster_id_or_object.copy()
        if new_monster:
            new_monster.hp = new_monster.max_hp
            new_monster.is_alive = True
        return new_monster
    else:
        print(f"エラー: 不正な引数です - {monster_id_or_object}")
        return None


def generate_enemy_party(location: Location, player=None) -> list[Monster]:
    """指定された場所に基づいて敵パーティを生成します (1〜3体)。"""
    enemy_party = []
    if not location.possible_enemies:
        return enemy_party

    num_enemies = random.randint(1, min(3, len(location.possible_enemies)))
    base_level = getattr(location, "avg_enemy_level", 1)

    for _ in range(num_enemies):
        enemy_id = random.choice(location.possible_enemies)
        enemy_instance = get_monster_instance_copy(enemy_id)
        if enemy_instance:
            if player is not None and hasattr(player, "monster_book"):
                player.monster_book.record_seen(enemy_instance.monster_id)
            target_level = max(1, base_level + random.randint(-1, 1))
            while enemy_instance.level < target_level:
                enemy_instance.level_up()
            enemy_party.append(enemy_instance)

    if not enemy_party and location.possible_enemies:
        enemy_id = random.choice(location.possible_enemies)
        enemy_instance = get_monster_instance_copy(enemy_id)
        if enemy_instance:
            if player is not None and hasattr(player, "monster_book"):
                player.monster_book.record_seen(enemy_instance.monster_id)
            target_level = max(1, base_level + random.randint(-1, 1))
            while enemy_instance.level < target_level:
                enemy_instance.level_up()
            enemy_party.append(enemy_instance)

    return enemy_party
