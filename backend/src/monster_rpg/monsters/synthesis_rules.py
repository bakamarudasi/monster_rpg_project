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
}

# 合成に必要なアイテムの定義
# キーは SYNTHESIS_RECIPES と同じタプル、値は必要なアイテムID
SYNTHESIS_ITEMS_REQUIRED = {
    ("orc_warrior", "slime"): "magic_stone",
    ("elf_mage", "slime"): "frost_crystal",
    ("orc_warrior", "skeleton_archer"): "abyss_shard",
    ("giant_golem", "thunder_eagle"): "thunder_core",
    ("celestial_dragon", "shadow_panther"): "celestial_feather",
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

