from __future__ import annotations

from typing import Callable, Dict, List, Optional, Any
import random

from .skills import Skill
from ..monsters.monster_class import Monster

# copied from battle to avoid circular import
ELEMENTAL_MULTIPLIERS = {
    ("火", "風"): 1.5,
    ("風", "水"): 1.5,
    ("水", "火"): 1.5,
}


def is_defending(monster: Monster) -> bool:
    """Check if the monster is in defending state."""
    return any(e.get("name") == "defending" for e in monster.status_effects)


def deal_damage(target: Monster, damage: int, log: List[Dict[str, str]] | None) -> int:
    """Apply raw damage considering defense."""
    if log is None:
        log = []
    actual = max(1, damage - target.defense)
    if is_defending(target):
        actual = int(actual * 0.5)
    target.hp -= actual
    log.append({'type': 'info', 'message': f"{target.name} took {actual} damage! (HP: {max(0, target.hp)})"})
    if target.hp <= 0:
        target.is_alive = False
        log.append({'type': 'info', 'message': f"{target.name} fainted!"})
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
    if is_defending(target):
        damage = int(damage * 0.5)
    return max(1, damage)


def _handle_damage(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if context is None:
        context = {}
    if log is None:
        log = []
    if skill is not None:
        damage = calculate_skill_damage(caster, target, skill)
        target.hp -= damage
        log.append({'type': 'info', 'message': f"{target.name} took {damage} damage! (HP: {max(0, target.hp)})"})
        if target.hp <= 0:
            target.is_alive = False
            log.append({'type': 'info', 'message': f"{target.name} fainted!"})
        else:
            # Counter status check
            if any(e["name"] == "counter_stance" for e in target.status_effects):
                log.append({'type': 'info', 'message': f"{target.name} counters!"})
                # For simplicity, fixed damage counterattack here
                counter_damage = int(caster.total_attack() * 0.5) # Counterattack with half of caster's attack
                caster.hp -= counter_damage
                log.append({'type': 'info', 'message': f"{caster.name} took {counter_damage} damage! (HP: {max(0, caster.hp)})"})
                if caster.hp <= 0:
                    caster.is_alive = False
                    log.append({'type': 'info', 'message': f"{caster.name} fainted!"})
        context["last_damage_dealt"] = damage  # Store damage dealt
    else:
        amount = effect.get("amount", 0)
        if isinstance(amount, str) and context is not None:
            amount = int(context.get(amount, 0))
        else:
            amount = int(amount)
        actual_damage = deal_damage(target, amount)
        if target.hp <= 0:
            target.is_alive = False
            log.append({'type': 'info', 'message': f"{target.name} fainted!"})
        else:
            # Counter status check
            if any(e["name"] == "counter_stance" for e in target.status_effects):
                log.append({'type': 'info', 'message': f"{target.name} counters!"})
                counter_damage = int(caster.total_attack() * 0.5) # Counterattack with half of caster's attack
                caster.hp -= counter_damage
                log.append({'type': 'info', 'message': f"{caster.name} took {counter_damage} damage! (HP: {max(0, caster.hp)})"})
                if caster.hp <= 0:
                    caster.is_alive = False
                    log.append({'type': 'info', 'message': f"{caster.name} fainted!"})
        context["last_damage_dealt"] = actual_damage  # Store damage dealt

def _handle_heal_from_damage(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if context is None:
        context = {}
    if log is None:
        log = []
    percent = float(effect.get("percent", 0))
    last_damage_dealt = context.get("last_damage_dealt", 0)
    heal_amount = int(last_damage_dealt * percent)
    if heal_amount > 0:
        caster.heal("hp", heal_amount)
        log.append({'type': 'info', 'message': f"{caster.name} は {heal_amount} HPを吸収した！ (残りHP: {caster.hp})"})



def _handle_heal(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    stat = effect.get("stat", "hp")
    amount = effect.get("amount", 0)
    target.heal(stat, amount)
    log.append({'type': 'info', 'message': f"{target.name} の{stat}が {amount} 回復した！"})


def _handle_buff(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    stat = effect.get("stat")
    amount = int(effect.get("amount", 0))
    duration = int(effect.get("duration", 0))
    if stat:
        target.apply_buff(stat, amount, duration)
        log.append({'type': 'info', 'message': f"{target.name} の{stat}が {amount} 上がった！ ({duration}ターン)"})


def _handle_buff_percent(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    stat = effect.get("stat")
    amount = float(effect.get("amount", 0))
    duration = int(effect.get("duration", 0))
    if stat:
        target.apply_buff_percent(stat, amount, duration)
        log.append({'type': 'info', 'message': f"{target.name} の{stat}が {amount*100:.0f}% 上がった！ ({duration}ターン)"})


def _handle_status(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    status = effect.get("status")
    duration = effect.get("duration")
    chance = float(effect.get("chance", 1.0))
    if status:
        if random.random() < chance:
            target.apply_status(status, log, duration)
        else:
            log.append({'type': 'info', 'message': f"{target.name} resisted the status effect."})



def _handle_revive(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    if target.is_alive:
        log.append({'type': 'info', 'message': f"{target.name} はまだ倒れていない。"})
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
    log.append({'type': 'info', 'message': f"{target.name} が復活した！ HP: {target.hp}"})


def _handle_cure_status(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    status = effect.get("status")
    if status:
        try:
            target.cure_status(status, log)
        except TypeError:
            target.cure_status(status)


def _handle_charge(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    """Apply a charging state that will trigger another skill next turn."""
    release_id = effect.get("release_skill_id")
    duration = int(effect.get("duration", 2))
    target.apply_status("charging", log, duration)
    if target.status_effects and target.status_effects[-1]["name"] == "charging":
        target.status_effects[-1]["release_skill_id"] = release_id


def _handle_hp_cost_percent(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    """Reduce caster HP by a percentage of max HP."""
    percent = float(effect.get("percent", 0))
    amount = int(caster.max_hp * percent)
    caster.hp -= amount
    if context is not None:
        context["last_hp_cost"] = amount
    log.append({'type': 'info', 'message': f"{caster.name} はHPを {amount} 消費した (残りHP: {max(0, caster.hp)})"})
    if caster.hp <= 0:
        caster.hp = 0
        caster.is_alive = False
        log.append({'type': 'info', 'message': f"{caster.name} は倒れた！"})


def _handle_self_ko(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    """Knock the caster out immediately."""
    caster.hp = 0
    caster.is_alive = False
    if context is not None:
        context["self_ko"] = True
    log.append({'type': 'info', 'message': f"{caster.name} は自滅した！"})


def _handle_mp_drain(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    if log is None:
        log = []
    amount = int(effect.get("amount", 0))
    target.mp = max(0, target.mp - amount)
    caster.mp = min(caster.max_mp, caster.mp + amount) # Caster gains MP, capped at max_mp
    log.append({'type': 'info', 'message': f"{target.name} のMPが {amount} 減少した！ (残りMP: {max(0, target.mp)})"})
    log.append({'type': 'info', 'message': f"{caster.name} はMPを {amount} 吸収した！ (残りMP: {caster.mp})"})


HANDLERS: Dict[str, Callable[[Monster, Monster, dict, List[Dict[str, str]], Optional[Skill], Optional[Dict[str, Any]]], None]] = {
    "damage": _handle_damage,
    "heal": _handle_heal,
    "buff": _handle_buff,
    "buff_percent": _handle_buff_percent,
    "status": _handle_status,
    "revive": _handle_revive,
    "cure_status": _handle_cure_status,
    "charge": _handle_charge,
    "hp_cost_percent": _handle_hp_cost_percent,
    "self_ko": _handle_self_ko,
    "heal_from_damage": _handle_heal_from_damage,
    "mp_drain": _handle_mp_drain,
}


def apply_effects(
    caster: Monster,
    target: Monster,
    effects: List[dict],
    skill: Optional[Skill] = None,
    log: Optional[List[Dict[str, str]]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply effect dictionaries to a target."""
    if context is None:
        context = {}
    if log is None:
        log = []

    for eff in effects:
        handler = HANDLERS.get(eff.get("type"))
        if handler:
            # Pass log to handlers that accept it
            if handler in [_handle_damage, _handle_heal, _handle_buff, _handle_buff_percent, _handle_status, _handle_revive, _handle_cure_status, _handle_charge, _handle_hp_cost_percent, _handle_self_ko, _handle_heal_from_damage, _handle_mp_drain]:
                handler(caster, target, eff, log, skill, context)
            else:
                handler(caster, target, eff, skill, context)
        else:
            # fallback: status name shortcut
            name = eff.get("type")
            if name:
                _handle_status(caster, target, {"status": name, "duration": eff.get("duration")}, log, skill, context)
    return context

