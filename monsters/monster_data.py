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
    name="スライム", hp=25, attack=8, defense=5, level=1, element="水",speed=5,
    # スライムは初期スキルとして回復スキルを持つ
    skills=[ALL_SKILLS["heal"]] if "heal" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="slime",
    rank=RANK_D, # 例: スライムはDランク
    drop_items=[(ALL_ITEMS["small_potion"], 0.5)]
)

GOBLIN = Monster(
    name="ゴブリン", hp=40, attack=12, defense=8, level=2, element="なし",speed=7,
    skills=[ALL_SKILLS["fireball"]] if "fireball" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="goblin",
    rank=RANK_D, # 例: ゴブリンはDランク
    drop_items=[(ALL_ITEMS["small_potion"], 0.2), (ALL_ITEMS["magic_stone"], 0.1)]
)

WOLF = Monster(
    name="ウルフ", hp=50, attack=15, defense=7, level=3, element="なし",speed=10,
    skills=[],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="wolf",
    rank=RANK_C, # 例: ウルフはCランク
    drop_items=[(ALL_ITEMS["medium_potion"], 0.1)]
)

SLIME_GOBLIN_HYBRID = Monster(
    name="スライムゴブリン", 
    hp=35,
    attack=10,
    defense=7,
    level=1, 
    element="混合",
    speed=6,
    skills=[], 
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="slime_goblin_hybrid",
    rank=RANK_C # 例: 合成モンスターはCランク
)

# 例として高ランクモンスターを追加
DRAGON_PUP = Monster(
    name="ドラゴンのこども",
    hp=70,
    attack=25,
    defense=20,
    level=5,
    element="火",
    speed=7,
    skills=[ALL_SKILLS["fireball"]] if "fireball" in ALL_SKILLS else [], # 初期スキルは弱めでも良い
    growth_type=GROWTH_TYPE_LATE, # 大器晩成型
    monster_id="dragon_pup",
    rank=RANK_A # 例: ドラゴンのこどもはAランク
)

PHOENIX_CHICK = Monster(
    name="不死鳥のヒナ",
    hp=60,
    attack=18,
    defense=22,
    level=5,
    element="火",
    speed=8,
    skills=[ALL_SKILLS["heal"]] if "heal" in ALL_SKILLS else [], # 自己回復スキル持ち
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="phoenix_chick",
    rank=RANK_S # 例: 不死鳥のヒナはSランク
)
ORC_WARRIOR = Monster(
    name="オークウォリアー",
    hp=60, attack=22, defense=15, level=4,
    element="土", speed=6,
    skills=[ALL_SKILLS["power_up"]] if "power_up" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="orc_warrior",
    rank=RANK_C,
)

SKELETON_ARCHER = Monster(
    name="スケルトンアーチャー",
    hp=45, attack=18, defense=8, level=3,
    element="闇", speed=9,
    skills=[ALL_SKILLS["poison_dart"]] if "poison_dart" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="skeleton_archer",
    rank=RANK_C,
)

ELF_MAGE = Monster(
    name="エルフメイジ",
    hp=55, attack=14, defense=10, level=4,
    element="風", speed=11,
    skills=[
        ALL_SKILLS[s] for s in ("ice_spear", "heal")
        if s in ALL_SKILLS
    ],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="elf_mage",
    rank=RANK_B,
)

TROLL_BRUTE = Monster(
    name="トロールブルート",
    hp=90, attack=28, defense=18, level=6,
    element="土", speed=4,
    skills=[ALL_SKILLS["regen"]] if "regen" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="troll_brute",
    rank=RANK_B,
)

MERMAID_SIREN = Monster(
    name="マーメイドサイレン",
    hp=65, attack=20, defense=14, level=6,
    element="水", speed=10,
    skills=[ALL_SKILLS["sleep_spell"]] if "sleep_spell" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="mermaid_siren",
    rank=RANK_B,
)

THUNDER_EAGLE = Monster(
    name="サンダーイーグル",
    hp=70, attack=24, defense=16, level=7,
    element="雷", speed=14,
    skills=[ALL_SKILLS["thunder_bolt"]] if "thunder_bolt" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="thunder_eagle",
    rank=RANK_A,
)

GIANT_GOLEM = Monster(
    name="ジャイアントゴーレム",
    hp=120, attack=32, defense=35, level=8,
    element="土", speed=3,
    skills=[
        ALL_SKILLS[s] for s in ("earth_quake", "guard_up")
        if s in ALL_SKILLS
    ],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="giant_golem",
    rank=RANK_A,
)

SHADOW_PANTHER = Monster(
    name="シャドウパンサー",
    hp=80, attack=30, defense=18, level=8,
    element="闇", speed=18,
    skills=[ALL_SKILLS["dark_pulse"]] if "dark_pulse" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="shadow_panther",
    rank=RANK_A,
)

VAMPIRE_LORD = Monster(
    name="ヴァンパイアロード",
    hp=95, attack=35, defense=22, level=10,
    element="闇", speed=15,
    skills=[
        ALL_SKILLS[s] for s in ("dark_pulse", "cure", "paralysis_shock")
        if s in ALL_SKILLS
    ],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="vampire_lord",
    rank=RANK_S,
)

CELESTIAL_DRAGON = Monster(
    name="セレスティアルドラゴン",
    hp=150, attack=45, defense=40, level=12,
    element="光", speed=12,
    skills=[
        ALL_SKILLS[s] for s in ("meteor_strike", "holy_light", "revive")
        if s in ALL_SKILLS
    ],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="celestial_dragon",
    rank=RANK_S,
)

WATER_WOLF = Monster(
    name="ウォーターワルフ", hp=55, attack=17, defense=9, level=4,
    element="水", speed=11,
    skills=[ALL_SKILLS[s] for s in ("ice_spear",) if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="water_wolf",
    rank=RANK_C,
)

POISON_ORC = Monster(
    name="ポイズンオーク", hp=70, attack=24, defense=16, level=5,
    element="毒", speed=7,
    skills=[ALL_SKILLS[s] for s in ("poison_dart", "weaken_armor") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="poison_orc",
    rank=RANK_B,
)

FROST_ELF = Monster(
    name="フロストエルフ", hp=60, attack=16, defense=12, level=5,
    element="氷", speed=12,
    skills=[ALL_SKILLS[s] for s in ("ice_spear", "heal", "speed_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="frost_elf",
    rank=RANK_B,
)

UNDEAD_WARRIOR = Monster(
    name="アンデッドウォリアー", hp=75, attack=25, defense=17, level=6,
    element="闇", speed=8,
    skills=[ALL_SKILLS[s] for s in ("dark_pulse", "stun_blow", "guard_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="undead_warrior",
    rank=RANK_B,
)

STORM_GOLEM = Monster(
    name="ストームゴーレム", hp=130, attack=35, defense=38, level=9,
    element="雷", speed=4,
    skills=[ALL_SKILLS[s] for s in ("earth_quake", "thunder_bolt", "guard_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="storm_golem",
    rank=RANK_A,
)

CELESTIAL_PANTHER = Monster(
    name="セレスティアルパンサー", hp=110, attack=38, defense=28, level=11,
    element="光", speed=19,
    skills=[ALL_SKILLS[s] for s in ("holy_light", "meteor_strike", "speed_up", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="celestial_panther",
    rank=RANK_S,
)

ABYSS_WATCHER = Monster(
    name="アビスウォッチャー",
    hp=95, attack=34, defense=24, level=9,
    element="闇", speed=17,
    skills=[ALL_SKILLS[s] for s in ("dark_pulse", "stun_blow", "speed_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="abyss_watcher",
    rank=RANK_A,
)

CINDER_SENTINEL = Monster(
    name="シンダーセンチネル",
    hp=140, attack=42, defense=42, level=11,
    element="火", speed=8,
    skills=[ALL_SKILLS[s] for s in ("meteor_strike", "guard_up", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="cinder_sentinel",
    rank=RANK_S,
)

ASHEN_DRAKE = Monster(
    name="アシェンドレイク",
    hp=125, attack=38, defense=30, level=10,
    element="火", speed=13,
    skills=[ALL_SKILLS[s] for s in ("dragon_breath", "thunder_bolt") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="ashen_drake",
    rank=RANK_A,
)

BLIGHTED_KNIGHT = Monster(
    name="ブライテッドナイト",
    hp=110, attack=36, defense=28, level=9,
    element="毒", speed=10,
    skills=[ALL_SKILLS[s] for s in ("poison_dart", "weaken_armor", "guard_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="blighted_knight",
    rank=RANK_A,
)

GRAVETIDE_HOLLOW = Monster(
    name="グレイブタイドホロウ",
    hp=90, attack=30, defense=18, level=8,
    element="闇", speed=11,
    skills=[ALL_SKILLS[s] for s in ("sleep_spell", "dark_pulse") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="gravetide_hollow",
    rank=RANK_B,
)

NAMELESS_KINGLING = Monster(
    name="ネームレスキングリング",
    hp=155, attack=48, defense=35, level=12,
    element="雷", speed=16,
    skills=[ALL_SKILLS[s] for s in ("thunder_bolt", "meteor_strike", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="nameless_kingling",
    rank=RANK_S,
)

PONTIFF_SHADE = Monster(
    name="ポンティフシェイド",
    hp=100, attack=32, defense=22, level=9,
    element="氷", speed=15,
    skills=[ALL_SKILLS[s] for s in ("ice_spear", "curse", "slow") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="pontiff_shade",
    rank=RANK_A,
)

# ------------------------------------------------------------
# ▼ 新モンスター
# ------------------------------------------------------------
DESERT_SCORPION = Monster(
    name="デザートスコーピオン", hp=60, attack=20, defense=14, level=4,
    element="毒", speed=9,
    skills=[ALL_SKILLS[s] for s in ("poison_dart", "stun_blow") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="desert_scorpion",
    rank=RANK_C,
)

SAND_WYRM = Monster(
    name="サンドワーム", hp=95, attack=28, defense=22, level=6,
    element="土", speed=14,
    skills=[ALL_SKILLS[s] for s in ("earth_quake", "power_up", "poison_dart") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="sand_wyrm",
    rank=RANK_B,
)

LAVA_ELEMENTAL = Monster(
    name="ラヴァエレメンタル", hp=110, attack=35, defense=30, level=8,
    element="火", speed=5,
    skills=[ALL_SKILLS[s] for s in ("meteor_strike", "dragon_breath") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="lava_elemental",
    rank=RANK_A,
)

CRYSTAL_DRAKE = Monster(
    name="クリスタルドレイク", hp=100, attack=33, defense=25, level=8,
    element="氷", speed=12,
    skills=[ALL_SKILLS[s] for s in ("ice_spear", "guard_up", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="crystal_drake",
    rank=RANK_A,
)

KRAKEN = Monster(
    name="クラーケン", hp=140, attack=38, defense=32, level=10,
    element="水", speed=7,
    skills=[ALL_SKILLS[s] for s in ("ice_spear", "heal", "slow") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="kraken",
    rank=RANK_A,
)

SKY_SERAPH = Monster(
    name="スカイセラフ", hp=120, attack=40, defense=28, level=11,
    element="光", speed=18,
    skills=[ALL_SKILLS[s] for s in ("holy_light", "thunder_bolt", "revive") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="sky_seraph",
    rank=RANK_S,
)

SPECTRAL_RAVEN = Monster(
    name="スペクトラルレイヴン",
    hp=55, attack=19, defense=11, level=4,
    element="闇", speed=20,
    skills=[ALL_SKILLS[s] for s in ("dark_pulse", "sleep_spell") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="spectral_raven",
    rank=RANK_C,
)

MIST_WRAITH = Monster(
    name="ミストレイス",
    hp=70, attack=24, defense=15, level=6,
    element="氷", speed=13,
    skills=[ALL_SKILLS[s] for s in ("ice_spear", "slow", "curse") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="mist_wraith",
    rank=RANK_B,
)

CORAL_HYDRA = Monster(
    name="コーラルハイドラ",
    hp=115, attack=32, defense=28, level=8,
    element="水", speed=9,
    skills=[ALL_SKILLS[s] for s in ("heal", "poison_dart", "guard_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="coral_hydra",
    rank=RANK_A,
)

IRON_JUGGERNAUT = Monster(
    name="アイアンジャガーノート",
    hp=140, attack=40, defense=45, level=10,
    element="土", speed=4,
    skills=[ALL_SKILLS[s] for s in ("earth_quake", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="iron_juggernaut",
    rank=RANK_A,
)

BLOOD_FIEND = Monster(
    name="ブラッドフィーンド",
    hp=105, attack=37, defense=23, level=9,
    element="闇", speed=14,
    skills=[ALL_SKILLS[s] for s in ("paralysis_shock", "dark_pulse", "regen") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="blood_fiend",
    rank=RANK_A,
)

MOONLIT_DRYAD = Monster(
    name="ムーンリットドリアード",
    hp=85, attack=26, defense=20, level=7,
    element="光", speed=16,
    skills=[ALL_SKILLS[s] for s in ("holy_light", "heal", "speed_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="moonlit_dryad",
    rank=RANK_B,
)

OBSIDIAN_TITAN = Monster(
    name="オブシディアンタイタン",
    hp=165, attack=48, defense=48, level=12,
    element="火", speed=6,
    skills=[ALL_SKILLS[s] for s in ("meteor_strike", "guard_up", "power_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_LATE,
    monster_id="obsidian_titan",
    rank=RANK_S,
)

ELECTRO_MANTIS = Monster(
    name="エレクトロマンティス",
    hp=90, attack=31, defense=18, level=8,
    element="雷", speed=22,
    skills=[ALL_SKILLS[s] for s in ("thunder_bolt", "stun_blow", "speed_up") if s in ALL_SKILLS],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="electro_mantis",
    rank=RANK_A,
)

ALL_MONSTERS = {
    "slime": SLIME,
    "goblin": GOBLIN,
    "wolf": WOLF,
    "slime_goblin_hybrid": SLIME_GOBLIN_HYBRID,
    "dragon_pup": DRAGON_PUP,
    "phoenix_chick": PHOENIX_CHICK,
    "orc_warrior": ORC_WARRIOR,
    "skeleton_archer": SKELETON_ARCHER,
    "elf_mage": ELF_MAGE,
    "troll_brute": TROLL_BRUTE,
    "mermaid_siren": MERMAID_SIREN,
    "thunder_eagle": THUNDER_EAGLE,
    "giant_golem": GIANT_GOLEM,
    "shadow_panther": SHADOW_PANTHER,
    "vampire_lord": VAMPIRE_LORD,
    "celestial_dragon": CELESTIAL_DRAGON,
    "water_wolf": WATER_WOLF,
    "poison_orc": POISON_ORC,
    "frost_elf": FROST_ELF,
    "undead_warrior": UNDEAD_WARRIOR,
    "storm_golem": STORM_GOLEM,
    "celestial_panther": CELESTIAL_PANTHER,
    "abyss_watcher": ABYSS_WATCHER,
    "cinder_sentinel": CINDER_SENTINEL,
    "ashen_drake": ASHEN_DRAKE,
    "blighted_knight": BLIGHTED_KNIGHT,
    "gravetide_hollow": GRAVETIDE_HOLLOW,
    "nameless_kingling": NAMELESS_KINGLING,
    "pontiff_shade": PONTIFF_SHADE,
    "desert_scorpion": DESERT_SCORPION,
    "sand_wyrm": SAND_WYRM,
    "lava_elemental": LAVA_ELEMENTAL,
    "crystal_drake": CRYSTAL_DRAKE,
    "kraken": KRAKEN,
    "sky_seraph": SKY_SERAPH,
    "spectral_raven": SPECTRAL_RAVEN,
    "mist_wraith": MIST_WRAITH,
    "coral_hydra": CORAL_HYDRA,
    "iron_juggernaut": IRON_JUGGERNAUT,
    "blood_fiend": BLOOD_FIEND,
    "moonlit_dryad": MOONLIT_DRYAD,
    "obsidian_titan": OBSIDIAN_TITAN,
    "electro_mantis": ELECTRO_MANTIS,
}
