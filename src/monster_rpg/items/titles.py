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

ALL_TITLES = {
    TITLE_SHARP.title_id: TITLE_SHARP,
    TITLE_STURDY.title_id: TITLE_STURDY,
    TITLE_QUICK.title_id: TITLE_QUICK,
    TITLE_MAGICAL.title_id: TITLE_MAGICAL,
}
