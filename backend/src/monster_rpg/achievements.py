"""実績＆図鑑マイルストーン。

達成条件は「プレイヤー状態の述語」で表し、check_achievements() がいつ呼ばれても
新規達成分だけ報酬を付与する（冪等）。捕獲数の節目や初合成・ボス撃破などを拾う。
"""

from __future__ import annotations

from .monsters.monster_data import MONSTER_BOOK_DATA, ALL_MONSTERS

# 全属性（無・混合は除く）を集めたかの判定に使う
_CORE_ELEMENTS = {"火", "水", "風", "土", "闇", "雷", "光", "氷", "毒"}


def _captured(player) -> int:
    return len(player.monster_book.captured)


def _has_all_elements(player) -> bool:
    els = {ALL_MONSTERS[m].element for m in player.monster_book.captured if m in ALL_MONSTERS}
    return _CORE_ELEMENTS.issubset(els)


# id / name / desc / check(player)->bool / reward{gold,items}
ACHIEVEMENTS = [
    {"id": "collector_10", "name": "見習い博士", "desc": "10種を仲間にする",
     "check": lambda p: _captured(p) >= 10, "reward": {"gold": 200}},
    {"id": "collector_30", "name": "一人前の博士", "desc": "30種を仲間にする",
     "check": lambda p: _captured(p) >= 30, "reward": {"gold": 500, "items": ["weapon_core_rare"]}},
    {"id": "collector_50", "name": "博識なる者", "desc": "50種を仲間にする",
     "check": lambda p: _captured(p) >= 50, "reward": {"gold": 1000, "items": ["celestial_feather"]}},
    {"id": "collector_all", "name": "図鑑完成", "desc": "全種を仲間にする",
     "check": lambda p: _captured(p) >= len(MONSTER_BOOK_DATA),
     "reward": {"gold": 5000, "items": ["elixir", "elixir"]}},
    {"id": "all_elements", "name": "万象を統べる", "desc": "全属性のモンスターを仲間にする",
     "check": _has_all_elements, "reward": {"gold": 800}},
    {"id": "synthesizer", "name": "錬成師", "desc": "はじめて合成を行う",
     "check": lambda p: "synthesized" in p.story_flags, "reward": {"gold": 150}},
    {"id": "boss_slayer", "name": "魔を討つ者", "desc": "はじめてボスを倒す",
     "check": lambda p: "boss_defeated" in p.story_flags, "reward": {"gold": 300}},
    {"id": "awakener", "name": "覚醒の立会人", "desc": "★レア個体を生み出す",
     "check": lambda p: "rare_born" in p.story_flags, "reward": {"gold": 400}},
    {"id": "arena_champion", "name": "闘技王", "desc": "闘技場を制覇する",
     "check": lambda p: getattr(p, "arena_best", 0) >= 5, "reward": {"gold": 1500}},
]

# 図鑑マイルストーン（UI表示用：捕獲数の節目）
BESTIARY_MILESTONES = [10, 30, 50, len(MONSTER_BOOK_DATA)]


def check_achievements(player, log=None) -> list[str]:
    """未達成のうち条件を満たしたものを解禁し、報酬を付与。新規達成メッセージを返す。"""
    from .items.item_data import ALL_ITEMS
    newly: list[str] = []
    for a in ACHIEVEMENTS:
        if a["id"] in player.achievements:
            continue
        try:
            ok = bool(a["check"](player))
        except Exception:
            ok = False
        if not ok:
            continue
        player.achievements.add(a["id"])
        reward = a.get("reward", {})
        gold = int(reward.get("gold", 0))
        player.gold += gold
        for iid in reward.get("items", []):
            item = ALL_ITEMS.get(iid)
            if item is not None:
                player.items.append(item)
        msg = f"🏆 実績「{a['name']}」を達成！"
        if gold:
            msg += f"（+{gold}G）"
        newly.append(msg)
        if log is not None:
            log.append({"type": "achievement", "message": msg})
    return newly
