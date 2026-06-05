"""個体の個性（性格・個体値・才能）。

ポケモンの「せいかく／個体値／個体値ジャッジ」を下敷きにしたモデル。

- 性格（Personality）… ナチュラル相当。1ステ+10%/1ステ-10%（バランス型あり）。
  派生4ステ（攻撃/防御/素早さ/魔力）に倍率として乗る。
- 個体値（IV）… ステごとの隠し数値 0〜31。誕生時に固定され、レベルが上がるほど
  ステに効いてくる＝成長率。HPを含む5ステ（HP/攻撃/防御/魔力/素早さ）が対象。
- 才能（Talent）… 個体値の総合評価ラベル（凡才〜鬼才）。データではなく IV から導出。
  最上位「鬼才」は実質5Vで、配合での厳選でしか到達できない＝収集の沼。
- 鑑定（appraise）… 個体値の数値は普段伏せ、鑑定で「さいこう／すばらしい…」と開示。

倍率（性格）は HP/MP に乗せず派生4ステのみ、成長（個体値）は HP も含めて level_up の
取得量に作用させる、という役割分担にしてある。
"""

from __future__ import annotations

import random
from dataclasses import dataclass

# 性格が触れる派生4ステの表示名
STAT_LABELS: dict[str, str] = {
    "attack": "攻撃",
    "defense": "防御",
    "speed": "素早さ",
    "magic": "魔力",
}

# 個体値を持つ5ステ（HPを含む）と表示名
IV_STATS: tuple[str, ...] = ("hp", "attack", "defense", "magic", "speed")
IV_LABELS: dict[str, str] = {
    "hp": "HP",
    "attack": "攻撃",
    "defense": "防御",
    "magic": "魔力",
    "speed": "素早さ",
}
IV_MAX = 31
# 個体値が成長率に与える強さ。最大個体値で、そのステの毎レベル取得量が
# (1 + IV_GROWTH_STRENGTH) 倍になる（0個体値は等倍＝従来どおり）。
# ポケモンの個体値の効き（最大でステ十数%）に近い体感になるよう控えめに設定。
IV_GROWTH_STRENGTH = 0.2


# ---------------------------------------------------------------------------
# 性格（ナチュラル）
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Personality:
    """性格（ステ傾向）。``up`` を ``magnitude`` だけ上げ、``down`` を同率下げる。"""

    id: str
    name: str
    up: str | None = None
    down: str | None = None
    magnitude: float = 0.10

    @property
    def modifiers(self) -> dict[str, float]:
        mods: dict[str, float] = {}
        if self.up:
            mods[self.up] = mods.get(self.up, 0.0) + self.magnitude
        if self.down:
            mods[self.down] = mods.get(self.down, 0.0) - self.magnitude
        return mods

    @property
    def effect_text(self) -> str:
        if not self.up and not self.down:
            return "バランス型（クセなし）"
        parts = []
        if self.up:
            parts.append(f"{STAT_LABELS.get(self.up, self.up)}↑")
        if self.down:
            parts.append(f"{STAT_LABELS.get(self.down, self.down)}↓")
        return " ".join(parts)


ALL_PERSONALITIES: dict[str, Personality] = {
    p.id: p
    for p in (
        Personality("balanced", "まじめ"),
        Personality("brave", "ちからじまん", up="attack", down="magic"),
        Personality("clever", "かしこい", up="magic", down="attack"),
        Personality("stubborn", "がんこ", up="defense", down="speed"),
        Personality("hasty", "せっかち", up="speed", down="defense"),
        Personality("naughty", "わんぱく", up="attack", down="defense"),
        Personality("careful", "しんちょう", up="defense", down="attack"),
        Personality("quiet", "ものしずか", up="magic", down="speed"),
        Personality("cheerful", "ようき", up="speed", down="magic"),
    )
}

DEFAULT_PERSONALITY_ID = "balanced"
_PERSONALITY_MUTATION_CHANCE = 0.10  # 配合での性格変異率


def get_personality(personality_id: str | None) -> Personality:
    return ALL_PERSONALITIES.get(personality_id or "", ALL_PERSONALITIES[DEFAULT_PERSONALITY_ID])


def random_personality_id() -> str:
    return random.choice(list(ALL_PERSONALITIES.keys()))


def inherit_personality_id(
    parent1_id: str | None,
    parent2_id: str | None,
    everstone_parent: int | None = None,
) -> str:
    """配合での性格継承。

    ``everstone_parent`` に 1 または 2 を渡すと、その親の性格を確定継承する
    （かわらずのいし相当）。指定がなければ基本はどちらかの親から、稀に変異する。
    """
    if everstone_parent == 1 and parent1_id in ALL_PERSONALITIES:
        return parent1_id
    if everstone_parent == 2 and parent2_id in ALL_PERSONALITIES:
        return parent2_id
    if random.random() < _PERSONALITY_MUTATION_CHANCE:
        return random_personality_id()
    pool = [pid for pid in (parent1_id, parent2_id) if pid in ALL_PERSONALITIES]
    if not pool:
        return DEFAULT_PERSONALITY_ID
    return random.choice(pool)


# ---------------------------------------------------------------------------
# 個体値（IV）
# ---------------------------------------------------------------------------
def random_iv() -> int:
    return random.randint(0, IV_MAX)


def random_ivs() -> dict[str, int]:
    """全ステを 0〜31 で一様ロール（野生個体用）。"""
    return {s: random_iv() for s in IV_STATS}


def zero_ivs() -> dict[str, int]:
    """全ステ0の個体値（既定値＝従来挙動と完全互換）。"""
    return {s: 0 for s in IV_STATS}


def normalize_ivs(ivs: dict[str, int] | None) -> dict[str, int]:
    """欠損や範囲外を補正した個体値辞書を返す。"""
    ivs = ivs or {}
    return {s: max(0, min(IV_MAX, int(ivs.get(s, 0) or 0))) for s in IV_STATS}


def iv_total(ivs: dict[str, int]) -> int:
    return sum(int(ivs.get(s, 0) or 0) for s in IV_STATS)


def iv_max_total() -> int:
    return IV_MAX * len(IV_STATS)


def iv_ratio(ivs: dict[str, int]) -> float:
    return iv_total(ivs) / iv_max_total()


def iv_judge_label(value: int) -> str:
    """個体値ジャッジ風の評価語（ポケモン準拠）。"""
    v = max(0, min(IV_MAX, int(value)))
    if v == IV_MAX:
        return "さいこう"
    if v == IV_MAX - 1:
        return "すばらしい"
    if v >= 26:
        return "すごくいい"
    if v >= 16:
        return "まあまあ"
    if v >= 1:
        return "ふつう"
    return "苦手"


# 配合補助アイテム（ポケモン準拠）。持ち込むと個体値・性格の継承を制御できる。
DESTINY_KNOT_ITEM = "destiny_knot"   # あかいいと: 個体値の継承数 3→5
EVERSTONE_ITEM = "everstone"         # かわらずのいし: 親の性格を確定継承
POWER_ITEMS: dict[str, str] = {      # パワー系: 指定ステの個体値を確定継承
    "power_weight": "hp",
    "power_bracer": "attack",
    "power_belt": "defense",
    "power_lens": "magic",
    "power_anklet": "speed",
}
DEFAULT_INHERIT_COUNT = 3
DESTINY_KNOT_INHERIT_COUNT = 5


def inherit_ivs(
    p1_ivs: dict[str, int] | None,
    p2_ivs: dict[str, int] | None,
    inherit_count: int = DEFAULT_INHERIT_COUNT,
    power_stats: dict[str, int] | None = None,
) -> dict[str, int]:
    """配合での個体値遺伝（ポケモン準拠）。

    ``inherit_count`` 個のステを親から継承し（各ステごとにランダムな親を採用）、
    残りは新規に 0〜31 をロールする。

    ``power_stats`` は「パワー系アイテム」相当で、``{stat: 1 or 2}`` の形でそのステを
    どちらの親から確定継承するかを指定する（必ず継承枠に含まれる）。
    """
    p1 = normalize_ivs(p1_ivs)
    p2 = normalize_ivs(p2_ivs)
    power_stats = {s: v for s, v in (power_stats or {}).items() if s in IV_STATS}

    # 継承するステを決める。パワー系で固定したステは必ず含める。
    chosen: list[str] = list(dict.fromkeys(power_stats.keys()))
    remaining = [s for s in IV_STATS if s not in chosen]
    random.shuffle(remaining)
    cap = max(len(chosen), min(inherit_count, len(IV_STATS)))
    while len(chosen) < cap and remaining:
        chosen.append(remaining.pop())

    result: dict[str, int] = {}
    for s in IV_STATS:
        if s in chosen:
            if s in power_stats:
                src = p1 if power_stats[s] == 1 else p2
            else:
                src = random.choice((p1, p2))
            result[s] = int(src.get(s, 0))
        else:
            result[s] = random_iv()
    return result


# ---------------------------------------------------------------------------
# 才能（個体値の総合評価ラベル＝導出値）
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Talent:
    """個体値の総合評価。``min_ratio`` 以上の個体値比率でこのランクになる。"""

    id: str
    name: str
    min_ratio: float
    hidden: bool = False  # 鬼才＝実質5V。配合の厳選でしか到達できない隠しランク


# 下位→上位。talent_from_ivs はこの並びを下から評価していく。
TALENT_RANKS: tuple[Talent, ...] = (
    Talent("common", "凡才", 0.0),
    Talent("hardworking", "努力家", 0.5),
    Talent("prodigy", "秀才", 0.7),
    Talent("genius", "天才", 0.85),
    Talent("mastermind", "鬼才", 0.97, hidden=True),
)
ALL_TALENTS: dict[str, Talent] = {t.id: t for t in TALENT_RANKS}
DEFAULT_TALENT_ID = "common"


def get_talent(talent_id: str | None) -> Talent:
    return ALL_TALENTS.get(talent_id or "", ALL_TALENTS[DEFAULT_TALENT_ID])


def talent_from_ivs(ivs: dict[str, int] | None) -> Talent:
    """個体値から才能ランクを導出する。"""
    ratio = iv_ratio(normalize_ivs(ivs))
    best = TALENT_RANKS[0]
    for t in TALENT_RANKS:
        if ratio >= t.min_ratio:
            best = t
    return best


# ---------------------------------------------------------------------------
# 固有特性（パッシブ）。才能（個体値）が高い個体にだけ宿る隠し才能。
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Trait:
    """固有特性。``effect`` で効果の種類、``value`` でその強さを表す。

    effect の種類:
      - "exp"            … 獲得経験値が ×(1+value)（育成が早い）
      - "atb"            … 戦闘開始時にATBゲージ +value（先手を取りやすい）
      - "drop"           … パーティにいる間、敵ドロップ率が ×(1+value)
      - "element_attack" … 自分の属性での攻撃ダメージ ×(1+value)
    """

    id: str
    name: str
    description: str
    effect: str
    value: float = 0.0


ALL_TRAITS: dict[str, Trait] = {
    t.id: t
    for t in (
        Trait("fast_learner", "速学", "獲得経験値が1.5倍になる。", "exp", 0.5),
        Trait("vanguard", "先制", "戦闘開始時にATBゲージが大きく溜まった状態で始まる。", "atb", 40),
        Trait("lucky", "幸運", "パーティにいる間、敵のドロップ率が上がる。", "drop", 0.5),
        Trait("element_savant", "属性の申し子", "自分の属性での攻撃ダメージが2割増しになる。", "element_attack", 0.2),
        # --- 新ステ直結 ---
        Trait("critical_master", "会心の極み", "会心率が常時+15%される。", "crit", 15),
        Trait("evasive", "見切り", "回避率が常時+15%される。", "evasion", 15),
        Trait("magic_ward", "魔法の盾", "受ける魔法ダメージが25%軽減される。", "magic_ward", 0.25),
        Trait("mana_leech", "吸魔", "魔法ダメージを与えると、その一部だけMPを回復する。", "mana_leech", 0.25),
        # --- リアクティブ ---
        Trait("endure", "不屈", "致死ダメージを受けてもHP1で持ちこたえる（1戦闘1回）。", "endure", 1),
        Trait("lifesteal", "吸血", "与えた物理ダメージの25%だけHPを回復する。", "lifesteal", 0.25),
        Trait("pinch_power", "火事場の馬鹿力", "HPが減るほど物理攻撃の威力が上がる（最大+50%）。", "pinch_attack", 0.5),
        # --- 状態異常 ---
        Trait("afflictor", "状態異常の達人", "自分が与える状態異常の成功率が上がる。", "ailment_power", 0.5),
        Trait("venomous", "毒手", "物理攻撃時に確率で相手を毒状態にする。", "venom", 0.3),
        Trait("iron_will", "鉄の精神", "状態異常を受けにくくなる。", "ailment_ward", 0.5),
    )
}

# 才能ランク別の固有特性の付与率（凡才〜秀才は宿らない）
_TRAIT_CHANCE_BY_TALENT = {"genius": 0.5, "mastermind": 1.0}


def get_trait(trait_id: str | None) -> Trait | None:
    return ALL_TRAITS.get(trait_id) if trait_id else None


def random_trait_id() -> str:
    return random.choice(list(ALL_TRAITS.keys()))


def roll_trait_for_talent(talent_id: str | None) -> str | None:
    """才能ランクに応じて固有特性を抽選する（鬼才は確定、天才は半々）。"""
    chance = _TRAIT_CHANCE_BY_TALENT.get(talent_id or "", 0.0)
    if chance > 0.0 and random.random() < chance:
        return random_trait_id()
    return None


def inherit_trait(parent1_trait: str | None, parent2_trait: str | None, child_talent_id: str | None) -> str | None:
    """配合での固有特性継承。

    子が天才以上のときだけ宿り、親が特性を持っていれば受け継ぎやすい。なければ抽選。
    """
    if child_talent_id not in _TRAIT_CHANCE_BY_TALENT:
        return None
    parents = [t for t in (parent1_trait, parent2_trait) if t in ALL_TRAITS]
    if parents and random.random() < 0.7:
        return random.choice(parents)
    return roll_trait_for_talent(child_talent_id)
