from __future__ import annotations

from typing import Callable, Dict, List, Optional, Any
import random

# copied from battle to avoid circular import
ELEMENTAL_MULTIPLIERS = {
    ("火", "風"): 1.5,
    ("風", "水"): 1.5,
    ("水", "火"): 1.5,
}

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


def calculate_skill_damage(caster: Monster, target: Monster, skill: Skill) -> int:
    """Calculate damage for a skill taking caster stats and elements into account."""
    if skill.category == "魔法":
        base_stat = getattr(caster, "magic", 0)
    else:
        base_stat = caster.total_attack()

    base = base_stat + skill.power - target.total_defense()
    damage = max(1, base)

    mult = ELEMENTAL_MULTIPLIERS.get((caster.element, target.element))
    if mult is None:
        rev = ELEMENTAL_MULTIPLIERS.get((target.element, caster.element))
        mult = 0.5 if rev is not None else 1.0

    damage = int(damage * mult)
    return max(1, damage)


def _handle_damage(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    if skill is not None:
        damage = calculate_skill_damage(caster, target, skill)
        target.hp -= damage
        print(f"{target.name} に {damage} のダメージ！ (残りHP: {max(0, target.hp)})")
        if target.hp <= 0:
            target.is_alive = False
            print(f"{target.name} は倒れた！")
    else:
        amount = effect.get("amount", 0)
        if isinstance(amount, str) and context is not None:
            amount = int(context.get(amount, 0))
        else:
            amount = int(amount)
        deal_damage(target, amount)


def _handle_heal(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    stat = effect.get("stat", "hp")
    amount = effect.get("amount", 0)
    target.heal(stat, amount)


def _handle_buff(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    stat = effect.get("stat")
    amount = int(effect.get("amount", 0))
    duration = int(effect.get("duration", 0))
    if stat:
        target.apply_buff(stat, amount, duration)


def _handle_status(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    status = effect.get("status")
    duration = effect.get("duration")
    chance = float(effect.get("chance", 1.0))
    if status:
        if random.random() < chance:
            target.apply_status(status, duration)
        else:
            print(f"{target.name} は状態異常を受けなかった。")


def _handle_revive(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
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


def _handle_cure_status(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    status = effect.get("status")
    if status:
        target.cure_status(status)


def _handle_charge(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Apply a charging state that will trigger another skill next turn."""
    release_id = effect.get("release_skill_id")
    duration = int(effect.get("duration", 2))
    target.apply_status("charging", duration)
    if target.status_effects and target.status_effects[-1]["name"] == "charging":
        target.status_effects[-1]["release_skill_id"] = release_id


def _handle_hp_cost_percent(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Reduce caster HP by a percentage of max HP."""
    percent = float(effect.get("percent", 0))
    amount = int(caster.max_hp * percent)
    caster.hp -= amount
    if context is not None:
        context["last_hp_cost"] = amount
    print(f"{caster.name} はHPを {amount} 消費した (残りHP: {max(0, caster.hp)})")
    if caster.hp <= 0:
        caster.hp = 0
        caster.is_alive = False
        print(f"{caster.name} は倒れた！")


def _handle_self_ko(
    caster: Monster,
    target: Monster,
    effect: dict,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    """Knock the caster out immediately."""
    caster.hp = 0
    caster.is_alive = False
    if context is not None:
        context["self_ko"] = True
    print(f"{caster.name} は自滅した！")


HANDLERS: Dict[str, Callable[[Monster, Monster, dict, Optional[Skill], Optional[dict[str, Any]]], None]] = {
    "damage": _handle_damage,
    "heal": _handle_heal,
    "buff": _handle_buff,
    "status": _handle_status,
    "revive": _handle_revive,
    "cure_status": _handle_cure_status,
    "charge": _handle_charge,
    "hp_cost_percent": _handle_hp_cost_percent,
    "self_ko": _handle_self_ko,
}


def apply_effects(
    caster: Monster,
    target: Monster,
    effects: List[dict],
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Apply effect dictionaries to a target."""
    if context is None:
        context = {}
    for eff in effects:
        handler = HANDLERS.get(eff.get("type"))
        if handler:
            handler(caster, target, eff, skill, context)
        else:
            # fallback: status name shortcut
            name = eff.get("type")
            if name:
                _handle_status(caster, target, {"status": name, "duration": eff.get("duration")}, skill, context)
    return context

