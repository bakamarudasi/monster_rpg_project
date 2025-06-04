# monsters/monster_data.py

from .monster_class import Monster, GROWTH_TYPE_AVERAGE, GROWTH_TYPE_EARLY, GROWTH_TYPE_LATE
from skills.skills import ALL_SKILLS
from items.item_data import ALL_ITEMS

# モンスターランク定義
RANK_S = "S"
RANK_A = "A"
RANK_B = "B"
RANK_C = "C"
RANK_D = "D"

SLIME = Monster(
    name="スライム", hp=25, attack=8, defense=5, level=1, element="水",
    skills=[ALL_SKILLS["heal"]] if "heal" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="slime",
    rank=RANK_D,
    drop_items=[(ALL_ITEMS["small_potion"], 0.2)],
    scout_rate=0.5
)

GOBLIN = Monster(
    name="ゴブリン", hp=40, attack=12, defense=8, level=2, element="なし",
    skills=[ALL_SKILLS["fireball"]] if "fireball" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="goblin",
    rank=RANK_D,
    drop_items=[(ALL_ITEMS["small_potion"], 0.15)],
    scout_rate=0.4
)

WOLF = Monster(
    name="ウルフ", hp=50, attack=15, defense=7, level=3, element="なし",
    skills=[],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="wolf",
    rank=RANK_C,
    drop_items=[(ALL_ITEMS["small_potion"], 0.1)],
    scout_rate=0.35
)

SLIME_GOBLIN_HYBRID = Monster(
    name="スライムゴブリン",
    hp=35,
    attack=10,
    defense=7,
    level=1,
    element="混合",
    skills=[],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="slime_goblin_hybrid",
    rank=RANK_C,
    drop_items=[(ALL_ITEMS["small_potion"], 0.25)],  # 例: 合成モンスターはCランク
    scout_rate=0.3
)

# 例として高ランクモンスターを追加
DRAGON_PUP = Monster(
    name="ドラゴンのこども",
    hp=70,
    attack=25,
    defense=20,
    level=5,
    element="火",
    skills=[ALL_SKILLS["fireball"]] if "fireball" in ALL_SKILLS else [], # 初期スキルは弱めでも良い
    growth_type=GROWTH_TYPE_LATE, # 大器晩成型
    monster_id="dragon_pup",
    rank=RANK_A,
    drop_items=[(ALL_ITEMS["small_potion"], 0.05)],
    scout_rate=0.15
)

PHOENIX_CHICK = Monster(
    name="不死鳥のヒナ",
    hp=60,
    attack=18,
    defense=22,
    level=5,
    element="火",
    skills=[ALL_SKILLS["heal"]] if "heal" in ALL_SKILLS else [], # 自己回復スキル持ち
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="phoenix_chick",
    rank=RANK_S,
    drop_items=[(ALL_ITEMS["small_potion"], 0.05)],  # 例: 不死鳥のヒナはSランク
    scout_rate=0.1
)


ALL_MONSTERS = {
    "slime": SLIME,
    "goblin": GOBLIN,
    "wolf": WOLF,
    "slime_goblin_hybrid": SLIME_GOBLIN_HYBRID,
    "dragon_pup": DRAGON_PUP,
    "phoenix_chick": PHOENIX_CHICK,
}
