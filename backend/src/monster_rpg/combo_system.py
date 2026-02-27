"""Combo skill system (コンボスキルシステム).

When specific skills are used consecutively by party members, a combo
triggers, dealing bonus effects.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any


# ---------------------------------------------------------------------------
# Combo definitions
# ---------------------------------------------------------------------------

COMBO_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "fire_storm": {
        "name": "ファイアストーム",
        "description": "火属性スキル2連続で大炎上！全体に追加炎ダメージ",
        "trigger": ["fireball", "dragon_breath"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_damage",
            "amount": 40,
            "status": "burn",
            "status_duration": 3,
        },
    },
    "absolute_zero": {
        "name": "アブソリュートゼロ",
        "description": "氷属性スキル2連続で極寒の一撃！全体に凍結付与",
        "trigger": ["ice_spear", "ice_bolt"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_damage",
            "amount": 50,
            "status": "freeze",
            "status_duration": 2,
        },
    },
    "thunder_chain": {
        "name": "サンダーチェイン",
        "description": "雷スキル2連続で連鎖雷撃！全体に麻痺付与",
        "trigger": ["thunder_bolt", "lightning"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_damage",
            "amount": 45,
            "status": "paralyze",
            "status_duration": 2,
        },
    },
    "holy_judgement": {
        "name": "ホーリージャッジメント",
        "description": "光スキル後に攻撃で聖なる裁き！追加大ダメージ",
        "trigger": ["holy_light", "meteor_strike"],
        "trigger_any_order": False,
        "effect": {
            "type": "single_damage",
            "amount": 70,
        },
    },
    "dark_convergence": {
        "name": "ダークコンバージェンス",
        "description": "闇スキル2連続で暗黒収束！敵全体のステータスダウン",
        "trigger": ["dark_pulse", "curse"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_debuff",
            "stats": {"attack": -8, "defense": -8, "speed": -5},
            "duration": 3,
        },
    },
    "healing_wind": {
        "name": "ヒーリングウインド",
        "description": "回復スキル2連続で癒しの風！味方全体HP回復",
        "trigger": ["heal", "cure"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_heal",
            "amount": 30,
        },
    },
    "fortification": {
        "name": "フォーティフィケーション",
        "description": "バフスキル2連続で鉄壁の守り！味方全体の防御大アップ",
        "trigger": ["guard_up", "power_up"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_buff",
            "stats": {"attack": 5, "defense": 8},
            "duration": 3,
        },
    },
    "poison_eruption": {
        "name": "ポイズンエラプション",
        "description": "毒スキル2連続で毒が爆発！全体に猛毒",
        "trigger": ["poison_dart", "poison_cloud"],
        "trigger_any_order": True,
        "effect": {
            "type": "aoe_damage",
            "amount": 25,
            "status": "spore_poison",
            "status_duration": 4,
        },
    },
    "earth_shatter": {
        "name": "アースシャッター",
        "description": "地属性スキル後にパワーアップで大地が割れる！",
        "trigger": ["earth_quake", "power_up"],
        "trigger_any_order": False,
        "effect": {
            "type": "aoe_damage",
            "amount": 55,
        },
    },
}


class ComboTracker:
    """Tracks skill usage to detect and trigger combos."""

    # Maximum number of recent skills to track
    HISTORY_SIZE = 5

    def __init__(self):
        self.skill_history: List[str] = []

    def record_skill(self, skill_id: str) -> None:
        """Record a skill usage."""
        self.skill_history.append(skill_id)
        if len(self.skill_history) > self.HISTORY_SIZE:
            self.skill_history.pop(0)

    def check_combo(self) -> Optional[Dict[str, Any]]:
        """Check if the recent skill history triggers a combo.

        Returns the combo definition if triggered, or None.
        """
        if len(self.skill_history) < 2:
            return None

        last_two = self.skill_history[-2:]

        for combo_id, combo in COMBO_DEFINITIONS.items():
            trigger = combo["trigger"]
            if len(trigger) != 2:
                continue

            if combo.get("trigger_any_order"):
                if set(last_two) == set(trigger):
                    return {"combo_id": combo_id, **combo}
            else:
                if last_two == trigger:
                    return {"combo_id": combo_id, **combo}

        return None

    def clear(self) -> None:
        """Reset combo tracking."""
        self.skill_history.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"skill_history": self.skill_history[:]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComboTracker":
        t = cls()
        t.skill_history = data.get("skill_history", [])
        return t


def apply_combo_effect(
    combo: Dict[str, Any],
    allies: list,
    enemies: list,
    log: Optional[List[Dict[str, str]]] = None,
) -> None:
    """Apply the effect of a triggered combo."""
    if log is None:
        log = []

    effect = combo.get("effect", {})
    etype = effect.get("type", "")

    log.append({
        'type': 'combo',
        'message': f"★コンボ発動★ 「{combo['name']}」！ {combo['description']}",
    })

    if etype == "aoe_damage":
        amount = effect.get("amount", 0)
        status = effect.get("status")
        status_dur = effect.get("status_duration", 2)
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            enemy.hp -= amount
            log.append({
                'type': 'info',
                'message': f"{enemy.name} に {amount} のコンボダメージ！ (HP: {max(0, enemy.hp)})",
            })
            if enemy.hp <= 0:
                enemy.is_alive = False
                log.append({'type': 'info', 'message': f"{enemy.name} は倒れた！"})
            elif status:
                enemy.apply_status(status, [], status_dur)
                log.append({
                    'type': 'info',
                    'message': f"{enemy.name} は状態異常になった！",
                })

    elif etype == "single_damage":
        amount = effect.get("amount", 0)
        alive_enemies = [e for e in enemies if e.is_alive]
        if alive_enemies:
            target = min(alive_enemies, key=lambda m: m.hp)
            target.hp -= amount
            log.append({
                'type': 'info',
                'message': f"{target.name} に {amount} のコンボダメージ！ (HP: {max(0, target.hp)})",
            })
            if target.hp <= 0:
                target.is_alive = False
                log.append({'type': 'info', 'message': f"{target.name} は倒れた！"})

    elif etype == "aoe_debuff":
        stats = effect.get("stats", {})
        duration = effect.get("duration", 3)
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            for stat, amount in stats.items():
                enemy.apply_buff(stat, amount, duration)
            log.append({
                'type': 'info',
                'message': f"{enemy.name} のステータスが低下した！",
            })

    elif etype == "aoe_heal":
        amount = effect.get("amount", 0)
        for ally in allies:
            if not ally.is_alive:
                continue
            before = ally.hp
            ally.hp = min(ally.max_hp, ally.hp + amount)
            healed = ally.hp - before
            if healed > 0:
                log.append({
                    'type': 'info',
                    'message': f"{ally.name} のHPが {healed} 回復した！",
                })

    elif etype == "aoe_buff":
        stats = effect.get("stats", {})
        duration = effect.get("duration", 3)
        for ally in allies:
            if not ally.is_alive:
                continue
            for stat, amount in stats.items():
                ally.apply_buff(stat, amount, duration)
            log.append({
                'type': 'info',
                'message': f"{ally.name} のステータスが上昇した！",
            })
