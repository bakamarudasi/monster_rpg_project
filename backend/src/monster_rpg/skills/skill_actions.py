from __future__ import annotations

from typing import Callable, Dict, List, Optional, Any
import random

from .skills import Skill
from ..monsters.monster_class import Monster
from ..elements import (
    ELEMENTAL_MULTIPLIERS,
    elemental_multiplier,
    field_multiplier,
    set_field,
)


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
    actual = target.absorb_with_shield(actual, log)
    target.hp -= actual
    if actual > 0:
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

    damage = int(damage * elemental_multiplier(caster.element, target.element))
    # フィールド（天候）補正：術者の属性が場と一致していれば増幅
    damage = int(damage * field_multiplier(caster.element))
    if is_defending(target):
        damage = int(damage * 0.5)
    return max(1, damage)


NEGATIVE_STATUSES = {
    "burn", "poison", "spore_poison", "freeze", "paralyze", "fear", "blind",
    "slow", "silence", "curse", "stun", "sleep", "confuse", "doom", "cant_attack",
}


def _bonus_multiplier(caster: Monster, target: Monster, effect: dict) -> float:
    """ダメージ効果の追加倍率（状態異常シナジー・追い討ち・背水）を計算する。

    対応するキーが無ければ 1.0 を返すので、通常のダメージ効果には影響しない。
    """
    mult = 1.0
    # 相手の（負の）状態異常の数だけ威力アップ
    per = float(effect.get("bonus_per_status", 0) or 0)
    if per:
        count = sum(1 for e in target.status_effects if e["name"] in NEGATIVE_STATUSES)
        mult *= 1.0 + per * count
    # 特定の状態異常がかかっていれば威力アップ（追い討ち）
    trigger = effect.get("bonus_if_status")
    if trigger:
        names = [trigger] if isinstance(trigger, str) else list(trigger)
        if any(e["name"] in names for e in target.status_effects):
            mult *= float(effect.get("status_multiplier", 1.5))
    # 背水：自分のHPが減っているほど威力アップ（desperation=1.0 で瀕死時 +100%）
    desp = float(effect.get("desperation", 0) or 0)
    if desp and caster.max_hp > 0:
        missing = 1.0 - (max(0, caster.hp) / caster.max_hp)
        mult *= 1.0 + desp * missing
    return mult


def _apply_counter(caster: Monster, target: Monster, log: List[Dict[str, str]]) -> None:
    """target がカウンター構えなら caster に反撃ダメージを与える。"""
    if any(e["name"] == "counter_stance" for e in target.status_effects):
        log.append({'type': 'info', 'message': f"{target.name} counters!"})
        counter_damage = int(caster.total_attack() * 0.5)  # 攻撃力の半分で反撃
        counter_damage = caster.absorb_with_shield(counter_damage, log)
        caster.hp -= counter_damage
        log.append({'type': 'info', 'message': f"{caster.name} took {counter_damage} damage! (HP: {max(0, caster.hp)})"})
        if caster.hp <= 0:
            caster.is_alive = False
            log.append({'type': 'info', 'message': f"{caster.name} fainted!"})


def _inflict(caster: Monster, target: Monster, damage: int, log: List[Dict[str, str]], context: Dict[str, Any]) -> int:
    """バリア → HP の順にダメージを与え、撃破判定とカウンターを処理する。"""
    damage = target.absorb_with_shield(damage, log)
    if damage > 0:
        target.hp -= damage
        log.append({'type': 'info', 'message': f"{target.name} took {damage} damage! (HP: {max(0, target.hp)})"})
    if target.hp <= 0:
        target.is_alive = False
        log.append({'type': 'info', 'message': f"{target.name} fainted!"})
    elif damage > 0:
        _apply_counter(caster, target, log)
    context["last_damage_dealt"] = damage
    return damage


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
    bonus = _bonus_multiplier(caster, target, effect)
    if skill is not None:
        damage = calculate_skill_damage(caster, target, skill)
        damage = max(1, int(damage * bonus))
        _inflict(caster, target, damage, log, context)
    else:
        amount = effect.get("amount", 0)
        if isinstance(amount, str):
            amount = int(context.get(amount, 0))
        else:
            amount = int(amount)
        amount = max(1, int(amount * bonus))
        # pass log so damage events are recorded and no error is raised
        actual_damage = deal_damage(target, amount, log)
        context["last_damage_dealt"] = actual_damage  # Store damage dealt
        if target.is_alive:
            _apply_counter(caster, target, log)

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


def _handle_permanent_stat(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """種アイテム等による恒久的なステータス上昇。"""
    if log is None:
        log = []
    stat = effect.get("stat", "attack")
    amount = int(effect.get("amount", 0))
    applied = target.add_permanent_stat(stat, amount)
    labels = {
        "attack": "こうげき", "defense": "しゅび", "speed": "すばやさ", "magic": "まりょく",
        "hp": "さいだいHP", "max_hp": "さいだいHP", "mp": "さいだいMP", "max_mp": "さいだいMP",
    }
    label = labels.get(stat, stat)
    if applied:
        log.append({'type': 'info', 'message': f"{target.name} の{label}が永続的に {applied} 上がった！"})


def _handle_multi_hit(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """同じ相手に複数回ヒットする連撃。ヒット数は min_hits〜max_hits でランダム。"""
    if context is None:
        context = {}
    if log is None:
        log = []
    min_hits = int(effect.get("min_hits", effect.get("hits", 2)))
    max_hits = int(effect.get("max_hits", effect.get("hits", min_hits)))
    if max_hits < min_hits:
        max_hits = min_hits
    hits = random.randint(min_hits, max_hits)
    bonus = _bonus_multiplier(caster, target, effect)
    log.append({'type': 'info', 'message': f"{caster.name} の連撃！ {hits} 回ヒット！"})
    total = 0
    for _ in range(hits):
        if not target.is_alive:
            break
        if skill is not None:
            dmg = calculate_skill_damage(caster, target, skill)
        else:
            dmg = max(1, caster.total_attack() + int(effect.get("amount", 0)) - target.total_defense())
        dmg = max(1, int(dmg * bonus))
        total += _inflict(caster, target, dmg, log, context)
    context["last_damage_dealt"] = total


def _handle_percent_damage(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """防御を無視して最大HP（または現在HP）の一定割合のダメージを与える。"""
    if context is None:
        context = {}
    if log is None:
        log = []
    percent = float(effect.get("percent", 0.25))
    base_val = target.hp if effect.get("based_on") == "current_hp" else target.max_hp
    damage = max(1, int(base_val * percent))
    damage = target.absorb_with_shield(damage, log)
    if damage > 0:
        target.hp -= damage
        log.append({'type': 'info', 'message': f"{target.name} は割合ダメージ {damage} を受けた！ (残りHP: {max(0, target.hp)})"})
    if target.hp <= 0:
        target.is_alive = False
        log.append({'type': 'info', 'message': f"{target.name} fainted!"})
    context["last_damage_dealt"] = damage


def _handle_transfer_status(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """術者自身の（負の）状態異常を相手へ移し替える。"""
    if log is None:
        log = []
    names = effect.get("statuses")
    moved: List[str] = []
    for e in list(caster.status_effects):
        nm = e["name"]
        if names is not None:
            if nm not in names:
                continue
        elif nm not in NEGATIVE_STATUSES:
            continue
        remove_cb = e.get("remove_func")
        caster.status_effects.remove(e)
        if callable(remove_cb):
            try:
                remove_cb()
            except Exception:
                pass
        target.apply_status(nm, log, e.get("remaining"))
        moved.append(nm)
    if moved:
        log.append({'type': 'info', 'message': f"{caster.name} は状態異常を {target.name} に移し替えた！"})
    else:
        log.append({'type': 'info', 'message': f"{caster.name} には移し替えられる状態異常がない。"})


def _handle_atb_change(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """対象の ATB（行動）ゲージを増減・設定する。ディレイやヘイストに使う。"""
    if log is None:
        log = []
    if "set" in effect:
        target.atb_gauge = max(0, min(100, int(effect["set"])))
        log.append({'type': 'info', 'message': f"{target.name} の行動ゲージが {target.atb_gauge} になった！"})
        return
    amount = int(effect.get("amount", 0))
    target.atb_gauge = max(0, min(100, target.atb_gauge + amount))
    if amount >= 0:
        log.append({'type': 'info', 'message': f"{target.name} の行動が早まった！ (ゲージ: {target.atb_gauge})"})
    else:
        log.append({'type': 'info', 'message': f"{target.name} の行動が遅れた！ (ゲージ: {target.atb_gauge})"})


def _handle_change_element(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """対象の属性を一定ターンの間だけ書き換える（弱点づくり・耐性づくり）。"""
    if log is None:
        log = []
    new_element = effect.get("element")
    duration = int(effect.get("duration", 3))
    old_element = target.element
    target.element = new_element

    def revert(m: Monster = target, e=old_element) -> None:
        m.element = e

    if duration > 0:
        target.status_effects.append({
            "name": "element_shift",
            "remaining": duration,
            "remove_func": revert,
        })
    log.append({'type': 'info', 'message': f"{target.name} の属性が {new_element} に変化した！"})


def _handle_set_field(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """戦場にフィールド（天候）を張り、特定属性の与ダメージを増幅する。"""
    if log is None:
        log = []
    element = effect.get("element")
    multiplier = float(effect.get("multiplier", 1.5))
    duration = int(effect.get("duration", 5))
    name = effect.get("field_name", "")
    set_field(element, multiplier, duration, name)
    display = name or (f"{element}フィールド" if element else "フィールド")
    log.append({'type': 'info', 'message': f"あたりは {display} に包まれた！ ({element}属性のダメージ {multiplier}倍 / {duration}ターン)"})


def _handle_shield(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """対象にバリア（HPの手前でダメージを肩代わりする盾）を付与する。"""
    if log is None:
        log = []
    amount = int(effect.get("amount", 0))
    percent = effect.get("percent")
    if percent:
        amount += int(target.max_hp * float(percent))
    target.shield = getattr(target, "shield", 0) + amount
    log.append({'type': 'info', 'message': f"{target.name} は {amount} のバリアを張った！ (バリア: {target.shield})"})


def _handle_transform(
    caster: Monster,
    target: Monster,
    effect: dict,
    log: List[Dict[str, str]] | None,
    skill: Optional[Skill] = None,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """術者が対象の戦闘ステータス・属性を一定ターンだけコピーする（変身）。"""
    if log is None:
        log = []
    duration = int(effect.get("duration", 3))
    snapshot = {
        "base_attack": caster.base_attack,
        "base_defense": caster.base_defense,
        "base_speed": caster.base_speed,
        "base_magic": caster.base_magic,
        "element": caster.element,
    }
    caster.base_attack = target.base_attack
    caster.base_defense = target.base_defense
    caster.base_speed = target.base_speed
    caster.base_magic = target.base_magic
    caster.element = target.element

    def revert(m: Monster = caster, s=snapshot) -> None:
        m.base_attack = s["base_attack"]
        m.base_defense = s["base_defense"]
        m.base_speed = s["base_speed"]
        m.base_magic = s["base_magic"]
        m.element = s["element"]

    if duration > 0:
        caster.status_effects.append({
            "name": "transform",
            "remaining": duration,
            "remove_func": revert,
        })
    log.append({'type': 'info', 'message': f"{caster.name} は {target.name} の姿をコピーした！"})


HANDLERS: Dict[str, Callable[[Monster, Monster, dict, List[Dict[str, str]], Optional[Skill], Optional[Dict[str, Any]]], None]] = {
    "damage": _handle_damage,
    "heal": _handle_heal,
    "permanent_stat": _handle_permanent_stat,
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
    "multi_hit": _handle_multi_hit,
    "percent_damage": _handle_percent_damage,
    "transfer_status": _handle_transfer_status,
    "atb_change": _handle_atb_change,
    "change_element": _handle_change_element,
    "set_field": _handle_set_field,
    "shield": _handle_shield,
    "transform": _handle_transform,
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
            # すべてのハンドラは (caster, target, effect, log, skill, context) のシグネチャ
            handler(caster, target, eff, log, skill, context)
        else:
            # fallback: status name shortcut
            name = eff.get("type")
            if name:
                _handle_status(caster, target, {"status": name, "duration": eff.get("duration")}, log, skill, context)
    return context

