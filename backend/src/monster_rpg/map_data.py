# map_data.py (新規作成)
import json
import os
import random  # エンカウント判定で使います
import copy
from typing import Optional
from .monsters import Monster, ALL_MONSTERS


class Location:
    def __init__(
        self,
        location_id,
        name,
        description,
        connections=None,
        possible_enemies=None,
        enemy_pool=None,
        party_size=None,
        encounter_rate=0.0,
        has_inn=False,
        inn_cost=0,
        hidden_connections=None,
        has_shop=False,
        shop_items=None,
        shop_monsters=None,
        boss_enemy_id=None,
        rare_enemies=None,
        treasure_items=None,
        required_item=None,
        event_chance=0.0,
        avg_enemy_level=1,
        enemy_weights: dict[str, float] | None = None,
        x: int = 0,
        y: int = 0,
    ):
        """
        場所の情報を保持するクラス。
        location_id (str): 場所を識別するユニークなID
        name (str): 場所の名前 (例: 「始まりの村」)
        description (str): 場所の説明文
        connections (dict): 接続されている場所の情報。 {"方向コマンド": "行き先のlocation_id"} の形式。
                            例: {"北へ進む": "forest_path_1", "南へ戻る": "village_square"}
        possible_enemies (list): その場所で出現する可能性のあるモンスターIDリスト。
                                 例: ["slime", "goblin"]
        enemy_pool (dict): モンスターIDをキーとした出現率(重み)の辞書。
        party_size (list|tuple): 出現する敵パーティの数の最小・最大値。
        encounter_rate (float): その場所でのエンカウント率 (0.0 から 1.0)。0ならエンカウントしない。
        required_item (str|None): 移動に必要なアイテムID。Noneなら制限なし。
        x, y (int): ワールドマップ上の座標。未指定なら 0,0。
        """
        self.location_id = location_id
        self.name = name
        self.description = description
        self.connections = connections if connections else {}
        self.possible_enemies = possible_enemies if possible_enemies else []
        self.enemy_pool = enemy_pool if enemy_pool else {}
        self.party_size = party_size if party_size else [1, 1]
        self.encounter_rate = encounter_rate
        self.has_inn = has_inn  # 宿屋があるかどうかのフラグ (True/False)
        self.inn_cost = inn_cost  # 宿泊料金**
        self.hidden_connections = hidden_connections if hidden_connections else {}
        self.has_shop = has_shop
        self.shop_items = shop_items if shop_items else {}
        self.shop_monsters = shop_monsters if shop_monsters else {}
        self.boss_enemy_id = boss_enemy_id
        self.rare_enemies = rare_enemies if rare_enemies else []
        self.treasure_items = treasure_items if treasure_items else []
        self.required_item = required_item
        self.event_chance = event_chance
        self.avg_enemy_level = avg_enemy_level
        self.x = x
        self.y = y
        self.enemy_weights = enemy_weights

    def get_random_enemy_id(self):
        """この場所で出現する可能性のあるモンスターIDをランダムに1つ返す。"""
        if self.enemy_weights:
            total = sum(self.enemy_weights.values())
            r = random.random() * total
            cum = 0.0
            for enemy_id, weight in self.enemy_weights.items():
                cum += weight
                if r < cum:
                    return enemy_id
        if self.enemy_pool:
            total = sum(self.enemy_pool.values())
            r = random.random() * total
            cum = 0.0
            for enemy_id, weight in self.enemy_pool.items():
                cum += weight
                if r < cum:
                    return enemy_id
        if self.possible_enemies:
            return random.choice(self.possible_enemies)
        return None

    def create_enemy_party(self) -> list[Monster] | None:
        """出現モンスタープールから敵パーティを生成する"""
        if not self.enemy_pool or random.random() > self.encounter_rate:
            return None

        min_size, max_size = self.party_size
        num_enemies = random.randint(min_size, max_size)

        enemy_ids = list(self.enemy_pool.keys())
        weights = list(self.enemy_pool.values())
        if not enemy_ids:
            return None

        chosen_ids = random.choices(enemy_ids, weights=weights, k=num_enemies)
        party = []
        for eid in chosen_ids:
            base_monster = ALL_MONSTERS.get(eid)
            if base_monster:
                party.append(copy.deepcopy(base_monster))
            else:
                print(f"警告: モンスターID '{eid}' が見つかりません。")

        return party if party else None


# --- 場所の定義 ---
# LOCATIONS は JSON ファイルからロードして初期化される
LOCATIONS: dict[str, Location] = {}


def load_locations(filepath: str | None = None) -> None:
    """JSON ファイルから場所データを読み込み LOCATIONS を初期化する."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "map", "locations.json")

    with open(filepath, encoding="utf-8") as f:
        text = f.read().replace("\u00a0", " ")
        data = json.loads(text)

    loaded: dict[str, Location] = {}
    for loc_id, attrs in data.items():
        attrs = attrs or {}
        attrs.setdefault("location_id", loc_id)
        loc = Location(
            location_id=attrs.get("location_id", loc_id),
            name=attrs.get("name", ""),
            description=attrs.get("description", ""),
            connections=attrs.get("connections"),
            possible_enemies=attrs.get("possible_enemies"),
            enemy_pool=attrs.get("enemy_pool"),
            party_size=attrs.get("party_size"),
            encounter_rate=attrs.get("encounter_rate", 0.0),
            has_inn=attrs.get("has_inn", False),
            inn_cost=attrs.get("inn_cost", 0),
            hidden_connections=attrs.get("hidden_connections"),
            has_shop=attrs.get("has_shop", False),
            shop_items=attrs.get("shop_items"),
            shop_monsters=attrs.get("shop_monsters"),
            boss_enemy_id=attrs.get("boss_enemy_id"),
            rare_enemies=attrs.get("rare_enemies"),
            treasure_items=attrs.get("treasure_items"),
            required_item=attrs.get("required_item"),
            event_chance=attrs.get("event_chance", 0.0),
            avg_enemy_level=attrs.get("avg_enemy_level", 1),
            enemy_weights=attrs.get("enemy_weights"),
            x=attrs.get("x", 0),
            y=attrs.get("y", 0),
        )
        loaded[loc_id] = loc

    LOCATIONS.clear()
    LOCATIONS.update(loaded)


STARTING_LOCATION_ID = "village_square"  # ゲーム開始時の場所ID


def get_map_overview() -> str:
    """LOCATIONS の概要をテキストで返す"""
    lines = []
    for loc in LOCATIONS.values():
        conn_parts = []
        for cmd, dest_id in loc.connections.items():
            dest = LOCATIONS.get(dest_id)
            dest_name = dest.name if dest else dest_id
            conn_parts.append(f"{cmd}->{dest_name}")
        conn_text = ", ".join(conn_parts) if conn_parts else "なし"
        lines.append(f"{loc.name}({loc.x},{loc.y}): {conn_text}")
    return "\n".join(lines)


def get_map_grid() -> list[list[Location | None]]:
    """LOCATIONS の座標から2次元グリッドを生成して返す"""
    if not LOCATIONS:
        return []

    xs = [loc.x for loc in LOCATIONS.values()]
    ys = [loc.y for loc in LOCATIONS.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    grid: list[list[Location | None]] = [
        [None for _ in range(width)] for _ in range(height)
    ]

    for loc in LOCATIONS.values():
        grid[loc.y - min_y][loc.x - min_x] = loc

    return grid


