"""ゲーム進行データ（実績・クエスト・図鑑報酬・アリーナ）の直列化ヘルパー。

これらはすべて Player の属性として持ち、player_progress テーブルに JSON 1行で
保存する。新しい進行系フィールドはここに足せば save/load に自動で乗る。
"""

from __future__ import annotations

import json

# set として持つフィールド（JSON では配列で保存）
SET_FIELDS = (
    "achievements",
    "quests_active",
    "quests_completed",
    "claimed_milestones",
    "story_flags",
)
# int として持つフィールド
INT_FIELDS = {"arena_best": 0}


def init_progress(player) -> None:
    """Player に進行系フィールドの初期値をセットする。"""
    for f in SET_FIELDS:
        setattr(player, f, set())
    for f, default in INT_FIELDS.items():
        setattr(player, f, default)


def to_json(player) -> str:
    data = {f: sorted(getattr(player, f, set()) or set()) for f in SET_FIELDS}
    for f, default in INT_FIELDS.items():
        data[f] = int(getattr(player, f, default) or default)
    return json.dumps(data, ensure_ascii=False)


def apply_json(player, text: str | None) -> None:
    try:
        data = json.loads(text) if text else {}
    except (ValueError, TypeError):
        data = {}
    for f in SET_FIELDS:
        setattr(player, f, set(data.get(f, []) or []))
    for f, default in INT_FIELDS.items():
        setattr(player, f, int(data.get(f, default) or default))
