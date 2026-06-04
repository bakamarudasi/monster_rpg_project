"""闘技場（アリーナ）。

終章クリア後のやり込み。編成したパーティ(全回復コピー)で段位に挑み、自動決着で
勝てば次の段位が解禁され報酬を得る。耐性・ビルド・ため技・装備を活かす最適編成の
動機を作る。対話バトルフローには干渉しない自己完結シミュレーション。
"""

from __future__ import annotations

from . import progress
from .monsters.monster_data import ALL_MONSTERS

# 段位。enemies は (monster_id, level)。reward は初回クリア時のみ付与。
TIERS = [
    {"name": "鉄級", "level": 20, "enemies": [("orc_warrior", 20), ("troll_brute", 20)],
     "reward": {"gold": 500, "items": ["medium_potion"]}},
    {"name": "銀級", "level": 30, "enemies": [("ashen_drake", 30), ("kraken", 30), ("giant_golem", 30)],
     "reward": {"gold": 1000, "items": ["weapon_core_rare"]}},
    {"name": "金級", "level": 40, "enemies": [("vampire_lord", 40), ("abyss_watcher", 40)],
     "reward": {"gold": 2000, "items": ["celestial_feather"]}},
    {"name": "白金級", "level": 45, "enemies": [("fallen_deity", 45), ("obsidian_titan", 45)],
     "reward": {"gold": 3500, "items": ["dragon_scale", "abyss_shard"]}},
    {"name": "覇級", "level": 50,
     "enemies": [("thunder_emperor", 50), ("gaia_colossus", 50), ("plague_monarch", 50)],
     "reward": {"gold": 6000, "items": ["elixir"], "monsters": ["phoenix_chick"]}},
]


def _build_enemy(monster_id: str, level: int):
    base = ALL_MONSTERS.get(monster_id)
    if base is None:
        return None
    mon = base.copy()
    if level > mon.level:
        mon.advance_to_level(level)
    return mon


def auto_resolve(player_party, enemy_party, player):
    """両陣営を自動行動させ、決着までシミュレートする。戻り値 (outcome, log)。"""
    from .battle import (Battle, process_status_effects, process_charge_state,
                         enemy_take_action)
    battle = Battle(player_party, enemy_party, player)
    log = battle.log
    guard = 0
    while not battle.finished and guard < 1000:
        guard += 1
        battle.advance_turn()
        actor = battle.current_actor
        if actor is None or not actor.is_alive:
            continue
        flags = process_status_effects(actor, log)
        if not actor.is_alive:
            battle._check_battle_end()
            continue
        if flags.get("skip_turn"):
            continue
        if actor in battle.player_party:
            allies, foes = battle.player_party, battle.enemy_party
        else:
            allies, foes = battle.enemy_party, battle.player_party
        if process_charge_state(actor, allies, foes, log):
            battle._check_battle_end()
            continue
        # actor が foes を攻撃（enemy_take_action は第2引数を攻撃対象とする）
        enemy_take_action(actor, foes, allies, log)
        actor.reset_atb_gauge()
        battle._check_battle_end()
    if not battle.finished:
        battle.outcome = "draw"
    return battle.outcome, log


def can_challenge(player, tier_idx: int) -> bool:
    """挑戦可能か（クリア済み段位＋次の1段まで）。"""
    return 0 <= tier_idx <= getattr(player, "arena_best", 0) and tier_idx < len(TIERS)


def run_arena_tier(player, tier_idx: int):
    """段位に挑戦。戻り値 (win, message, reward_parts)。"""
    if not can_challenge(player, tier_idx):
        return False, "まだ挑戦できない段位です。", []
    if not player.party_monsters:
        return False, "パーティが編成されていません。", []
    tier = TIERS[tier_idx]
    enemies = [m for m in (_build_enemy(mid, lv) for mid, lv in tier["enemies"]) if m]
    party = [m.copy() for m in player.party_monsters]  # 全回復コピーで挑む
    outcome, _ = auto_resolve(party, enemies, player)
    win = outcome == "win"
    reward_parts: list[str] = []
    if win:
        first_clear = tier_idx == getattr(player, "arena_best", 0)
        if tier_idx + 1 > getattr(player, "arena_best", 0):
            player.arena_best = tier_idx + 1
        if first_clear:
            reward_parts = progress.grant_reward(player, tier.get("reward", {}))
        from .achievements import check_achievements
        check_achievements(player)
        msg = f"{tier['name']}を制覇した！"
        if reward_parts:
            msg += " 報酬: " + "／".join(reward_parts)
        return True, msg, reward_parts
    return False, f"{tier['name']}に敗れた…再挑戦しよう。", []


def arena_view(player) -> list[dict]:
    best = getattr(player, "arena_best", 0)
    rows = []
    for i, t in enumerate(TIERS):
        if i < best:
            status = "cleared"
        elif i == best:
            status = "open"
        else:
            status = "locked"
        rows.append({"idx": i, "name": t["name"], "level": t["level"],
                     "enemies": [ALL_MONSTERS[mid].name for mid, _ in t["enemies"] if mid in ALL_MONSTERS],
                     "reward": t.get("reward", {}), "status": status})
    return rows
