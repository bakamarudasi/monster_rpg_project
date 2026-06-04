# synthesis_rules.py (新規作成)

# 合成レシピの定義
# キー: (素材モンスター1のID, 素材モンスター2のID) のタプル。IDはアルファベット順にソートして登録。
# バリュー: 結果モンスターのID
# モンスターIDは、ALL_MONSTERS のキーと一致させる（通常はモンスター名の小文字）

SYNTHESIS_RECIPES = {
    ("slime", "wolf"): "water_wolf",              # 例: スライム + ウルフ
    ("orc_warrior", "slime"): "poison_orc",       # スライムの粘性×オークの暴力
    ("elf_mage", "slime"): "frost_elf",           # 冷気魔力を帯びたエルフ
    ("orc_warrior", "skeleton_archer"): "undead_warrior",
    ("giant_golem", "thunder_eagle"): "storm_golem",
    ("celestial_dragon", "shadow_panther"): "celestial_panther",
    # --- 特殊配合: ダーク童話の住人（隠しレシピ） ---
    ("blighted_knight", "elf_mage"): "poison_queen",        # 白雪の毒后
    ("shadow_panther", "vampire_lord"): "beheader_alice",   # 断頭のアリシア
    ("shadow_panther", "wolf"): "crimson_hood",             # 紅ずきんの牙
    ("abyss_watcher", "pontiff_shade"): "sleeping_maiden",  # 硝子棺の眠り姫
    ("lava_elemental", "sky_seraph"): "match_ember",        # マッチ売りの焔
    # --- 新モンスターの錬成レシピ（野生に出ない＝作って手に入れる） ---
    ("giant_golem", "shadow_panther"): "obsidian_gargoyle",   # 黒曜のガーゴイル
    ("desert_scorpion", "sand_wyrm"): "wyrm_of_dunes",        # 砂海の竜
    ("cinder_hound", "wyrm_of_dunes"): "inferno_wyrm",        # 獄炎の竜（連鎖配合）
    ("frost_elf", "glacier_warden"): "glacial_empress",       # 氷獄の女王
    ("abyss_watcher", "kraken"): "void_leviathan",            # 虚海のリヴァイアサン
    ("celestial_dragon", "sky_seraph"): "astral_seraphim",    # 天輪のセラフィム
    ("astral_seraphim", "vampire_lord"): "abyssal_seraph",    # 堕天の熾天使

    # === 追加レシピ（既存86体を素材の網で結ぶ。組み合わせ＝コンテンツ量） ===
    # --- 序盤の遊べる配合 ---
    ("bat", "wild_rat"): "spark_mouse",                    # 小獣どうし→帯電ネズミ
    ("goblin", "wolf"): "orc_warrior",                     # 群れの長
    ("moss_slime", "walking_mushroom"): "thorn_lurker",    # 苔と茸→棘の潜伏者
    ("mire_toad", "rock_crab"): "tide_serpent",            # 沼の主
    ("mire_toad", "skeleton_archer"): "bog_revenant",      # 沼＋骸→沼の亡者
    # --- 鳥・雷の系譜 ---
    ("gale_harrier", "spark_mouse"): "thunder_eagle",      # 疾風＋帯電→雷鷲
    ("gale_harrier", "thunder_eagle"): "thunderlord_roc",  # 雷帝の大鷲
    ("sky_seraph", "thunder_eagle"): "solar_griffon",      # 陽光のグリフォン
    ("flame_mantis", "thunder_eagle"): "electro_mantis",   # 電磁の蟷螂
    # --- 水棲の系譜 ---
    ("mermaid_siren", "tide_serpent"): "coral_hydra",      # 珊瑚の多頭
    ("crystal_golem", "sand_wyrm"): "crystal_drake",       # 水晶の竜
    # --- 巨像・大地の系譜 ---
    ("giant_golem", "troll_brute"): "iron_juggernaut",     # 鋼鉄の巨兵
    ("crystal_golem", "frost_elf"): "glacier_warden",      # 氷河の番人
    ("cinder_hound", "lava_elemental"): "cinder_sentinel", # 焔の守護像
    ("cinder_sentinel", "giant_golem"): "obsidian_titan",  # 黒曜の巨神
    ("cinder_hound", "flame_mantis"): "lava_elemental",    # 溶岩の精
    # --- 自然・光の系譜 ---
    ("meadow_sprite", "walking_mushroom"): "moonlit_dryad",# 月夜の樹精
    ("ashen_drake", "ember_pup"): "phoenix_chick",         # 不死鳥の雛
    ("dragon_pup", "sky_seraph"): "celestial_dragon",      # 天空竜
    # --- 闇・不死の系譜 ---
    ("shadow_panther", "spectral_raven"): "midnight_horror",  # 真夜中の恐怖
    ("skeleton_archer", "spectral_raven"): "gravetide_hollow",# 墓潮のうろ
    ("undead_warrior", "venom_naga"): "blighted_knight",      # 疫病の騎士
    ("abyss_watcher", "frost_elf"): "pontiff_shade",          # 氷の教皇
    ("abyss_watcher", "shadow_panther"): "blood_fiend",       # 血の魔
    ("abyss_watcher", "blood_fiend"): "vampire_lord",         # 吸血鬼の王
    ("abyss_watcher", "midnight_horror"): "eldritch_tome",    # 禁忌の魔導書
    ("data_wraith", "vampire_lord"): "nameless_kingling",     # 名もなき王
    ("phantom_thief", "shadow_panther"): "ronin_spirit",      # 浪人の霊
    ("mist_wraith", "thunder_eagle"): "storm_djinn",          # 嵐の精霊
}

# ジャックポット（大当たり）配合の抽選プール。家系配合などの非レシピ配合時に
# ごく稀に出現するダーク童話の住人たち。tale_devourer は最高レアでこの枠のみ。
SPECIAL_MONSTER_POOL = [
    "poison_queen",
    "beheader_alice",
    "crimson_hood",
    "sleeping_maiden",
    "match_ember",
    "tale_devourer",
]

# 合成に必要なアイテムの定義
# キーは SYNTHESIS_RECIPES と同じタプル、値は必要なアイテムID
SYNTHESIS_ITEMS_REQUIRED = {
    ("orc_warrior", "slime"): "magic_stone",
    ("elf_mage", "slime"): "frost_crystal",
    ("orc_warrior", "skeleton_archer"): "abyss_shard",
    ("giant_golem", "thunder_eagle"): "thunder_core",
    ("celestial_dragon", "shadow_panther"): "celestial_feather",
    # S級錬成は希少素材を要求
    ("abyss_watcher", "kraken"): "abyss_shard",
    ("celestial_dragon", "sky_seraph"): "celestial_feather",
    ("frost_elf", "glacier_warden"): "frost_crystal",
    ("astral_seraphim", "vampire_lord"): "abyss_shard",
    # 追加S級錬成のゲート
    ("cinder_sentinel", "giant_golem"): "fire_crystal",
    ("abyss_watcher", "blood_fiend"): "abyss_shard",
    ("abyss_watcher", "midnight_horror"): "abyss_shard",
    ("data_wraith", "vampire_lord"): "thunder_core",
    ("dragon_pup", "sky_seraph"): "celestial_feather",
}

# モンスター1体とアイテム1つで行う特殊合成のレシピ
# キーは (モンスターID, アイテムID) のタプル、値は生成されるモンスターID
MONSTER_ITEM_RECIPES = {
    ("slime", "dragon_scale"): "dragon_pup",  # スライム + ドラゴンスケイル
    ("wolf", "frost_crystal"): "water_wolf",  # ウルフ + フロストクリスタル
}

# アイテム同士の合成レシピ
# キーは (アイテム1ID, アイテム2ID) のタプル。アルファベット順に並べる
# 値は生成されるアイテムIDまたは装備ID
ITEM_ITEM_RECIPES = {
    ("dragon_scale", "magic_stone"): "bronze_sword",
    ("small_potion", "small_potion"): "medium_potion",
}

# ---------------------------
# New: family-based synthesis
# ---------------------------

# Mapping of ranks to numeric values for calculating blended ranks.  Higher
# values represent stronger monsters.  The mapping includes rank "E" used by
# some of the weaker monsters.
RANK_VALUES = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1, "E": 0}

# Reverse lookup table for converting numeric values back to rank strings.
VALUE_TO_RANK = {v: k for k, v in RANK_VALUES.items()}

# When two monsters do not match a specific recipe, their families may still
# combine to produce a new monster.  Keys are tuples of family names (sorted
# alphabetically) and values are the resulting family.  The monster to create is
# chosen based on the parents' ranks.
FAMILY_SYNTHESIS_RULES = {
    ("beast", "slime"): "slime",
    ("dragon", "slime"): "dragon_pup",
}


def find_family_synthesis_result(
    family1: str | None,
    rank1: str | None,
    family2: str | None,
    rank2: str | None,
) -> str | None:
    """Return a monster ID for a family based synthesis result.

    The function first determines the resulting family from
    ``FAMILY_SYNTHESIS_RULES`` and then looks through all monsters to find the
    one whose rank is closest to the blended rank of the parents.
    """

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
    target_value = (v1 + v2) / 2

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

