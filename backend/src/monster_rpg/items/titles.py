from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Title:
    """Prefix title applied to equipment."""
    title_id: str
    name: str
    description: str
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    added_skills: List[str] = field(default_factory=list)

TITLE_SHARP = Title(
    title_id="sharp",
    name="鋭い",
    description="攻撃性能が高められている。",
    stat_bonuses={"attack": 5},
)

TITLE_STURDY = Title(
    title_id="sturdy",
    name="頑丈な",
    description="防御性能が高められている。",
    stat_bonuses={"defense": 5},
)

TITLE_QUICK = Title(
    title_id="quick",
    name="俊足の",
    description="素早さが少し上昇する。",
    stat_bonuses={"speed": 3},
)

TITLE_MAGICAL = Title(
    title_id="magical",
    name="魔力を秘めた",
    description="装備者に新たなスキルを授ける。",
    added_skills=["fireball"],
)

# --- カテゴリ1: 単体ステータス強化系 ---
TITLE_LIFE = Title("life", "生命の", "最大HPが上昇する。", {"hp": 10})
TITLE_MANA = Title("mana", "魔力の", "最大SPが上昇する。", {"sp": 10})
TITLE_SAGES = Title("sages", "賢者の", "魔法攻撃力が上昇する。", {"magic_attack": 5})
TITLE_GUARDIANS = Title("guardians", "守護の", "魔法防御力が上昇する。", {"magic_defense": 5})
TITLE_ASSASSINS = Title("assassins", "暗殺者の", "会心率が上昇する。", {"critical_rate": 5})
TITLE_NIMBLE = Title("nimble", "身かわしの", "回避率が上昇する。", {"evasion_rate": 5})

# --- カテゴリ2: 複合・トレードオフ系 ---
TITLE_BERSERKERS = Title("berserkers", "狂戦士の", "攻撃力が大幅に上がるが、防御力が犠牲になる。", {"attack": 10, "defense": -5})
TITLE_VETERANS = Title("veterans", "熟練の", "攻撃力と防御力がバランス良く上昇する。", {"attack": 3, "defense": 3})
TITLE_GALE = Title("gale", "疾風の", "素早さと回避能力が同時に高まる。", {"speed": 5, "evasion_rate": 3})
TITLE_GLASS_CANNON = Title("glass_cannon", "諸刃の", "絶大な攻撃力を得る代わりに、非常に打たれ弱くなる。", {"attack": 15, "hp": -10})

# --- カテゴリ3: スキル付与系 ---
TITLE_HEALING = Title("healing", "癒やしの", "回復スキル「ヒール」が使用可能になる。", added_skills=["heal"])
TITLE_FREEZING = Title("freezing", "氷結の", "氷属性の攻撃魔法が使用可能になる。", added_skills=["ice_bolt"])
TITLE_THUNDEROUS = Title("thunderous", "雷鳴の", "雷属性の攻撃魔法が使用可能になる。", added_skills=["lightning"])
TITLE_INSPIRING = Title("inspiring", "鼓舞する", "味方の能力を上昇させる補助スキルを授ける。", added_skills=["attack_up"])
TITLE_WEAKENING = Title("weakening", "弱体化の", "敵の能力を低下させる妨害スキルを授ける。", added_skills=["defense_down"])

# --- カテゴリ4: 耐性系 ---
TITLE_POISON_RESIST = Title("poison_resist", "毒耐性の", "毒状態になりにくくなる。", {"poison_resistance": 50})
TITLE_FIRE_WARD = Title("fire_ward", "火炎除けの", "火属性のダメージを軽減する。", {"fire_resistance": 30})

# --- カテゴリ5: デメリット系 ---
TITLE_RUSTED = Title("rusted", "錆びついた", "装備が劣化しており、性能が低下している。", {"attack": -5})
TITLE_CLUMSY = Title("clumsy", "不器用な", "動きが鈍くなり、攻撃も当たりにくくなる。", {"speed": -5, "critical_rate": -5})


# --- 全ての称号をまとめた辞書 ---
ALL_TITLES = {
    # 基本
    TITLE_SHARP.title_id: TITLE_SHARP,
    TITLE_STURDY.title_id: TITLE_STURDY,
    TITLE_QUICK.title_id: TITLE_QUICK,
    TITLE_MAGICAL.title_id: TITLE_MAGICAL,
    # カテゴリ1
    TITLE_LIFE.title_id: TITLE_LIFE,
    TITLE_MANA.title_id: TITLE_MANA,
    TITLE_SAGES.title_id: TITLE_SAGES,
    TITLE_GUARDIANS.title_id: TITLE_GUARDIANS,
    TITLE_ASSASSINS.title_id: TITLE_ASSASSINS,
    TITLE_NIMBLE.title_id: TITLE_NIMBLE,
    # カテゴリ2
    TITLE_BERSERKERS.title_id: TITLE_BERSERKERS,
    TITLE_VETERANS.title_id: TITLE_VETERANS,
    TITLE_GALE.title_id: TITLE_GALE,
    TITLE_GLASS_CANNON.title_id: TITLE_GLASS_CANNON,
    # カテゴリ3
    TITLE_HEALING.title_id: TITLE_HEALING,
    TITLE_FREEZING.title_id: TITLE_FREEZING,
    TITLE_THUNDEROUS.title_id: TITLE_THUNDEROUS,
    TITLE_INSPIRING.title_id: TITLE_INSPIRING,
    TITLE_WEAKENING.title_id: TITLE_WEAKENING,
    # カテゴリ4
    TITLE_POISON_RESIST.title_id: TITLE_POISON_RESIST,
    TITLE_FIRE_WARD.title_id: TITLE_FIRE_WARD,
    # カテゴリ5
    TITLE_RUSTED.title_id: TITLE_RUSTED,
    TITLE_CLUMSY.title_id: TITLE_CLUMSY,
}
