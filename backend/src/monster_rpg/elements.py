"""属性相性表と戦場（フィールド/天候）の状態管理。

このモジュールはパッケージ内の他モジュールに依存しない「葉モジュール」なので、
``battle`` と ``skills.skill_actions`` の双方から循環インポートなしで参照できる。

これまで属性相性表 (``ELEMENTAL_MULTIPLIERS``) は ``battle.py`` と
``skill_actions.py`` に別々にコピーされており、内容が既に食い違っていた
（battle 側にだけ 光→闇 があった）。ここに一本化して両者から import する。
"""

from __future__ import annotations

from typing import Any, Dict, Optional


# (攻撃側属性, 防御側属性): その向きで攻撃したときの倍率。
# 「強い向き」だけを列挙する。逆向き (防御側→攻撃側) は
# ``elemental_multiplier`` が自動的に 0.5 (いまひとつ) として扱う。
# 光↔闇 のように相互に弱点な関係は、両方向を明示的に 1.5 で登録する。
ELEMENTAL_MULTIPLIERS: Dict[tuple[str, str], float] = {
    # 三すくみ①（既存）: 火 → 風 → 水 → 火
    ("火", "風"): 1.5,
    ("風", "水"): 1.5,
    ("水", "火"): 1.5,
    # 4元素サイクル: 雷 → 水 → 火 → 氷 → 雷
    ("雷", "水"): 1.5,   # 雷は水に伝わる
    ("火", "氷"): 1.5,   # 炎は氷を溶かす
    ("氷", "雷"): 1.5,   # 凍結が雷を絶つ
    # 土と風・雷
    ("風", "土"): 1.5,   # 風は砂塵を吹き飛ばす
    ("土", "雷"): 1.5,   # 大地は雷を接地して吸収する
    # 毒は風で散らされる
    ("風", "毒"): 1.5,
    # 光と闇は相互に弱点
    ("光", "闇"): 1.5,
    ("闇", "光"): 1.5,
}


def elemental_multiplier(attacker_element: Optional[str], defender_element: Optional[str]) -> float:
    """属性相性によるダメージ倍率を返す。

    - 「強い向き」が登録されていればその倍率 (基本 1.5)。
    - 逆向きだけが登録されている場合は 0.5 (いまひとつ)。
    - どちらにも無い・無属性などは 1.0。
    """
    if not attacker_element or not defender_element:
        return 1.0
    mult = ELEMENTAL_MULTIPLIERS.get((attacker_element, defender_element))
    if mult is not None:
        return mult
    if ELEMENTAL_MULTIPLIERS.get((defender_element, attacker_element)) is not None:
        return 0.5
    return 1.0


# --- 戦場（フィールド / 天候） ------------------------------------------------
# 戦闘中に張られる「場」の状態。特定属性のダメージを全体的に増幅する。
# プロセス内で 1 戦闘ずつ進む簡易ゲームなのでモジュールレベルの状態として持つ。
# Battle 生成時に ``clear_field`` され、ターン経過で ``tick_field`` が減衰させる。
_FIELD: Dict[str, Any] = {"element": None, "multiplier": 1.0, "remaining": 0, "name": ""}


def set_field(element: Optional[str], multiplier: float = 1.5, duration: int = 3, name: str = "") -> None:
    """フィールドを張る。``element`` 属性の与ダメージを ``multiplier`` 倍にする。"""
    _FIELD["element"] = element
    _FIELD["multiplier"] = float(multiplier)
    _FIELD["remaining"] = int(duration)
    _FIELD["name"] = name or (f"{element}フィールド" if element else "フィールド")


def get_field() -> Optional[Dict[str, Any]]:
    """現在有効なフィールドの情報を返す。無ければ None。"""
    if _FIELD["remaining"] <= 0 or _FIELD["element"] is None:
        return None
    return dict(_FIELD)


def field_multiplier(attacker_element: Optional[str]) -> float:
    """攻撃側属性がフィールドと一致していれば増幅倍率を返す。"""
    if (
        _FIELD["remaining"] > 0
        and _FIELD["element"] is not None
        and attacker_element == _FIELD["element"]
    ):
        return float(_FIELD["multiplier"])
    return 1.0


def tick_field() -> Optional[str]:
    """フィールドの残りターンを 1 減らす。今のターンで切れたらフィールド名を返す。"""
    if _FIELD["remaining"] > 0:
        _FIELD["remaining"] -= 1
        if _FIELD["remaining"] <= 0:
            expired = _FIELD["name"]
            clear_field()
            return expired
    return None


def clear_field() -> None:
    """フィールドを消す（戦闘開始時のリセット用）。"""
    _FIELD["element"] = None
    _FIELD["multiplier"] = 1.0
    _FIELD["remaining"] = 0
    _FIELD["name"] = ""
