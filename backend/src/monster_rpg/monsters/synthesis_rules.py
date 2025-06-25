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

# When two monsters do not match a specific recipe, their families may still
# combine to produce a new monster. Keys are tuples of family names (sorted
# alphabetically) and values are the resulting monster IDs.
FAMILY_SYNTHESIS_RULES = {
    ("beast", "slime"): "slime_goblin_hybrid",
    ("dragon", "slime"): "dragon_pup",
}

