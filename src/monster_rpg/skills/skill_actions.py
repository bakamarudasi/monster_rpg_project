from __future__ import annotations

from typing import Callable, Dict

from .skills import Skill
from ..monsters.monster_class import Monster


def deal_damage(target: Monster, damage: int) -> int:
    """Apply raw damage to target considering defense."""
    actual = max(1, damage - target.defense)
    target.hp -= actual
    print(f"{target.name} に {actual} のダメージ！ (残りHP: {max(0, target.hp)})")
    if target.hp <= 0:
        target.is_alive = False
        print(f"{target.name} は倒れた！")
    return actual


def simple_attack(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
    """Basic attack skill handler."""
    deal_damage(target, skill.power)
    if isinstance(skill.effect, str):
        from ..battle import apply_status  # local import to avoid circular
        apply_status(target, skill.effect)


def simple_heal(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
    """Basic healing skill handler."""
    before = target.hp
    target.hp = min(target.max_hp, target.hp + skill.power)
    healed = target.hp - before
    print(f"{target.name} のHPが {healed} 回復した！ (現在HP: {target.hp})")


def buff_speed_up(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
    amount = 5
    target.speed += amount

    def revert(m: Monster = target, a: int = amount) -> None:
        m.speed -= a

    if skill.duration > 0:
        target.status_effects.append({
            "name": skill.name,
            "remaining": skill.duration,
            "remove_func": revert,
        })
    print(f"{target.name} の素早さが上がった！")


def buff_atk_def_up(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
    amount = 5
    target.attack += amount
    target.defense += amount

    def revert(m: Monster = target, a: int = amount) -> None:
        m.attack -= a
        m.defense -= a

    if skill.duration > 0:
        target.status_effects.append({
            "name": skill.name,
            "remaining": skill.duration,
            "remove_func": revert,
        })
    print(f"{target.name} の攻撃と防御が上がった！")


def revive_target(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
    if target.is_alive:
        print(f"{target.name} はまだ倒れていない。")
        return
    target.is_alive = True
    target.hp = target.max_hp // 2
    print(f"{target.name} が復活した！ HPが {target.hp} に回復した。")


def _status_applier(name: str) -> Callable[[Monster, Monster, Skill], None]:
    def func(caster: Monster, target: Monster, skill: Skill, **kwargs) -> None:
        from ..battle import apply_status
        apply_status(target, name, skill.duration)
    return func


SKILL_EFFECT_MAP: Dict[str, Callable[..., None]] = {
    "speed_up": buff_speed_up,
    "atk_def_up": buff_atk_def_up,
    "revive": revive_target,
}

# Status effects and other simple flags
for _name in [
    "burn",
    "poison",
    "freeze",
    "paralyze",
    "regen",
    "stun",
    "sleep",
    "confuse",
    "fear",
    "blind",
    "slow",
    "silence",
    "curse",
]:
    SKILL_EFFECT_MAP.setdefault(_name, _status_applier(_name))
