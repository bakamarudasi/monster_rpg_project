# map_data.py (新規作成)
import random # エンカウント判定で使います

class Location:
    def __init__(self, location_id, name, description, connections=None,
                 possible_enemies=None, enemy_weights=None, encounter_rate=0.0, has_inn=False,
                 inn_cost=0, hidden_connections=None, has_shop=False,
                 shop_items=None, shop_monsters=None, boss_enemy_id=None,
                 rare_enemies=None, treasure_items=None, event_chance=0.0,
                 avg_enemy_level=1):
        """
        場所の情報を保持するクラス。
        location_id (str): 場所を識別するユニークなID
        name (str): 場所の名前 (例: 「始まりの村」)
        description (str): 場所の説明文
        connections (dict): 接続されている場所の情報。 {"方向コマンド": "行き先のlocation_id"} の形式。
                            例: {"北へ進む": "forest_path_1", "南へ戻る": "village_square"}
        possible_enemies (list): その場所で出現する可能性のあるモンスターのID (ALL_MONSTERSのキー)のリスト。
                                 例: ["slime", "goblin"]
        enemy_weights (dict): possible_enemies の各モンスターを引く確率の重み
                              例: {"slime": 0.8, "goblin": 0.2}
        encounter_rate (float): その場所でのエンカウント率 (0.0 から 1.0)。0ならエンカウントしない。
        """
        self.location_id = location_id
        self.name = name
        self.description = description
        self.connections = connections if connections else {}
        self.possible_enemies = possible_enemies if possible_enemies else []
        self.enemy_weights = enemy_weights
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

    def get_random_enemy_id(self):
        """この場所で出現する可能性のあるモンスターIDをランダムに1つ返す。"""
        if self.possible_enemies:
            if self.enemy_weights:
                enemies = list(self.enemy_weights.keys())
                weights = list(self.enemy_weights.values())
                return random.choices(enemies, weights=weights, k=1)[0]
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
        shop_monsters={"slime": 50},
        avg_enemy_level=1
    ),
    "field_near_village": Location(
        location_id="field_near_village",
        name="村の近くの草原",
        description="見渡す限りの草原が広がっている。時折、弱いモンスターの姿が見える。",
        connections={"南": "village_square", "北東": "forest_entrance"},
        possible_enemies=["slime"], # ALL_MONSTERSのキーで指定
        encounter_rate=0.6, # 60%の確率でエンカウント
        avg_enemy_level=1
    ),
    "forest_entrance": Location(
        location_id="forest_entrance",
        name="妖精の森・入り口",
        description="薄暗い森の入り口。奥からはかすかに獣の気配がする。",
        connections={"南西": "field_near_village", "奥へ": "deep_forest", "東": "mystic_lake"},
        possible_enemies=["goblin", "slime"],
        enemy_weights={"goblin": 0.7, "slime": 0.3},
        encounter_rate=0.75,
        avg_enemy_level=2
    ),
    "mystic_lake": Location(
        location_id="mystic_lake",
        name="神秘の湖",
        description="森の奥にひっそりと佇む美しい湖。水面が青く光っている。",
        connections={"西": "forest_entrance"},
        possible_enemies=["water_wolf", "forest_spirit"],
        encounter_rate=0.8,
        avg_enemy_level=3
    ),
    "deep_forest": Location(
        location_id="deep_forest",
        name="妖精の森・奥地",
        description="木々が鬱蒼と茂り、昼なお暗い。強力なモンスターが生息しているようだ。",
        connections={"入り口へ": "forest_entrance"},
        possible_enemies=["wolf", "goblin", "forest_spirit"],
        enemy_weights={"wolf": 0.5, "goblin": 0.3, "forest_spirit": 0.2},
        encounter_rate=0.9,
        hidden_connections={"さらに奥へ": "forest_boss_room"},
        boss_enemy_id="dragon_pup",
        rare_enemies=["phoenix_chick"],
        treasure_items=["small_potion"],
        event_chance=0.3,
        avg_enemy_level=4
    ),
    "forest_boss_room": Location(
        location_id="forest_boss_room",
        name="森の守護者の間",
        description="森の奥深くに佇む神秘的な祭壇。強大なモンスターの気配がする。",
        connections={"奥地へ戻る": "deep_forest"},
        possible_enemies=["dragon_pup"],
        encounter_rate=1.0,
        avg_enemy_level=5
    ),
    "hill_road": Location(
    location_id="hill_road",
    name="丘陵街道",
    description="ゆるやかな丘を抜ける古びた街道。行商人の姿もちらほら。",
    connections={"南": "field_near_village", "北": "mountain_foothills"},
    possible_enemies=["wolf", "orc_warrior"],
    encounter_rate=0.55,
    avg_enemy_level=3
),

"mountain_foothills": Location(
    location_id="mountain_foothills",
    name="山麓の荒野",
    description="切り立った崖と転がる岩石。空気が薄くなり始めている。",
    connections={"南": "hill_road", "北": "thunder_peak", "西": "ancient_ruins"},
    possible_enemies=["orc_warrior", "skeleton_archer", "troll_brute"],
    encounter_rate=0.75,
    treasure_items=["medium_potion"],
    avg_enemy_level=4,
),

"thunder_peak": Location(
    location_id="thunder_peak",
    name="雷鳴峰",
    description="雲間を貫く尖塔のような山頂。常に雷が轟く。",
    connections={"南": "mountain_foothills"},
    possible_enemies=["thunder_eagle", "storm_golem"],
    encounter_rate=0.85,
    rare_enemies=["nameless_kingling"],
    boss_enemy_id="storm_golem",
    treasure_items=["thunder_core"],
    avg_enemy_level=6,
),

"ancient_ruins": Location(
    location_id="ancient_ruins",
    name="古代遺跡",
    description="苔むした石碑と崩れた柱が並ぶ、忘れられた文明の跡。",
    connections={"東": "mountain_foothills", "地下へ": "catacombs_entrance"},
    possible_enemies=["elf_mage", "goblin", "undead_warrior"],
    encounter_rate=0.7,
    event_chance=0.25,
    avg_enemy_level=5,
),

"catacombs_entrance": Location(
    location_id="catacombs_entrance",
    name="地下墓地・入口",
    description="石階段が闇へと続く。不気味な気配が漂う。",
    connections={"上へ戻る": "ancient_ruins", "奥へ": "catacombs_deep"},
    possible_enemies=["skeleton_archer", "undead_warrior", "gravetide_hollow"],
    encounter_rate=0.8,
    treasure_items=["frost_crystal"],
    avg_enemy_level=6,
),

"catacombs_deep": Location(
    location_id="catacombs_deep",
    name="地下墓地・深層",
    description="蝋燭の火が揺れる石室。静寂を破る足音が反響する。",
    connections={"入口へ戻る": "catacombs_entrance", "奈落へ": "abyssal_chasm"},
    possible_enemies=["blighted_knight", "vampire_lord"],
    encounter_rate=0.9,
    boss_enemy_id="abyss_watcher",
    rare_enemies=["abyss_watcher"],
    treasure_items=["abyss_shard"],
    avg_enemy_level=8,
),

"abyssal_chasm": Location(
    location_id="abyssal_chasm",
    name="深淵の裂け目",
    description="底知れぬ闇が広がる亀裂。闇の鼓動が聞こえる。",
    connections={"地上へ": "catacombs_deep", "光の塔へ": "celestial_tower"},
    possible_enemies=["shadow_panther", "abyss_watcher", "blighted_knight"],
    encounter_rate=1.0,
    avg_enemy_level=9,
),

"celestial_tower": Location(
    location_id="celestial_tower",
    name="天啓の塔",
    description="蒼穹へと伸びる光輝の塔。最上階には試練が待つ。",
    connections={"深淵へ戻る": "abyssal_chasm"},
    possible_enemies=["celestial_panther", "cinder_sentinel"],
    encounter_rate=0.85,
    boss_enemy_id="celestial_dragon",
    has_shop=True,
    shop_items={"large_potion": 120, "elixir": 300, "celestial_feather": 500},
    has_inn=True,
    inn_cost=50,
    treasure_items=["celestial_feather", "elixir"],
    avg_enemy_level=10,
),
"desert_outskirts": Location(
    location_id="desert_outskirts",
    name="砂漠の外れ",
    description="熱風が吹きつけ、遠くに蜃気楼が揺れる。",
    connections={"西": "field_near_village", "東": "desert_oasis"},
    possible_enemies=["desert_scorpion", "sand_wyrm"],
    encounter_rate=0.65,
    avg_enemy_level=4,
),

"desert_oasis": Location(
    location_id="desert_oasis",
    name="オアシスの集落",
    description="椰子の木が茂る水辺。旅人の憩いの場だ。",
    connections={"西": "desert_outskirts", "北": "sunken_temple"},
    has_inn=True, inn_cost=20,
    has_shop=True, shop_items={"medium_potion": 40, "antidote": 25},
    possible_enemies=["desert_scorpion"],
    encounter_rate=0.3,
    avg_enemy_level=3,
),

"sunken_temple": Location(
    location_id="sunken_temple",
    name="水没した神殿",
    description="半ば湖に沈んだ古代神殿。水棲モンスターの巣窟。",
    connections={"南": "desert_oasis", "深部へ": "abyssal_marsh"},
    possible_enemies=["kraken", "mermaid_siren", "water_wolf"],
    encounter_rate=0.85,
    treasure_items=["frost_crystal"],
    avg_enemy_level=7,
),

"abyssal_marsh": Location(
    location_id="abyssal_marsh",
    name="深淵の湿地",
    description="黒い水面に泡が弾ける不気味な湿地帯。",
    connections={"上へ": "sunken_temple", "東": "volcanic_ridge"},
    possible_enemies=["kraken", "blighted_knight", "abyss_watcher"],
    encounter_rate=0.95,
    avg_enemy_level=8,
),

"volcanic_ridge": Location(
    location_id="volcanic_ridge",
    name="熔岩稜線",
    description="赤熱した溶岩が流れ、空気が揺らめく灼熱地帯。",
    connections={"西": "abyssal_marsh", "北": "lava_core"},
    possible_enemies=["lava_elemental", "troll_brute", "orc_warrior"],
    encounter_rate=0.9,
    rare_enemies=["cinder_sentinel"],
    treasure_items=["dragon_scale"],
    avg_enemy_level=9,
),

"lava_core": Location(
    location_id="lava_core",
    name="熔岩核",
    description="流動するマグマの中央に浮かぶ岩盤。炎の脈動が響く。",
    connections={"南": "volcanic_ridge", "上空へ": "sky_isle"},
    boss_enemy_id="lava_elemental",
    possible_enemies=["lava_elemental"],
    encounter_rate=1.0,
    avg_enemy_level=10,
),

"sky_isle": Location(
    location_id="sky_isle",
    name="浮遊島・聖域",
    description="雲海を見下ろす浮島。澄んだ風の中で光が舞う。",
    connections={"下へ": "lava_core", "北": "celestial_tower"},  # 既存塔と直通
    possible_enemies=["sky_seraph", "thunder_eagle", "celestial_panther"],
    encounter_rate=0.8,
    hidden_connections={"更なる空の高みへ": "sky_isle_inner_sanctum"},
    avg_enemy_level=10,
),

"sky_isle_inner_sanctum": Location(
    location_id="sky_isle_inner_sanctum",
    name="浮遊島・内なる聖域",
    description="静謐な光が満ちる最奥部。翼を持つ守護者が待ち構えている。",
    connections={"外縁へ戻る": "sky_isle"},
    boss_enemy_id="sky_seraph",
    possible_enemies=["sky_seraph"],
    encounter_rate=1.0,
    treasure_items=["celestial_feather", "elixir"],
    avg_enemy_level=12,
)
# ------------------------------------------------------------
# ▼ ここまで追加マップ
# ------------------------------------------------------------

    
}

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
        lines.append(f"{loc.name}: {conn_text}")
    return "\n".join(lines)


def display_map() -> None:
    """ワールドマップを表示する"""
    print("===== ワールドマップ =====")
    print(get_map_overview())
    print("========================")
