"""性格に応じたオート戦闘の行動選択。

性格（ステ傾向）を「戦い方のクセ」に翻訳する。プレイヤーのオート戦闘で、現在の
行動者の性格からアクションを決める。

- 攻撃寄り（ちからじまん/わんぱく）… 強い攻撃スキルがあれば撃つ。なければ通常攻撃。
- 魔法寄り（かしこい/ものしずか）… 攻撃スキル（魔法）を優先して撃つ。
- 防御寄り（がんこ/しんちょう）… 味方が傷ついていれば回復、いなければ通常攻撃。
- 素早さ寄り（せっかち/ようき）… ひたすら通常攻撃で最も弱った敵を狩る。
- バランス（まじめ）… 最初の敵に通常攻撃（従来どおり）。

返り値は ``Battle.process_player_action`` が解釈するアクション辞書。
"""

from __future__ import annotations

# 性格の up ステータス → オートAIスタイル
_STYLE_BY_UP = {
    "attack": "aggressive",
    "magic": "caster",
    "defense": "guardian",
    "speed": "striker",
}


def auto_style(monster) -> str:
    """モンスターの性格からオートAIのスタイルを決める。"""
    up = getattr(getattr(monster, "personality", None), "up", None)
    return _STYLE_BY_UP.get(up, "balanced")


def _is_offensive(skill) -> bool:
    return getattr(skill, "target", None) == "enemy"


def _is_heal(skill) -> bool:
    return any(e.get("type") == "heal" for e in getattr(skill, "effects", []) or [])


def _affordable(actor, skill) -> bool:
    return actor.mp >= getattr(skill, "cost", 0)


def _alive_enemy_indices(enemies) -> list[int]:
    return [i for i, e in enumerate(enemies) if getattr(e, "is_alive", False)]


def _lowest_hp_enemy_idx(enemies) -> int:
    alive = _alive_enemy_indices(enemies)
    if not alive:
        return -1
    return min(alive, key=lambda i: enemies[i].hp)


def _strongest_offensive_skill_idx(actor) -> int | None:
    """所持スキル中、撃てる最もコストの高い攻撃スキルの index（actor.skills 基準）。"""
    best, best_cost = None, -1
    for i, sk in enumerate(getattr(actor, "skills", []) or []):
        if _is_offensive(sk) and _affordable(actor, sk):
            cost = getattr(sk, "cost", 0)
            if cost > best_cost:
                best, best_cost = i, cost
    return best


def _heal_skill_idx(actor) -> int | None:
    for i, sk in enumerate(getattr(actor, "skills", []) or []):
        if _is_heal(sk) and _affordable(actor, sk):
            return i
    return None


def _hurt_ally_idx(allies, threshold: float = 0.5) -> int | None:
    """HPが threshold 割れの生存している味方のうち、最も割合が低い者の index。"""
    candidates = [
        (i, a) for i, a in enumerate(allies)
        if getattr(a, "is_alive", False) and a.max_hp > 0 and a.hp / a.max_hp <= threshold
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda pair: pair[1].hp / pair[1].max_hp)[0]


def _attack(target_idx: int) -> dict:
    return {"type": "attack", "target_enemy": target_idx}


def _skill(skill_idx: int, target_enemy: int = 0, target_ally: int = 0) -> dict:
    return {"type": "skill", "skill": skill_idx, "target_enemy": target_enemy, "target_ally": target_ally}


def choose_auto_action(actor, allies, enemies) -> dict:
    """性格に応じたオート行動を決める。敵が全滅していれば通常攻撃（エンジン側で処理）。"""
    enemy_idx = _lowest_hp_enemy_idx(enemies)
    if enemy_idx < 0:
        return _attack(-1)  # 対象なし。エンジンに委ねる。

    style = auto_style(actor)

    if style == "guardian":
        hurt = _hurt_ally_idx(allies)
        heal = _heal_skill_idx(actor)
        if hurt is not None and heal is not None:
            return _skill(heal, target_ally=hurt)
        return _attack(enemy_idx)

    if style == "caster":
        skill_idx = _strongest_offensive_skill_idx(actor)
        if skill_idx is not None:
            return _skill(skill_idx, target_enemy=enemy_idx)
        return _attack(enemy_idx)

    if style == "aggressive":
        # コストのある“大技”があれば撃つ。無ければ最も弱った敵に通常攻撃。
        skill_idx = _strongest_offensive_skill_idx(actor)
        if skill_idx is not None and getattr(actor.skills[skill_idx], "cost", 0) > 0:
            return _skill(skill_idx, target_enemy=enemy_idx)
        return _attack(enemy_idx)

    if style == "striker":
        return _attack(enemy_idx)

    # balanced: 従来どおり最初の生存敵へ通常攻撃
    first = _alive_enemy_indices(enemies)[0]
    return _attack(first)
