# synthesis_rules.py (強化版)

# 合成レシピの定義
# キー: (素材モンスター1のID, 素材モンスター2のID) のタプル。IDはアルファベット順にソートして登録。
# バリュー: 結果モンスターのID

SYNTHESIS_RECIPES = {
    # --- 基本レシピ ---
    ("slime", "wolf"): "water_wolf",
    ("orc_warrior", "slime"): "poison_orc",
    ("elf_mage", "slime"): "frost_elf",
    ("orc_warrior", "skeleton_archer"): "undead_warrior",
    ("giant_golem", "thunder_eagle"): "storm_golem",
    ("celestial_dragon", "shadow_panther"): "celestial_panther",

    # --- 新規レシピ ---
    ("bat", "imp"): "spectral_raven",
    ("goblin", "walking_mushroom"): "poison_orc",
    ("wolf", "shadow_panther"): "abyss_watcher",
    ("dragon_pup", "phoenix_chick"): "celestial_dragon",
    ("mermaid_siren", "slime"): "coral_hydra",
    ("desert_scorpion", "orc_warrior"): "blighted_knight",
    ("frost_elf", "mist_wraith"): "pontiff_shade",
    ("blood_fiend", "skeleton_archer"): "vampire_lord",
    ("elf_mage", "moonlit_dryad"): "sky_seraph",
    ("giant_golem", "lava_elemental"): "obsidian_titan",
    ("iron_juggernaut", "thunder_eagle"): "nameless_kingling",
    ("troll_brute", "undead_warrior"): "iron_juggernaut",
    ("sand_wyrm", "desert_scorpion"): "crystal_drake",
    ("goblin", "wild_rat"): "slime_goblin_hybrid",
    ("electro_mantis", "bat"): "thunder_eagle",
    ("moonlit_dryad", "walking_mushroom"): "mermaid_siren",
    ("ashen_drake", "cinder_sentinel"): "obsidian_titan",
    ("kraken", "coral_hydra"): "celestial_dragon",

    # --- スライム系 合成 ---
    ("slime", "slime"): "king_slime",                     # スライム + スライム → キングスライム
    ("dark_slime", "slime"): "dark_slime",                # スライム + ダークスライム → ダークスライム
    ("heal_slime", "slime"): "heal_slime",                # スライム + ホイミスライム → ホイミスライム
    ("metal_slime", "slime"): "metal_slime",              # スライム + メタルスライム → メタルスライム

    # --- ドラゴン系 合成 ---
    ("dragon_pup", "elemental_fire"): "fire_dragon",      # ドラゴンパピー + ファイアエレメンタル → ファイアドラゴン
    ("dragon_pup", "elemental_ice"): "ice_dragon",        # ドラゴンパピー + アイスエレメンタル → アイスドラゴン
    ("dragon_pup", "elemental_thunder"): "thunder_dragon", # ドラゴンパピー + サンダーエレメンタル → サンダードラゴン
    ("dragon_zombie", "zombie"): "dragon_zombie",          # ゾンビ + ドラゴンゾンビ(家族合成用)
    ("fire_dragon", "ice_dragon"): "holy_dragon",          # ファイアドラゴン + アイスドラゴン → ホーリードラゴン

    # --- 獣系 合成 ---
    ("dire_wolf", "wolf"): "dire_wolf",                    # ウルフ + ダイアウルフ → ダイアウルフ
    ("dire_wolf", "elemental_ice"): "silver_fenrir",       # ダイアウルフ + アイスエレメンタル → シルバーフェンリル
    ("elemental_fire", "wolf"): "flame_lion",              # ウルフ + ファイアエレメンタル → フレイムライオン
    ("elemental_thunder", "wolf"): "thunder_tiger",        # ウルフ + サンダーエレメンタル → サンダータイガー
    ("flame_lion", "silver_fenrir"): "golden_bahamut",     # フレイムライオン + シルバーフェンリル → ゴールデンバハムート
    ("dire_wolf", "flame_lion"): "cerberus",               # ダイアウルフ + フレイムライオン → ケルベロス
    ("flame_lion", "sea_serpent"): "chimera",              # フレイムライオン + シーサーペント → キマイラ

    # --- 悪魔系 合成 ---
    ("imp", "lesser_demon"): "lesser_demon",               # インプ + レッサーデーモン → レッサーデーモン
    ("lesser_demon", "vampire_lord"): "arch_demon",        # レッサーデーモン + ヴァンパイアロード → アークデーモン
    ("elf_mage", "lesser_demon"): "succubus",              # エルフ魔導士 + レッサーデーモン → サキュバス
    ("arch_demon", "holy_dragon"): "demon_king",           # アークデーモン + ホーリードラゴン → 魔王

    # --- アンデッド系 合成 ---
    ("ghost", "zombie"): "wraith",                         # ゾンビ + ゴースト → レイス
    ("elf_mage", "wraith"): "lich",                        # エルフ魔導士 + レイス → リッチ
    ("skeleton_archer", "undead_warrior"): "death_knight",  # スケルトンアーチャー + アンデッドウォリアー → デスナイト

    # --- 植物系 合成 ---
    ("mandragora", "walking_mushroom"): "venus_trap",      # マンドラゴラ + ウォーキングマッシュルーム → ビーナストラップ
    ("treant", "walking_mushroom"): "treant",              # ウォーキングマッシュルーム + トレント → トレント
    ("holy_dragon", "treant"): "world_tree",               # トレント + ホーリードラゴン → 世界樹

    # --- 鳥系 合成 ---
    ("griffin", "thunder_eagle"): "storm_roc",              # サンダーイーグル + グリフォン → ストームロック
    ("harpy", "thunder_eagle"): "griffin",                  # ハーピー + サンダーイーグル → グリフォン
    ("phoenix", "phoenix_chick"): "phoenix",               # フェニックスチック → フェニックス

    # --- 水棲系 合成 ---
    ("kraken", "sea_serpent"): "leviathan",                # シーサーペント + クラーケン → リヴァイアサン
    ("mermaid_siren", "water_sprite"): "water_sprite",     # マーメイドセイレーン → ウンディーネ

    # --- 機械系 合成 ---
    ("clockwork_soldier", "iron_juggernaut"): "war_machine", # クロックワーク + アイアンジャガーノート → ウォーマシン
    ("thunder_dragon", "war_machine"): "mecha_dragon",      # ウォーマシン + サンダードラゴン → メカドラゴン

    # --- 妖精系 合成 ---
    ("moonlit_dryad", "pixie"): "titania",                 # ピクシー + ムーンリットドライアド → ティターニア
    ("griffin", "pixie"): "oberon",                        # ピクシー + グリフォン → オベロン
    ("angel", "sky_seraph"): "angel",                      # スカイセラフ + エンジェル

    # --- 岩石系 合成 ---
    ("gargoyle", "rock_golem"): "gargoyle",                # ロックゴーレム + ガーゴイル
    ("crystal_golem", "rock_golem"): "crystal_golem",      # ロックゴーレム + クリスタルゴーレム
    ("crystal_golem", "obsidian_titan"): "diamond_titan",  # クリスタルゴーレム + オブシディアンタイタン → ダイヤモンドタイタン

    # --- 人型系 合成 ---
    ("ninja", "orc_warrior"): "samurai",                   # 忍者 + オークウォーリア → 侍
    ("lesser_demon", "samurai"): "dark_knight",            # 侍 + レッサーデーモン → 暗黒騎士
    ("ninja", "shadow_panther"): "shadow_assassin",        # 忍者 + シャドウパンサー → シャドウアサシン
    ("samurai", "titania"): "hero",                        # 侍 + ティターニア → 勇者

    # --- 魔法系 合成 ---
    ("elemental_fire", "elemental_ice"): "grand_wizard",   # 各エレメンタル → 大魔導士
    ("dark_elf", "elf_mage"): "dark_elf",                  # エルフ魔導士 + ダークエルフ

    # --- 虫系 合成 ---
    ("desert_scorpion", "giant_spider"): "doom_scorpion",  # デザートスコーピオン + ジャイアントスパイダー → ドゥームスコーピオン
    ("electro_mantis", "giant_spider"): "queen_bee",       # エレクトロマンティス + ジャイアントスパイダー → クイーンビー
}

# 合成に必要なアイテムの定義
SYNTHESIS_ITEMS_REQUIRED = {
    ("orc_warrior", "slime"): "magic_stone",
    ("elf_mage", "slime"): "frost_crystal",
    ("orc_warrior", "skeleton_archer"): "abyss_shard",
    ("giant_golem", "thunder_eagle"): "thunder_core",
    ("celestial_dragon", "shadow_panther"): "celestial_feather",
    ("dragon_pup", "phoenix_chick"): "dragon_scale",
    ("blood_fiend", "skeleton_archer"): "abyss_shard",
    ("giant_golem", "lava_elemental"): "fire_crystal",
    ("kraken", "coral_hydra"): "celestial_feather",
}

# モンスター1体とアイテム1つで行う特殊合成のレシピ
MONSTER_ITEM_RECIPES = {
    ("slime", "dragon_scale"): "dragon_pup",
    ("wolf", "frost_crystal"): "water_wolf",
    ("goblin", "magic_stone"): "orc_warrior",
    ("bat", "thunder_core"): "electro_mantis",
    ("imp", "fire_crystal"): "lava_elemental",
    ("wild_rat", "abyss_shard"): "spectral_raven",
    ("walking_mushroom", "magic_stone"): "moonlit_dryad",
    ("skeleton_archer", "abyss_shard"): "gravetide_hollow",
    ("orc_warrior", "steel_ingot"): "iron_juggernaut",
    ("dragon_pup", "celestial_feather"): "ashen_drake",
    # --- 新規 モンスター+アイテム レシピ ---
    ("slime", "fire_crystal"): "dark_slime",
    ("slime", "holy_crystal"): "heal_slime",
    ("slime", "steel_ingot"): "metal_slime",
    ("zombie", "abyss_shard"): "wraith",
    ("wolf", "fire_crystal"): "flame_lion",
    ("wolf", "thunder_core"): "thunder_tiger",
    ("goblin", "abyss_shard"): "lesser_demon",
    ("rock_golem", "holy_crystal"): "crystal_golem",
    ("walking_mushroom", "herb"): "mandragora",
    ("mandragora", "magic_stone"): "venus_trap",
    ("harpy", "thunder_core"): "storm_roc",
    ("pixie", "celestial_feather"): "titania",
    ("ninja", "abyss_shard"): "shadow_assassin",
    ("clockwork_soldier", "steel_ingot"): "war_machine",
    ("fire_wisp", "dragon_scale"): "elemental_fire",
    ("ice_wisp", "frost_crystal"): "elemental_ice",
}

# アイテム同士の合成レシピ
ITEM_ITEM_RECIPES = {
    ("dragon_scale", "magic_stone"): "bronze_sword",
    ("small_potion", "small_potion"): "medium_potion",
    ("medium_potion", "medium_potion"): "large_potion",
    ("fire_crystal", "steel_ingot"): "flame_blade",
    ("frost_crystal", "steel_ingot"): "frost_edge",
    ("thunder_core", "steel_ingot"): "storm_lance",
    ("abyss_shard", "steel_ingot"): "shadow_dagger",
    ("celestial_feather", "magic_stone"): "holy_staff",
    ("fire_crystal", "frost_crystal"): "magic_stone",
    ("thunder_core", "magic_stone"): "power_fragment",
    ("tough_leather", "tough_leather"): "leather_armor",
    ("steel_ingot", "steel_ingot"): "iron_shield",
    ("dragon_scale", "celestial_feather"): "dragon_mail",
}

# ---------------------------
# Family-based synthesis (拡張版)
# ---------------------------

RANK_VALUES = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "E": 0}
VALUE_TO_RANK = {v: k for k, v in RANK_VALUES.items()}

FAMILY_SYNTHESIS_RULES = {
    # --- スライム系 ---
    ("beast", "slime"): "slime",
    ("dragon", "slime"): "dragon",
    ("slime", "slime"): "slime",
    ("humanoid", "slime"): "slime",
    ("magic", "slime"): "slime",

    # --- ドラゴン系 ---
    ("dragon", "dragon"): "dragon",
    ("beast", "dragon"): "dragon",
    ("aquatic", "dragon"): "dragon",
    ("insect", "dragon"): "dragon",
    ("machine", "dragon"): "dragon",

    # --- 獣系 ---
    ("beast", "beast"): "beast",
    ("beast", "humanoid"): "beast",
    ("beast", "insect"): "beast",
    ("beast", "plant"): "beast",

    # --- 悪魔系 ---
    ("demon", "demon"): "demon",
    ("demon", "undead"): "undead",
    ("demon", "humanoid"): "demon",
    ("demon", "fairy"): "demon",
    ("demon", "magic"): "demon",

    # --- アンデッド系 ---
    ("undead", "undead"): "undead",
    ("beast", "undead"): "undead",
    ("undead", "humanoid"): "undead",

    # --- 植物系 ---
    ("plant", "plant"): "plant",
    ("plant", "aquatic"): "plant",
    ("plant", "fairy"): "plant",
    ("plant", "spirit"): "spirit",

    # --- 鳥系 ---
    ("bird", "bird"): "bird",
    ("beast", "bird"): "bird",
    ("bird", "dragon"): "dragon",
    ("bird", "fairy"): "bird",

    # --- 水棲系 ---
    ("aquatic", "aquatic"): "aquatic",
    ("aquatic", "beast"): "aquatic",

    # --- 機械系 ---
    ("machine", "machine"): "machine",
    ("construct", "construct"): "construct",
    ("construct", "dragon"): "construct",
    ("elemental", "construct"): "construct",
    ("machine", "construct"): "machine",

    # --- 妖精系 ---
    ("fairy", "fairy"): "fairy",
    ("fairy", "plant"): "fairy",
    ("fairy", "humanoid"): "fairy",
    ("fairy", "magic"): "fairy",

    # --- 岩石系 ---
    ("mineral", "mineral"): "mineral",
    ("mineral", "construct"): "mineral",
    ("mineral", "machine"): "mineral",

    # --- 魔法系 ---
    ("magic", "magic"): "magic",
    ("magic", "humanoid"): "magic",

    # --- 人型系 ---
    ("humanoid", "humanoid"): "humanoid",
    ("humanoid", "spirit"): "spirit",

    # --- 虫系 ---
    ("insect", "insect"): "insect",
    ("insect", "plant"): "insect",

    # --- 精霊系 ---
    ("spirit", "spirit"): "spirit",
    ("spirit", "undead"): "undead",
}

# ---------------------------------------------------------------------------
# Synthesis bonus traits: certain synthesis results can produce special traits
# ---------------------------------------------------------------------------
SYNTHESIS_TRAIT_BONUS = {
    # result_monster_id -> possible trait upgrade
    "celestial_dragon": "last_stand",
    "obsidian_titan": "iron_wall",
    "celestial_panther": "swift",
    "vampire_lord": "life_steal",
    "nameless_kingling": "last_stand",
    "holy_dragon": "last_stand",
    "demon_king": "berserker",
    "golden_bahamut": "fierce",
    "phoenix": "last_stand",
    "leviathan": "iron_wall",
    "world_tree": "regenerator",
    "diamond_titan": "iron_wall",
    "mecha_dragon": "thunder_resist",
    "hero": "last_stand",
    "cerberus": "fierce",
    "chimera": "berserker",
}


def find_family_synthesis_result(
    family1: str | None,
    rank1: str | None,
    family2: str | None,
    rank2: str | None,
) -> str | None:
    """Return a monster ID for a family based synthesis result."""

    if not family1 or not family2:
        return None

    key = tuple(sorted([family1.lower(), family2.lower()]))
    result_family = FAMILY_SYNTHESIS_RULES.get(key)
    if not result_family:
        return None

    from . import monster_data as all_monster_data

    all_monsters = all_monster_data.ALL_MONSTERS

    v1 = RANK_VALUES.get(str(rank1).upper(), 0)
    v2 = RANK_VALUES.get(str(rank2).upper(), 0)
    # Family synthesis now always produces at least same tier or one tier higher
    target_value = min((v1 + v2) / 2 + 0.5, 5)

    candidates = [
        m for m in all_monsters.values() if m.family and m.family.lower() == result_family
    ]
    if not candidates:
        if result_family in all_monsters:
            return result_family
        return None

    def rank_value(mon):
        return RANK_VALUES.get(str(mon.rank).upper(), 0)

    best = min(candidates, key=lambda m: abs(rank_value(m) - target_value))
    return best.monster_id


def get_synthesis_trait_bonus(result_monster_id: str) -> str | None:
    """Return a bonus trait for certain synthesis results."""
    return SYNTHESIS_TRAIT_BONUS.get(result_monster_id)
