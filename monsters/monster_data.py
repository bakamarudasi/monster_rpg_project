# monsters/monster_data.py

from dataclasses import dataclass
from typing import Dict

from .monster_class import (
    Monster,
    GROWTH_TYPE_AVERAGE,
    GROWTH_TYPE_EARLY,
    GROWTH_TYPE_LATE,
)
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
    drop_items=[(ALL_ITEMS["small_potion"], 0.5)],
    image_filename="slime.png"
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
    drop_items=[(ALL_ITEMS["medium_potion"], 0.1)],
    image_filename="wolf.png"
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
    rank=RANK_C ,# 例: 合成モンスターはCランク
    image_filename="slime_goblin_hybrid.png",
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
    rank=RANK_A, # 例: ドラゴンのこどもはAランク
    image_filename="dragon_pup.png",
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
    rank=RANK_S, # 例: 不死鳥のヒナはSランク
    image_filename="phoenix_chick.png",
)
ORC_WARRIOR = Monster(
    name="オークウォリアー",
    hp=60, attack=22, defense=15, level=4,
    element="土", speed=6,
    skills=[ALL_SKILLS["power_up"]] if "power_up" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="orc_warrior",
    rank=RANK_C,
    image_filename="orc_warrior.png",
)

SKELETON_ARCHER = Monster(
    name="スケルトンアーチャー",
    hp=45, attack=18, defense=8, level=3,
    element="闇", speed=9,
    skills=[ALL_SKILLS["poison_dart"]] if "poison_dart" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_AVERAGE,
    monster_id="skeleton_archer",
    rank=RANK_C,
    image_filename="skeleton_archer.png",
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
    image_filename="elf_mage.png",
)

TROLL_BRUTE = Monster(
    name="トロールブルート",
    hp=90, attack=28, defense=18, level=6,
    element="土", speed=4,
    skills=[ALL_SKILLS["regen"]] if "regen" in ALL_SKILLS else [],
    growth_type=GROWTH_TYPE_EARLY,
    monster_id="troll_brute",
    rank=RANK_B,
    image_filename="troll_brute.png",
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
    image_filename="water_wolf.png",
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


# ------------------------------------------------------------
# モンスター図鑑データ
# ------------------------------------------------------------

@dataclass
class MonsterBookEntry:
    monster_id: str
    description: str = ""
    location_hint: str = ""
    synthesis_hint: str = ""
    reward: int = 0


# 既存モンスターすべての図鑑データを用意する。
# 各エントリの詳細は必要に応じて編集してください。
MONSTER_BOOK_DATA: Dict[str, MonsterBookEntry] = {
    mid: MonsterBookEntry(monster_id=mid) for mid in ALL_MONSTERS.keys()
}

# サンプルとしていくつかのモンスターには簡単な説明を記載
MONSTER_BOOK_DATA["slime"].description = (
    "ぷるぷるした弱小モンスター。水属性で、初心者の相手に最適。"
)
MONSTER_BOOK_DATA["slime"].location_hint = "村の近くの草原などに出現"
MONSTER_BOOK_DATA["slime"].synthesis_hint = (
    "別種族と掛け合わせると特殊なモンスターが生まれるかも。"
)

MONSTER_BOOK_DATA["wolf"].description = "俊敏な牙獣。群れで行動することが多い。"
MONSTER_BOOK_DATA["wolf"].location_hint = "妖精の森の奥地や丘陵街道に出現"
MONSTER_BOOK_DATA["wolf"].synthesis_hint = "水に関連したモンスターと相性が良い。"

MONSTER_BOOK_DATA["water_wolf"].description = "水辺に潜むウルフ。鋭い爪で襲いかかる。"
MONSTER_BOOK_DATA["water_wolf"].location_hint = "神秘の湖に出現"
MONSTER_BOOK_DATA["water_wolf"].synthesis_hint = (
    "スライムとウルフを組み合わせると誕生するらしい。"
)


MONSTER_BOOK_DATA["slime_goblin_hybrid"].description = (
    "粘体と鬼童の性、異形として世に現る。ずる賢さとしぶとき身を兼備す。"
)
MONSTER_BOOK_DATA["slime_goblin_hybrid"].location_hint = "湿り気帯びし洞窟の奥深く、静かに棲みつく。"
MONSTER_BOOK_DATA["slime_goblin_hybrid"].synthesis_hint = (
    "斯くも稀なる組み合わせ、斯の魔物を生む。"
)

MONSTER_BOOK_DATA["dragon_pup"].description = (
    "いまだ成竜にあらずとも、炎の眷属たる威厳を漂わす龍の幼子なり。"
)
MONSTER_BOOK_DATA["dragon_pup"].location_hint = "火山の麓、またはドラゴンの古巣にて目撃談あり。"
MONSTER_BOOK_DATA["dragon_pup"].synthesis_hint = (
    "成体ドラゴンと交われば、真なる力に目覚めるとも…"
)

MONSTER_BOOK_DATA["phoenix_chick"].description = (
    "不死鳥の雛、まだ幼き身なれど、炎と再生の力をその身に宿す。"
)
MONSTER_BOOK_DATA["phoenix_chick"].location_hint = "古代の遺跡、灼熱の大地にて稀に発見さる。"
MONSTER_BOOK_DATA["phoenix_chick"].synthesis_hint = (
    "炎を纏いし魔物と交わる時、伝説の力を垣間見せる。"
)

MONSTER_BOOK_DATA["orc_warrior"].description = (
    "猛々しき力を誇るオークの戦士、凶暴にして恐れ知らず。"
)
MONSTER_BOOK_DATA["orc_warrior"].location_hint = "峻険なる山岳、或いは荒野の野営地に集うと聞く。"
MONSTER_BOOK_DATA["orc_warrior"].synthesis_hint = (
    "毒や粘りを有する魔物との交わり、凶悪なる変化を遂ぐ。"
)

MONSTER_BOOK_DATA["skeleton_archer"].description = (
    "骸骨の兵、弓を携え静かに闇を彷徨う不浄の存在。"
)
MONSTER_BOOK_DATA["skeleton_archer"].location_hint = "忘却されし墓地、暗き洞穴にて佇む姿あり。"
MONSTER_BOOK_DATA["skeleton_archer"].synthesis_hint = (
    "他の屍者と合せば、更なる死の軍勢となるやも。"
)

MONSTER_BOOK_DATA["elf_mage"].description = (
    "森に住まう精霊の使い手、古の魔法を紡ぐエルフの賢者なり。"
)
MONSTER_BOOK_DATA["elf_mage"].location_hint = "霊樹の森、あるいは神殿跡にて目撃さる。"
MONSTER_BOOK_DATA["elf_mage"].synthesis_hint = (
    "水・氷を司る者と合成すれば、精霊の奇跡を得るとも。"
)

MONSTER_BOOK_DATA["troll_brute"].description = (
    "巨躯にして粗暴なる山の怪物。力は比類なきも、知恵は拙し。"
)
MONSTER_BOOK_DATA["troll_brute"].location_hint = "山奥の洞窟、または古き遺跡にて棲息す。"
MONSTER_BOOK_DATA["troll_brute"].synthesis_hint = (
    "頑強なる者と混ぜれば、更なる剛の者となる。"
)

MONSTER_BOOK_DATA["mermaid_siren"].description = (
    "美声にて人を惑わす人魚なり。その歌声、時に死を招くとも云う。"
)
MONSTER_BOOK_DATA["mermaid_siren"].location_hint = "深き海の底、或いは静謐なる入り江に棲む。"
MONSTER_BOOK_DATA["mermaid_siren"].synthesis_hint = (
    "水と魅惑の性を持つ者と合わさる時、新たなる美が生まれる。"
)

MONSTER_BOOK_DATA["thunder_eagle"].description = (
    "雷光纏う天空の覇者、鷲のごとき威容で大空を翔ける。"
)
MONSTER_BOOK_DATA["thunder_eagle"].location_hint = "嵐吹き荒ぶ山頂、或いは雷雲の彼方に棲む。"
MONSTER_BOOK_DATA["thunder_eagle"].synthesis_hint = (
    "岩や巨人と合成せし時、さらなる嵐を呼ぶものと成らん。"
)

MONSTER_BOOK_DATA["giant_golem"].description = (
    "大地の意思宿りし巨像。重き歩み、あらゆる障壁となる。"
)
MONSTER_BOOK_DATA["giant_golem"].location_hint = "古の遺跡、岩山の影にて不動のまま眠る。"
MONSTER_BOOK_DATA["giant_golem"].synthesis_hint = (
    "雷や機械の精と交わり、新たなる命が吹き込まれる。"
)

MONSTER_BOOK_DATA["shadow_panther"].description = (
    "深き闇に紛れる黒豹。静寂を纏い、影より影へと舞う。"
)
MONSTER_BOOK_DATA["shadow_panther"].location_hint = "月夜の森、闇の谷間にて姿を消す。"
MONSTER_BOOK_DATA["shadow_panther"].synthesis_hint = (
    "光と闇の狭間にて、幻影と交わることで進化す。"
)

MONSTER_BOOK_DATA["vampire_lord"].description = (
    "永き夜を統べる不死の王。その眼光、命ある者を畏れさせる。"
)
MONSTER_BOOK_DATA["vampire_lord"].location_hint = "廃れし城館、夜の墓場にて徘徊す。"
MONSTER_BOOK_DATA["vampire_lord"].synthesis_hint = (
    "屍者や血を糧とする者との合成、強き呪いを生む。"
)

MONSTER_BOOK_DATA["celestial_dragon"].description = (
    "天空を司る伝説の龍。全ての理を体現せし古き守護者なり。"
)
MONSTER_BOOK_DATA["celestial_dragon"].location_hint = "雲海遥か上、神殿跡にて眠るという。"
MONSTER_BOOK_DATA["celestial_dragon"].synthesis_hint = (
    "稀なる者と交われば、未知なる進化が訪れるやもしれぬ。"
)

MONSTER_BOOK_DATA["poison_orc"].description = (
    "猛毒を纏いしオークの戦鬼。触れる者皆、命を落とすと云う。"
)
MONSTER_BOOK_DATA["poison_orc"].location_hint = "瘴気漂う沼沢や、陰鬱なる洞穴に棲む。"
MONSTER_BOOK_DATA["poison_orc"].synthesis_hint = (
    "毒や粘液、屍者との交わりで、なお強き変異を見せる。"
)

MONSTER_BOOK_DATA["frost_elf"].description = (
    "冷気の魔力纏いし精霊の末裔。氷の矢にて敵を討つ。"
)
MONSTER_BOOK_DATA["frost_elf"].location_hint = "雪深き森、氷の洞にて静かに息づく。"
MONSTER_BOOK_DATA["frost_elf"].synthesis_hint = (
    "氷霊や精霊と合成し、新たな奇跡を起こす。"
)

MONSTER_BOOK_DATA["undead_warrior"].description = (
    "死してなお魂を持つ戦士。その剣、恐れを知らず振るわれる。"
)
MONSTER_BOOK_DATA["undead_warrior"].location_hint = "古き戦場跡や闇の神殿にて彷徨う。"
MONSTER_BOOK_DATA["undead_warrior"].synthesis_hint = (
    "屍者や戦士の性を有する者と交わり、更なる戦鬼を生む。"
)

MONSTER_BOOK_DATA["storm_golem"].description = (
    "雷と大地の力が合わさりし巨像。暴風と共に歩む破壊者なり。"
)
MONSTER_BOOK_DATA["storm_golem"].location_hint = "雷鳴轟く峻嶺、嵐の只中に現る。"
MONSTER_BOOK_DATA["storm_golem"].synthesis_hint = (
    "電気や大地の精と合成すれば、さらなる力を得る。"
)

MONSTER_BOOK_DATA["celestial_panther"].description = (
    "天空の力を帯びし神秘の黒豹。星降る夜、その姿を見ること叶う。"
)
MONSTER_BOOK_DATA["celestial_panther"].location_hint = "空の裂け目、星の海にて現る。"
MONSTER_BOOK_DATA["celestial_panther"].synthesis_hint = (
    "天空や幻獣の性を持つ者との合成にて生まれる稀有なる獣なり。"
)

MONSTER_BOOK_DATA["abyss_watcher"].description = (
    "深淵を静かに見つめる守人。その眼、世界の均衡を測るという。"
)
MONSTER_BOOK_DATA["abyss_watcher"].location_hint = "闇深き底、廃墟の片隅にて孤独に佇む。"
MONSTER_BOOK_DATA["abyss_watcher"].synthesis_hint = (
    "闇や時空の理を司る者と合せば、さらなる神秘を得る。"
)

MONSTER_BOOK_DATA["cinder_sentinel"].description = (
    "灼熱の灰に身を包みし守護者。炎と灰、二つの相を持つ。"
)
MONSTER_BOOK_DATA["cinder_sentinel"].location_hint = "火山や焦土の地、常に熱を発し続ける。"
MONSTER_BOOK_DATA["cinder_sentinel"].synthesis_hint = (
    "炎や石、守りを司る者と合せし時、新たなる壁とならん。"
)

MONSTER_BOOK_DATA["ashen_drake"].description = (
    "灰の力を抱く小竜。滅びと再生、両極の性を備える。"
)
MONSTER_BOOK_DATA["ashen_drake"].location_hint = "火山帯、焼け野原の片隅にてその影を見る。"
MONSTER_BOOK_DATA["ashen_drake"].synthesis_hint = (
    "炎、風、竜の血を引く者と交われば真価を発揮す。"
)

MONSTER_BOOK_DATA["blighted_knight"].description = (
    "呪いを纏いし黒き騎士。腐敗せし鎧にて敵を圧倒す。"
)
MONSTER_BOOK_DATA["blighted_knight"].location_hint = "呪われし城郭、死の大地にて佇む。"
MONSTER_BOOK_DATA["blighted_knight"].synthesis_hint = (
    "屍者や毒、騎士の名を持つ者との合成により進化せん。"
)

MONSTER_BOOK_DATA["gravetide_hollow"].description = (
    "墓所の深き淵にて待ち受ける怪しき影。静けさの中、獲物を待つ。"
)
MONSTER_BOOK_DATA["gravetide_hollow"].location_hint = "忘却されし墓地の最深部、誰も知らぬ静寂の底。"
MONSTER_BOOK_DATA["gravetide_hollow"].synthesis_hint = (
    "屍者、水、闇の力を持つ者と交わりて進化するという。"
)

MONSTER_BOOK_DATA["nameless_kingling"].description = (
    "名もなき王の末裔。時を超えし力、今なお眠れる王威を帯びる。"
)
MONSTER_BOOK_DATA["nameless_kingling"].location_hint = "古の王家の墓所、廃都の影にて発見されし。"
MONSTER_BOOK_DATA["nameless_kingling"].synthesis_hint = (
    "王族や精霊、竜の血を引く者と交わればその真価を現す。"
)

MONSTER_BOOK_DATA["pontiff_shade"].description = (
    "司祭の怨嗟より生まれし影。呪詛と祈り、二つの相を持つ。"
)
MONSTER_BOOK_DATA["pontiff_shade"].location_hint = "呪われし教会、闇の祭壇にて人知れず佇む。"
MONSTER_BOOK_DATA["pontiff_shade"].synthesis_hint = (
    "闇や精霊、魔法を操る者と合成すれば新たな術を得る。"
)

MONSTER_BOOK_DATA["desert_scorpion"].description = (
    "砂海を駆ける狩人。猛毒の尾を振るい、敵を一閃に葬る。"
)
MONSTER_BOOK_DATA["desert_scorpion"].location_hint = "砂漠や蜃気楼の彼方、オアシス近辺に潜む。"
MONSTER_BOOK_DATA["desert_scorpion"].synthesis_hint = (
    "毒や大地、昆虫の性を持つ者との合成が妙。"
)

MONSTER_BOOK_DATA["sand_wyrm"].description = (
    "砂に潜みし大いなる蛇竜。地を震わせて地上に顕現す。"
)
MONSTER_BOOK_DATA["sand_wyrm"].location_hint = "砂漠の地底深く、静かなる闇の中。"
MONSTER_BOOK_DATA["sand_wyrm"].synthesis_hint = (
    "大地や竜、虫の血を引く者と交わりて強化す。"
)

MONSTER_BOOK_DATA["lava_elemental"].description = (
    "灼熱の溶岩に魂を持つ精霊。触れるもの総てを灰燼に帰す。"
)
MONSTER_BOOK_DATA["lava_elemental"].location_hint = "活火山の噴火口、または溶岩の洞に宿る。"
MONSTER_BOOK_DATA["lava_elemental"].synthesis_hint = (
    "炎や石、精霊と合わさる時、真の力を発揮す。"
)

MONSTER_BOOK_DATA["crystal_drake"].description = (
    "水晶の鱗を持つ小竜。美しくも苛烈なる攻撃性を秘める。"
)
MONSTER_BOOK_DATA["crystal_drake"].location_hint = "鉱山の奥底、または地下水晶宮殿にて目撃あり。"
MONSTER_BOOK_DATA["crystal_drake"].synthesis_hint = (
    "大地や竜、光を持つ者と交わりて新たな形を成す。"
)

MONSTER_BOOK_DATA["kraken"].description = (
    "深き海より現れし大いなる魔物。触手を以て船を沈めるとも。"
)
MONSTER_BOOK_DATA["kraken"].location_hint = "大海原の只中、海底遺跡にて目撃談多し。"
MONSTER_BOOK_DATA["kraken"].synthesis_hint = (
    "水や巨大、触手を持つ者との合成にてさらなる変異を遂げる。"
)

MONSTER_BOOK_DATA["sky_seraph"].description = (
    "空を舞う天の使い。慈悲と破壊、相反する力を持つという。"
)
MONSTER_BOOK_DATA["sky_seraph"].location_hint = "天空の神殿、または雲の上に姿現す。"
MONSTER_BOOK_DATA["sky_seraph"].synthesis_hint = (
    "天使や光、飛翔を得意とする者と合成せよ。"
)

MONSTER_BOOK_DATA["spectral_raven"].description = (
    "死霊の力宿る大鴉。その影、死の兆しを告げるという。"
)
MONSTER_BOOK_DATA["spectral_raven"].location_hint = "薄闇の森、或いは廃墟の上空を舞う。"
MONSTER_BOOK_DATA["spectral_raven"].synthesis_hint = (
    "屍者や闇、飛行の性を持つ者と合成にて進化す。"
)

MONSTER_BOOK_DATA["mist_wraith"].description = (
    "霧と化せし幽鬼。物理の刃をもすり抜け、姿を変える。"
)
MONSTER_BOOK_DATA["mist_wraith"].location_hint = "霧深き湖畔、幽玄なる森にて漂う。"
MONSTER_BOOK_DATA["mist_wraith"].synthesis_hint = (
    "霊体や水、幻影の者と交わればその性質変わる。"
)

MONSTER_BOOK_DATA["coral_hydra"].description = (
    "珊瑚より成りし多頭の魔獣。水中にてその真価を発揮す。"
)
MONSTER_BOOK_DATA["coral_hydra"].location_hint = "珊瑚礁の奥、浅瀬の洞にて見かけられる。"
MONSTER_BOOK_DATA["coral_hydra"].synthesis_hint = (
    "水、竜、再生の性を持つ者と合成にて強力となる。"
)

MONSTER_BOOK_DATA["iron_juggernaut"].description = (
    "鉄に魂宿りし機械の巨獣。防御と火力において並ぶ者なし。"
)
MONSTER_BOOK_DATA["iron_juggernaut"].location_hint = "古の工房、廃れた工場跡にて眠り続ける。"
MONSTER_BOOK_DATA["iron_juggernaut"].synthesis_hint = (
    "機械や鉄、巨人の性を持つ者と合成でさらに強固な体となる。"
)

MONSTER_BOOK_DATA["blood_fiend"].description = (
    "血を糧とせし魔獣。夜毎に獲物の香りを嗅ぎ分けては徘徊す。"
)
MONSTER_BOOK_DATA["blood_fiend"].location_hint = "夜の森、または吸血鬼の館近辺に出没す。"
MONSTER_BOOK_DATA["blood_fiend"].synthesis_hint = (
    "血や屍、吸収を得意とする者と合成すべし。"
)

MONSTER_BOOK_DATA["moonlit_dryad"].description = (
    "月光を浴びて輝く精霊樹。癒やしの力を内に秘める。"
)
MONSTER_BOOK_DATA["moonlit_dryad"].location_hint = "月夜の森、聖域の奥深くにて現れる。"
MONSTER_BOOK_DATA["moonlit_dryad"].synthesis_hint = (
    "精霊や木、光の性を持つ者と交わりて新たな命芽生えん。"
)

MONSTER_BOOK_DATA["obsidian_titan"].description = (
    "黒曜石の鎧纏いし巨人。その身、あらゆる攻撃を退ける。"
)
MONSTER_BOOK_DATA["obsidian_titan"].location_hint = "火山帯の地下、炎の眠る深部にて鎮座す。"
MONSTER_BOOK_DATA["obsidian_titan"].synthesis_hint = (
    "岩や炎、巨人の性を持つ者と合成し防御特化す。"
)

MONSTER_BOOK_DATA["electro_mantis"].description = (
    "雷を操る鎌切の化身。その動き、稲妻の如し。"
)
MONSTER_BOOK_DATA["electro_mantis"].location_hint = "雷雨降りし森、或いは廃れし発電所に棲む。"
MONSTER_BOOK_DATA["electro_mantis"].synthesis_hint = (
    "虫や雷、速さを重んずる者と合成で特異な進化を遂ぐ。"
)
