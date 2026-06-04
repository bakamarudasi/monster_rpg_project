"""個体の個性（性格・才能）。

``is_rare`` / ``plus_value`` が「強さの底上げ」を担うのに対し、ここでは個体ごとの
"クセ" を表現する。

- 性格（Personality）… ステ傾向。あるステータスが上がり、別のステータスが下がる
  （またはクセ無しのバランス型）。攻撃/防御/素早さ/魔力に倍率として乗る。
- 才能（Talent）… 隠し才能を含む素質ランク。全ステに小さな倍率がかかる。最上位
  「鬼才」は野生では出ず、天才同士の配合からごく稀にしか生まれない＝収集の沼。

どちらも倍率は HP/MP には乗せず、派生4ステータス（attack/defense/speed/magic）にのみ
作用させることで、レベルアップやHP回復まわりのロジックには一切手を入れずに済むように
してある。
"""

from __future__ import annotations

import random
from dataclasses import dataclass

# 性格が触れるステータスの表示名（魔力なども含む派生4ステ）
STAT_LABELS: dict[str, str] = {
    "attack": "攻撃",
    "defense": "防御",
    "speed": "素早さ",
    "magic": "魔力",
}


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
        """stat -> 倍率の増減（+0.10 で +10%、-0.10 で -10%）。"""
        mods: dict[str, float] = {}
        if self.up:
            mods[self.up] = mods.get(self.up, 0.0) + self.magnitude
        if self.down:
            mods[self.down] = mods.get(self.down, 0.0) - self.magnitude
        return mods

    @property
    def effect_text(self) -> str:
        """「攻撃↑ 魔力↓」のような短い説明テキスト。"""
        if not self.up and not self.down:
            return "バランス型（クセなし）"
        parts = []
        if self.up:
            parts.append(f"{STAT_LABELS.get(self.up, self.up)}↑")
        if self.down:
            parts.append(f"{STAT_LABELS.get(self.down, self.down)}↓")
        return " ".join(parts)


# 各派生ステを上下に散らした、被りのない性格セット。バランス型を1つ含む。
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


@dataclass(frozen=True)
class Talent:
    """才能（素質ランク）。全ステに ``multiplier`` を乗せる。"""

    id: str
    name: str
    multiplier: float = 1.0
    weight: int = 0          # 野生抽選の重み（0 は野生に出ない＝隠し才能）
    hidden: bool = False     # 配合でしか到達できない最上位

    @property
    def bonus_percent(self) -> int:
        """+10 のような表示用の％値（端数は四捨五入）。"""
        return round((self.multiplier - 1.0) * 100)


# 下位から上位への順序。配合の継承・昇格判定はこの並びの index を使う。
TALENT_ORDER: tuple[str, ...] = (
    "common",
    "hardworking",
    "prodigy",
    "genius",
    "mastermind",
)

ALL_TALENTS: dict[str, Talent] = {
    "common": Talent("common", "凡才", multiplier=1.0, weight=100),
    "hardworking": Talent("hardworking", "努力家", multiplier=1.03, weight=45),
    "prodigy": Talent("prodigy", "秀才", multiplier=1.06, weight=15),
    "genius": Talent("genius", "天才", multiplier=1.10, weight=4),
    # 鬼才（隠し才能）… 野生では出現せず、天才同士の配合からのみごく稀に生まれる。
    "mastermind": Talent("mastermind", "鬼才", multiplier=1.18, weight=0, hidden=True),
}

DEFAULT_TALENT_ID = "common"

# 配合まわりの確率・しきい値
_PERSONALITY_MUTATION_CHANCE = 0.10   # 親と無関係な性格に変異する確率
_TALENT_UPGRADE_CHANCE = 0.15         # 高い方の親を1段超える確率
_TALENT_REGRESS_CHANCE = 0.10         # 高い方の親より1段下がる確率
_MASTERMIND_CHANCE = 0.08             # 天才×天才から鬼才が生まれる確率
_GENIUS_RANK = TALENT_ORDER.index("genius")
_MAX_NORMAL_RANK = _GENIUS_RANK       # 通常の昇格で到達できる上限（鬼才は別枠）


def get_personality(personality_id: str | None) -> Personality:
    """ID から性格を引く。未知の場合はバランス型にフォールバック。"""
    return ALL_PERSONALITIES.get(personality_id or "", ALL_PERSONALITIES[DEFAULT_PERSONALITY_ID])


def get_talent(talent_id: str | None) -> Talent:
    """ID から才能を引く。未知の場合は凡才にフォールバック。"""
    return ALL_TALENTS.get(talent_id or "", ALL_TALENTS[DEFAULT_TALENT_ID])


def random_personality_id() -> str:
    """性格を一様ランダムに選ぶ。"""
    return random.choice(list(ALL_PERSONALITIES.keys()))


def random_talent_id() -> str:
    """才能を重み付きで選ぶ（隠し才能 weight=0 は野生では出ない）。"""
    talents = [t for t in ALL_TALENTS.values() if t.weight > 0]
    weights = [t.weight for t in talents]
    return random.choices(talents, weights=weights, k=1)[0].id


def _talent_rank(talent_id: str | None) -> int:
    try:
        return TALENT_ORDER.index(talent_id or DEFAULT_TALENT_ID)
    except ValueError:
        return 0


def inherit_personality_id(parent1_id: str | None, parent2_id: str | None) -> str:
    """配合での性格継承。基本はどちらかの親から、稀に変異して別の性格になる。"""
    if random.random() < _PERSONALITY_MUTATION_CHANCE:
        return random_personality_id()
    pool = [pid for pid in (parent1_id, parent2_id) if pid in ALL_PERSONALITIES]
    if not pool:
        return DEFAULT_PERSONALITY_ID
    return random.choice(pool)


def inherit_talent_id(parent1_id: str | None, parent2_id: str | None) -> str:
    """配合での才能継承。

    良個体（高い才能）同士を掛け合わせるほど高才能の子が出やすい＝配合ループの核。
    基本は高い方の親の才能を引き継ぎ、一定確率で1段昇格／降格する。天才同士からは
    ごく稀に隠し才能「鬼才」が生まれる。
    """
    r1 = _talent_rank(parent1_id)
    r2 = _talent_rank(parent2_id)
    hi = max(r1, r2)

    # 天才×天才のときだけ、隠し才能「鬼才」の抽選を行う。
    if r1 >= _GENIUS_RANK and r2 >= _GENIUS_RANK and random.random() < _MASTERMIND_CHANCE:
        return "mastermind"

    roll = random.random()
    if roll < _TALENT_UPGRADE_CHANCE and hi < _MAX_NORMAL_RANK:
        rank = hi + 1
    elif roll < _TALENT_UPGRADE_CHANCE + _TALENT_REGRESS_CHANCE:
        rank = max(0, hi - 1)
    else:
        rank = hi

    rank = min(rank, _MAX_NORMAL_RANK)
    return TALENT_ORDER[rank]
