"""依頼（クエスト）システム。

掲示板で受注し、条件を満たすと報酬を受け取れる。条件はプレイヤー状態の述語で表す。
種類:
  capture_count : 図鑑の捕獲数が target 以上
  capture_id    : 特定モンスターを仲間にした
  capture_any   : target(リスト)のいずれかを仲間にした
  defeat        : 特定ボスを倒した（story_flags の "defeated:<id>"）
"""

from __future__ import annotations

from . import progress

QUESTS = [
    {"id": "q_first_friend", "name": "はじめての仲間", "type": "capture_count", "target": 1,
     "desc": "モンスターを1体仲間にする。", "reward": {"gold": 100, "items": ["small_potion"]}},
    {"id": "q_make_water_wolf", "name": "水狼の錬成", "type": "capture_id", "target": "water_wolf",
     "desc": "ウォーターウルフを手に入れる（スライム+ウルフ等）。", "reward": {"gold": 200, "items": ["magic_stone"]}},
    {"id": "q_collect_15", "name": "見習い研究者", "type": "capture_count", "target": 15,
     "desc": "図鑑を15体ぶん埋める。", "reward": {"gold": 300, "items": ["medium_potion", "medium_potion"]}},
    {"id": "q_slay_match_ember", "name": "焔の少女を鎮めよ", "type": "defeat", "target": "match_ember",
     "desc": "マッチ売りの焔(match_ember)を討伐する。", "reward": {"gold": 600, "items": ["fire_crystal"]}},
    {"id": "q_collect_40", "name": "図鑑の番人", "type": "capture_count", "target": 40,
     "desc": "図鑑を40体ぶん埋める。", "reward": {"gold": 1000, "items": ["celestial_feather"]}},
    {"id": "q_slay_poison_queen", "name": "白雪の毒后", "type": "defeat", "target": "poison_queen",
     "desc": "毒后(poison_queen)を討伐する。", "reward": {"gold": 800, "items": ["armor_fragment_rare"]}},
    {"id": "q_make_demon_lord", "name": "魔王を錬成せよ", "type": "capture_any",
     "target": ["storm_sovereign", "gaia_colossus", "plague_monarch", "abyssal_tide_king", "thunder_emperor"],
     "desc": "新たな魔王枠を合成で生み出す。", "reward": {"gold": 1500, "items": ["abyss_shard"]}},
    {"id": "q_slay_tale_devourer", "name": "物語の終焉", "type": "defeat", "target": "tale_devourer",
     "desc": "物語を喰らうもの(tale_devourer)を討伐する。", "reward": {"gold": 3000, "items": ["elixir"]}},
]

QUEST_BY_ID = {q["id"]: q for q in QUESTS}


def is_complete(player, quest) -> bool:
    t, tgt = quest["type"], quest["target"]
    captured = player.monster_book.captured
    if t == "capture_count":
        return len(captured) >= int(tgt)
    if t == "capture_id":
        return tgt in captured
    if t == "capture_any":
        return any(x in captured for x in tgt)
    if t == "defeat":
        return f"defeated:{tgt}" in player.story_flags
    return False


def accept_quest(player, quest_id) -> tuple[bool, str]:
    if quest_id not in QUEST_BY_ID:
        return False, "そのような依頼はない。"
    if quest_id in player.quests_completed:
        return False, "その依頼は達成済み。"
    if quest_id in player.quests_active:
        return False, "すでに受注している。"
    player.quests_active.add(quest_id)
    return True, f"依頼「{QUEST_BY_ID[quest_id]['name']}」を受注した。"


def claim_quest(player, quest_id) -> tuple[bool, str]:
    quest = QUEST_BY_ID.get(quest_id)
    if not quest or quest_id not in player.quests_active:
        return False, "受注していない依頼。"
    if not is_complete(player, quest):
        return False, "まだ達成条件を満たしていない。"
    player.quests_active.discard(quest_id)
    player.quests_completed.add(quest_id)
    parts = progress.grant_reward(player, quest.get("reward", {}))
    reward_txt = "／".join(parts) if parts else "報酬"
    return True, f"依頼「{quest['name']}」達成！ 報酬: {reward_txt}"


def quest_view(player) -> list[dict]:
    """掲示板表示用に各依頼の状態を組み立てる。"""
    rows = []
    for q in QUESTS:
        if q["id"] in player.quests_completed:
            status = "completed"
        elif q["id"] in player.quests_active:
            status = "ready" if is_complete(player, q) else "active"
        else:
            status = "available"
        rows.append({"id": q["id"], "name": q["name"], "desc": q["desc"],
                     "reward": q.get("reward", {}), "status": status})
    return rows
