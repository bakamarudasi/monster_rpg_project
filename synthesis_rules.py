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

# 将来的には、合成に必要なアイテムなどもここに定義できる
# SYNTHESIS_ITEMS_REQUIRED = {
# "slime_goblin_hybrid": "magic_stone",
# }
