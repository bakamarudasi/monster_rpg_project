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

    # === 魔王枠（新規）：合成限定のプレステージS級。属性の手薄なS帯を埋める ===
    ("storm_djinn", "thunderlord_roc"): "storm_sovereign",        # 風: 暴風の覇王
    ("iron_juggernaut", "obsidian_titan"): "gaia_colossus",       # 土: 山喰らいの巨王
    ("blighted_knight", "venom_naga"): "plague_monarch",          # 毒: 万病の魔王
    ("coral_hydra", "void_leviathan"): "abyssal_tide_king",       # 水: 深淵の海皇
    ("nameless_kingling", "thunderlord_roc"): "thunder_emperor",  # 雷: 雷霆の帝王
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
    # 魔王枠の錬成ゲート
    ("storm_djinn", "thunderlord_roc"): "thunder_core",
    ("iron_juggernaut", "obsidian_titan"): "dragon_scale",
    ("blighted_knight", "venom_naga"): "abyss_shard",
    ("coral_hydra", "void_leviathan"): "frost_crystal",
    ("nameless_kingling", "thunderlord_roc"): "thunder_core",
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


# ---------------------------------------------------------------------------
# 位階配合 (rank-order breeding) — DQM準拠の汎用フォールバック
# ---------------------------------------------------------------------------
# 特定レシピにも家系ルールにも当たらない任意の2体から「必ず何か」を生む仕組み。
# これにより全組み合わせが配合可能になり、どの個体も配合の累代＋値を伸ばせる
# （レシピの無い種が＋値を振れない問題の解消）。
#
# 位階＝系統(family)内での強さの並び順。既存データ（rank→初期ステ合計）から自動導出する。
# 通常配合の上限はA級まで（S級＝魔王枠は特殊配合/ジャックポット専用）。

# 通常配合で到達できる最高ランク値。これを超える種（＝S級）は位階ラダーから除外する。
GENERIC_MAX_RANK_VALUE = RANK_VALUES["A"]


def _template_strength(template) -> tuple[int, int]:
    """種族の強さキー（位階比較用）。(ランク値, 初期ステ合計) の辞書順で比較する。"""
    rank_v = RANK_VALUES.get(str(getattr(template, "rank", "")).upper(), 0)
    total = (
        getattr(template, "max_hp", 0)
        + getattr(template, "max_mp", 0)
        + getattr(template, "base_attack", 0)
        + getattr(template, "base_defense", 0)
        + getattr(template, "base_speed", 0)
    )
    return (rank_v, total)


def _species_strength(monster) -> tuple[int, int]:
    """個体の「種族としての」強さキー。位階は種族固有なのでレベルや＋値ではなく
    種族テンプレ（ALL_MONSTERS）で測る。未登録種は個体の実値で代用する。"""
    from . import monster_data as all_monster_data

    mid = (getattr(monster, "monster_id", "") or "").lower()
    template = all_monster_data.ALL_MONSTERS.get(mid)
    return _template_strength(template if template is not None else monster)


def family_ladder(family: str) -> list:
    """系統内のテンプレを弱→強で並べた位階ラダー。S級は通常配合の上限から除外する。"""
    from . import monster_data as all_monster_data

    fam = (family or "").lower()
    members = [
        m
        for m in all_monster_data.ALL_MONSTERS.values()
        if (getattr(m, "family", "") or "").lower() == fam
        and RANK_VALUES.get(str(getattr(m, "rank", "")).upper(), 0) <= GENERIC_MAX_RANK_VALUE
    ]
    return sorted(members, key=_template_strength)


def _step_up_in_family(family: str, ref_strength: tuple[int, int]) -> str | None:
    """系統内で ref_strength より位階が1つ上のテンプレID。上が無ければ None。"""
    for t in family_ladder(family):
        if _template_strength(t) > ref_strength:
            return t.monster_id
    return None


def ikai_synthesis_candidates(parent1, parent2) -> list[str]:
    """位階配合の子候補ID。先頭が推奨（位階が高い親の系統で1つ上）。

    候補は最大4つ: 〔高位の親の系統で1つ上〕〔もう片方の系統で1つ上〕〔親1そのもの〕
    〔親2そのもの〕。親そのものを含めるのは「同種配合での＋値稼ぎ」と、ユーザー原案の
    「親のどちらかの枠に収める」を両立するため。位階1つ上はS級を含まない（A止まり）。
    """
    from . import monster_data as all_monster_data

    all_monsters = all_monster_data.ALL_MONSTERS
    s1 = _species_strength(parent1)
    s2 = _species_strength(parent2)
    higher, lower = (parent1, parent2) if s1 >= s2 else (parent2, parent1)
    href = max(s1, s2)

    candidates: list[str] = []

    def add(mid):
        if mid and mid in all_monsters and mid not in candidates:
            candidates.append(mid)

    add(_step_up_in_family(getattr(higher, "family", "") or "", href))
    add(_step_up_in_family(getattr(lower, "family", "") or "", href))
    add((getattr(higher, "monster_id", "") or "").lower())
    add((getattr(lower, "monster_id", "") or "").lower())
    return candidates


def synthesis_candidates(parent1, parent2) -> tuple[tuple | None, list[str]]:
    """配合の子候補を解決する。戻り値は (recipe_key or None, [候補ID...])。

    - 特殊レシピに当たる場合: recipe_key を返し、候補はそのレシピ結果のみ（上書き＝選択不可）。
    - それ以外: 既存の家系ルール結果（あれば）に続けて位階配合の候補を返す（プレイヤーが選択）。
    """
    id1 = (getattr(parent1, "monster_id", "") or "").lower()
    id2 = (getattr(parent2, "monster_id", "") or "").lower()
    recipe_key = tuple(sorted([id1, id2]))
    if recipe_key in SYNTHESIS_RECIPES:
        return recipe_key, [SYNTHESIS_RECIPES[recipe_key]]

    candidates: list[str] = []
    fam = find_family_synthesis_result(
        getattr(parent1, "family", None),
        getattr(parent1, "rank", None),
        getattr(parent2, "family", None),
        getattr(parent2, "rank", None),
    )
    if fam:
        candidates.append(fam)
    for cid in ikai_synthesis_candidates(parent1, parent2):
        if cid not in candidates:
            candidates.append(cid)
    return None, candidates

