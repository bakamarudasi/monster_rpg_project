from __future__ import annotations

from typing import Callable, Dict, List
import random

from .skills import Skill
from ..monsters.monster_class import Monster


def deal_damage(target: Monster, damage: int) -> int:
    """Apply raw damage considering defense."""
    actual = max(1, damage - target.defense)
    target.hp -= actual
    print(f"{target.name} に {actual} のダメージ！ (残りHP: {max(0, target.hp)})")
    if target.hp <= 0:
        target.is_alive = False
        print(f"{target.name} は倒れた！")
    return actual


def _handle_damage(caster: Monster, target: Monster, effect: dict) -> None:
    amount = int(effect.get("amount", 0))
    deal_damage(target, amount)


def _handle_heal(caster: Monster, target: Monster, effect: dict) -> None:
    stat = effect.get("stat", "hp")
    amount = effect.get("amount", 0)
    target.heal(stat, amount)


def _handle_buff(caster: Monster, target: Monster, effect: dict) -> None:
    stat = effect.get("stat")
    amount = int(effect.get("amount", 0))
    duration = int(effect.get("duration", 0))
    if stat:
        target.apply_buff(stat, amount, duration)


def _handle_status(caster: Monster, target: Monster, effect: dict) -> None:
    status = effect.get("status")
    duration = effect.get("duration")
    chance = float(effect.get("chance", 1.0))
    if status:
        if random.random() < chance:
            target.apply_status(status, duration)
        else:
            print(f"{target.name} は状態異常を受けなかった。")


def _handle_revive(caster: Monster, target: Monster, effect: dict) -> None:
    if target.is_alive:
        print(f"{target.name} はまだ倒れていない。")
        return
    amount = effect.get("amount", "half")
    target.is_alive = True
    if amount == "half":
        target.hp = target.max_hp // 2
    elif amount == "full":
        target.hp = target.max_hp
    else:
        try:
            target.hp = min(target.max_hp, int(amount))
        except (TypeError, ValueError):
            target.hp = target.max_hp // 2
    print(f"{target.name} が復活した！ HP: {target.hp}")


def _handle_cure_status(caster: Monster, target: Monster, effect: dict) -> None:
    status = effect.get("status")
    if status:
        target.cure_status(status)


HANDLERS: Dict[str, Callable[[Monster, Monster, dict], None]] = {
    "damage": _handle_damage,
    "heal": _handle_heal,
    "buff": _handle_buff,
    "status": _handle_status,
    "revive": _handle_revive,
    "cure_status": _handle_cure_status,
}


def apply_effects(
    caster: Monster,
    target: Monster,
    effects: List[dict],
) -> None:
    """Apply effect dictionaries to a target."""
    for eff in effects:
        handler = HANDLERS.get(eff.get("type"))
        if handler:
            handler(caster, target, eff)
        else:
            # fallback: status name shortcut
            name = eff.get("type")
            if name:
                _handle_status(caster, target, {"status": name, "duration": eff.get("duration")})

