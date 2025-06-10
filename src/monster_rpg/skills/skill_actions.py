"""Common skill action utilities."""

from __future__ import annotations
from typing import Callable

from ..monsters.monster_class import Monster


def deal_damage(target: Monster, amount: int) -> None:
    """Inflict raw damage to a monster and print result."""
    target.hp -= amount
    print(f"{target.name} に {amount} のダメージ！ (残りHP: {max(0, target.hp)})")
    if target.hp <= 0:
        target.is_alive = False
        print(f"{target.name} は倒れた！")


def simple_attack(caster: Monster, target: Monster, power: int) -> None:
    """Basic attack damage ignoring caster stats."""
    actual = max(1, power - target.defense)
    deal_damage(target, actual)


def simple_heal(target: Monster, amount: int) -> None:
    before = target.hp
    target.hp = min(target.max_hp, target.hp + amount)
    healed = target.hp - before
    print(f"{target.name} のHPが {healed} 回復した！ (現在HP: {target.hp})")


def _buff_speed(caster: Monster, target: Monster, skill) -> None:
    amount = 5
    target.speed += amount

    def revert(m=target, a=amount):
        m.speed -= a

    if skill.duration > 0:
        target.status_effects.append(
            {"name": skill.name, "remaining": skill.duration, "remove_func": revert}
        )
    print(f"{target.name} の能力が上がった！")


def _buff_atk_def(caster: Monster, target: Monster, skill) -> None:
    amount = 5
    target.attack += amount
    target.defense += amount

    def revert(m=target, a=amount):
        m.attack -= a
        m.defense -= a

    if skill.duration > 0:
        target.status_effects.append(
            {"name": skill.name, "remaining": skill.duration, "remove_func": revert}
        )
    print(f"{target.name} の能力が上がった！")


def _apply_status(caster: Monster, target: Monster, skill) -> None:
    from ..battle import apply_status

    apply_status(target, skill.effect, skill.duration)


def _revive(caster: Monster, target: Monster, skill) -> None:
    if target.is_alive:
        print(f"{target.name} はまだ倒れていない。")
        return
    target.is_alive = True
    target.hp = target.max_hp // 2
    print(f"{target.name} が復活した！ HPが半分回復した。")


# Map of effect names to handler functions
SKILL_EFFECT_MAP: dict[str, Callable[[Monster, Monster, object], None]] = {
    "speed_up": _buff_speed,
    "atk_def_up": _buff_atk_def,
    "poison": _apply_status,
    "burn": _apply_status,
    "freeze": _apply_status,
    "paralyze": _apply_status,
    "regen": _apply_status,
    "fear": _apply_status,
    "blind": _apply_status,
    "slow": _apply_status,
    "silence": _apply_status,
    "curse": _apply_status,
    "stun": _apply_status,
    "sleep": _apply_status,
    "confuse": _apply_status,
    "revive": _revive,
}
