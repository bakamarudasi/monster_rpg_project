"""Monster passive trait (特性) system.

Each monster can have a trait that provides a passive bonus in battle.
Traits are applied automatically and affect damage, healing, status resistance, etc.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Trait definitions
# ---------------------------------------------------------------------------

TRAIT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # --- 攻撃系 ---
    "fierce": {
        "name": "猛攻",
        "description": "攻撃ダメージが15%増加する",
        "on_attack_multiplier": 1.15,
    },
    "ambush": {
        "name": "奇襲",
        "description": "先手を取ったとき攻撃ダメージが25%増加する",
        "on_first_strike_multiplier": 1.25,
    },
    "berserker": {
        "name": "バーサーカー",
        "description": "HPが30%以下の時、攻撃力が50%増加する",
        "low_hp_attack_multiplier": 1.5,
        "low_hp_threshold": 0.3,
    },

    # --- 防御系 ---
    "iron_wall": {
        "name": "鉄壁",
        "description": "受けるダメージが15%減少する",
        "on_defend_multiplier": 0.85,
    },
    "thick_hide": {
        "name": "厚い皮膚",
        "description": "物理ダメージを10%軽減する",
        "physical_damage_reduction": 0.10,
    },
    "fire_resist": {
        "name": "炎耐性",
        "description": "火属性からのダメージを30%軽減する",
        "element_resist": "火",
        "element_resist_amount": 0.30,
    },
    "ice_resist": {
        "name": "氷耐性",
        "description": "氷属性からのダメージを30%軽減する",
        "element_resist": "氷",
        "element_resist_amount": 0.30,
    },
    "thunder_resist": {
        "name": "雷耐性",
        "description": "雷属性からのダメージを30%軽減する",
        "element_resist": "雷",
        "element_resist_amount": 0.30,
    },

    # --- 回復・サポート系 ---
    "regenerator": {
        "name": "自然回復",
        "description": "毎ターン最大HPの5%を回復する",
        "regen_percent": 0.05,
    },
    "mana_flow": {
        "name": "魔力の泉",
        "description": "毎ターンMPを3回復する",
        "mp_regen": 3,
    },

    # --- 状態異常系 ---
    "poison_body": {
        "name": "毒の体",
        "description": "物理攻撃を受けた時20%で相手を毒にする",
        "on_hit_status": "poison",
        "on_hit_status_chance": 0.20,
    },
    "static": {
        "name": "静電気",
        "description": "物理攻撃を受けた時20%で相手を麻痺にする",
        "on_hit_status": "paralyze",
        "on_hit_status_chance": 0.20,
    },
    "flame_body": {
        "name": "炎の体",
        "description": "物理攻撃を受けた時20%で相手をやけどにする",
        "on_hit_status": "burn",
        "on_hit_status_chance": 0.20,
    },
    "status_guard": {
        "name": "状態異常耐性",
        "description": "状態異常にかかる確率を30%軽減する",
        "status_resist": 0.30,
    },

    # --- スピード系 ---
    "swift": {
        "name": "俊足",
        "description": "素早さが20%増加する",
        "speed_multiplier": 1.20,
    },
    "slow_starter": {
        "name": "スロースターター",
        "description": "ターン経過ごとに攻撃力が5%ずつ上昇する(最大30%)",
        "turn_attack_boost": 0.05,
        "turn_attack_boost_max": 0.30,
    },

    # --- 特殊系 ---
    "life_steal": {
        "name": "吸血",
        "description": "攻撃ダメージの10%をHP回復する",
        "drain_percent": 0.10,
    },
    "last_stand": {
        "name": "不屈",
        "description": "致命的ダメージを受けた時、1回だけHP1で耐える",
        "survive_fatal": True,
    },
    "exp_boost": {
        "name": "経験値ブースト",
        "description": "獲得経験値が20%増加する",
        "exp_multiplier": 1.20,
    },
    "scout_charm": {
        "name": "スカウトの魅力",
        "description": "スカウト成功率が15%上昇する",
        "scout_rate_bonus": 0.15,
    },
}


def get_trait(trait_id: str) -> Optional[Dict[str, Any]]:
    """Return trait definition by ID, or None if not found."""
    return TRAIT_DEFINITIONS.get(trait_id)


def apply_attack_trait(
    attacker_trait: Optional[str],
    damage: int,
    turn_count: int = 0,
    attacker_hp_ratio: float = 1.0,
    is_first_strike: bool = False,
) -> int:
    """Modify outgoing damage based on attacker's trait."""
    if not attacker_trait:
        return damage
    trait = TRAIT_DEFINITIONS.get(attacker_trait)
    if not trait:
        return damage

    result = float(damage)

    # Fierce: flat attack multiplier
    mult = trait.get("on_attack_multiplier")
    if mult:
        result *= mult

    # Ambush: bonus on first strike
    if is_first_strike and trait.get("on_first_strike_multiplier"):
        result *= trait["on_first_strike_multiplier"]

    # Berserker: low HP bonus
    threshold = trait.get("low_hp_threshold")
    if threshold and attacker_hp_ratio <= threshold:
        result *= trait.get("low_hp_attack_multiplier", 1.0)

    # Slow starter: per-turn boost
    per_turn = trait.get("turn_attack_boost")
    if per_turn:
        max_boost = trait.get("turn_attack_boost_max", 1.0)
        boost = min(per_turn * turn_count, max_boost)
        result *= (1.0 + boost)

    return max(1, round(result))


def apply_defense_trait(
    defender_trait: Optional[str],
    damage: int,
    attacker_element: Optional[str] = None,
    is_physical: bool = True,
) -> int:
    """Modify incoming damage based on defender's trait."""
    if not defender_trait:
        return damage
    trait = TRAIT_DEFINITIONS.get(defender_trait)
    if not trait:
        return damage

    result = float(damage)

    # Iron wall: flat damage reduction
    mult = trait.get("on_defend_multiplier")
    if mult:
        result *= mult

    # Thick hide: physical damage reduction
    if is_physical:
        phys_red = trait.get("physical_damage_reduction", 0)
        if phys_red:
            result *= (1.0 - phys_red)

    # Elemental resistance
    resist_elem = trait.get("element_resist")
    if resist_elem and attacker_element == resist_elem:
        result *= (1.0 - trait.get("element_resist_amount", 0))

    return max(1, round(result))


def check_on_hit_trait(
    defender_trait: Optional[str],
) -> Optional[tuple[str, float]]:
    """Check if the defender has an on-hit status trait.

    Returns (status_name, chance) or None.
    """
    if not defender_trait:
        return None
    trait = TRAIT_DEFINITIONS.get(defender_trait)
    if not trait:
        return None
    status = trait.get("on_hit_status")
    chance = trait.get("on_hit_status_chance", 0)
    if status and chance > 0:
        return (status, chance)
    return None


def check_fatal_survive(defender_trait: Optional[str], already_triggered: bool) -> bool:
    """Check if the defender's trait allows surviving a fatal blow.

    Returns True if the monster should survive with 1 HP.
    """
    if already_triggered:
        return False
    if not defender_trait:
        return False
    trait = TRAIT_DEFINITIONS.get(defender_trait)
    if not trait:
        return False
    return bool(trait.get("survive_fatal"))


def get_drain_percent(trait_id: Optional[str]) -> float:
    """Return HP drain percentage from attacks (0.0 if none)."""
    if not trait_id:
        return 0.0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 0.0
    return float(trait.get("drain_percent", 0.0))


def get_speed_multiplier(trait_id: Optional[str]) -> float:
    """Return speed multiplier from trait (1.0 if none)."""
    if not trait_id:
        return 1.0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 1.0
    return float(trait.get("speed_multiplier", 1.0))


def get_regen_amount(trait_id: Optional[str], max_hp: int) -> int:
    """Return HP regen amount per turn."""
    if not trait_id:
        return 0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 0
    pct = trait.get("regen_percent", 0)
    return int(max_hp * pct) if pct else 0


def get_mp_regen(trait_id: Optional[str]) -> int:
    """Return MP regen per turn."""
    if not trait_id:
        return 0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 0
    return int(trait.get("mp_regen", 0))


def get_status_resist(trait_id: Optional[str]) -> float:
    """Return status resistance reduction (0.0 - 1.0)."""
    if not trait_id:
        return 0.0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 0.0
    return float(trait.get("status_resist", 0.0))


def get_exp_multiplier(trait_id: Optional[str]) -> float:
    """Return EXP multiplier from trait."""
    if not trait_id:
        return 1.0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 1.0
    return float(trait.get("exp_multiplier", 1.0))


def get_scout_bonus(trait_id: Optional[str]) -> float:
    """Return scout rate bonus from trait."""
    if not trait_id:
        return 0.0
    trait = TRAIT_DEFINITIONS.get(trait_id)
    if not trait:
        return 0.0
    return float(trait.get("scout_rate_bonus", 0.0))
