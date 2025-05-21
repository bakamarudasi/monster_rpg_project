# monsters/monster_data.py

# 同じフォルダ内の monster_class.py から Monster クラスと成長タイプ定数をインポート
from .monster_class import Monster, GROWTH_TYPE_AVERAGE, GROWTH_TYPE_EARLY, GROWTH_TYPE_LATE
# skills.py から ALL_SKILLS 辞書をインポート (パスは環境に合わせて調整)
# from ..skills.skills import ALL_SKILLS # 一つ上の階層のskillsフォルダを見る場合
from skills.skills import ALL_SKILLS # skillsフォルダが同じ階層か、Pythonのパスが通っていれば

# --- 個々のモンスターインスタンスを定義 ---
SLIME = Monster(
    name="スライム", hp=25, attack=8, defense=5, level=1, element="水",
    skills=[ALL_SKILLS["heal"]] if "heal" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY
)

GOBLIN = Monster(
    name="ゴブリン", hp=40, attack=12, defense=8, level=2, element="なし",
    skills=[ALL_SKILLS["fireball"]] if "fireball" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE
)

# DRAGON = Monster(name="ドラゴン", ..., growth_type=GROWTH_TYPE_LATE)

# --- 全モンスターを格納する辞書 ---
ALL_MONSTERS = {
    "slime": SLIME,
    "goblin": GOBLIN,
    # "dragon": DRAGON,
}