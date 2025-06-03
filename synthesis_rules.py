# synthesis_rules.py (新規作成)

# 合成レシピの定義
# キー: (素材モンスター1のID, 素材モンスター2のID) のタプル。IDはアルファベット順にソートして登録。
# バリュー: 結果モンスターのID
# モンスターIDは、ALL_MONSTERS のキーと一致させる（通常はモンスター名の小文字）

SYNTHESIS_RECIPES = {
    ("goblin", "slime"): "slime_goblin_hybrid", # ゴブリンとスライムを合成するとスライムゴブリンハイブリッドが生まれる
    # 他のレシピもここに追加
    # 例: ("slime", "wolf"): "water_wolf",
}

# 将来的には、合成に必要なアイテムなどもここに定義できる
# SYNTHESIS_ITEMS_REQUIRED = {
# "slime_goblin_hybrid": "magic_stone",
# }
