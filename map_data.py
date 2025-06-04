# map_data.py (新規作成)
import random # エンカウント判定で使います

class Location:
    def __init__(self, location_id, name, description, connections=None, possible_enemies=None, encounter_rate=0.0, has_inn=False, inn_cost=0, hidden_connections=None, has_shop=False, shop_items=None, shop_monsters=None):
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

    def get_random_enemy_id(self):
        """この場所で出現する可能性のあるモンスターIDをランダムに1つ返す。"""
        if self.possible_enemies:
            return random.choice(self.possible_enemies)
        return None

# --- 場所の定義 ---
# ここにゲーム世界の場所をどんどん追加していきます。
LOCATIONS = {
    "village_square": Location(
        location_id="village_square",
        name="アリアルの村・広場",
        description="あなたの冒険が始まる小さな村の広場。宿屋の看板が見える。",
        connections={"北": "field_near_village"},
        encounter_rate=0.0,
        has_inn=True,  # 宿屋あり
        inn_cost=10,   # 宿泊料10G
        has_shop=True,
        shop_items={"small_potion": 15},
        shop_monsters={"slime": 50}
    ),
    "field_near_village": Location(
        location_id="field_near_village",
        name="村の近くの草原",
        description="見渡す限りの草原が広がっている。時折、弱いモンスターの姿が見える。",
        connections={"南": "village_square", "北東": "forest_entrance"},
        possible_enemies=["slime"], # ALL_MONSTERSのキーで指定
        encounter_rate=0.6 # 60%の確率でエンカウント
    ),
    "forest_entrance": Location(
        location_id="forest_entrance",
        name="妖精の森・入り口",
        description="薄暗い森の入り口。奥からはかすかに獣の気配がする。",
        connections={"南西": "field_near_village", "奥へ": "deep_forest"},
        possible_enemies=["goblin", "slime"],
        encounter_rate=0.75
    ),
    "deep_forest": Location(
        location_id="deep_forest",
        name="妖精の森・奥地",
        description="木々が鬱蒼と茂り、昼なお暗い。強力なモンスターが生息しているようだ。",
        connections={"入り口へ": "forest_entrance"},
        possible_enemies=["wolf", "goblin"], # wolf は ALL_MONSTERS に定義が必要
        encounter_rate=0.9,
        hidden_connections={"さらに奥へ": "forest_boss_room"}
    ),
    "forest_boss_room": Location(
        location_id="forest_boss_room",
        name="森の守護者の間",
        description="森の奥深くに佇む神秘的な祭壇。強大なモンスターの気配がする。",
        connections={"奥地へ戻る": "deep_forest"},
        possible_enemies=["dragon_pup"],
        encounter_rate=1.0
    ),
    
}

STARTING_LOCATION_ID = "village_square" # ゲーム開始時の場所ID