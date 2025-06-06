# map_data.py (新規作成)
import json
import os
import random  # エンカウント判定で使います

class Location:
    def __init__(
        self,
        location_id,
        name,
        description,
        connections=None,
        possible_enemies=None,
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
        possible_enemies (list): その場所で出現する可能性のあるモンスターのID (ALL_MONSTERSのキー)のリスト。
                                 例: ["slime", "goblin"]
        encounter_rate (float): その場所でのエンカウント率 (0.0 から 1.0)。0ならエンカウントしない。
        x, y (int): ワールドマップ上の座標。未指定なら 0,0。
        """
        self.location_id = location_id
        self.name = name
        self.description = description
        self.connections = connections if connections else {}
        self.possible_enemies = possible_enemies if possible_enemies else []
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
        if self.possible_enemies:
            return random.choice(self.possible_enemies)
        return None

# --- 場所の定義 ---
# LOCATIONS は JSON ファイルからロードして初期化される
LOCATIONS: dict[str, Location] = {}


def load_locations(filepath: str | None = None) -> None:
    """JSON ファイルから場所データを読み込み LOCATIONS を初期化する."""
    global LOCATIONS
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "data", "locations.json")

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

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


def display_map() -> None:
    """ワールドマップを表示する"""
    print("===== ワールドマップ =====")
    print(get_map_overview())
    print("========================")
