"""レイド（最大9体 VS レイドボス1体）のアプリケーションサービス。

戦闘エンジン（Battle / ATB）と Web の /battle ルート・UI・報酬処理を
そのまま再利用し、ここでは「ボスの生成」と「出撃メンバーの編成」だけを担う。
Flask 非依存。
"""

from __future__ import annotations

from ..battle import start_atb_battle
from ..raid_data import get_raid, RAID_MONSTERS

# 1回のレイドに出撃できる最大数（3編成 × 3体）
MAX_RAID_PARTY = 9


def collect_available(player) -> list:
    """レイドに出せる手持ち＋控えモンスターの一覧（実体）を返す。"""
    return list(player.party_monsters) + list(player.reserve_monsters)


def build_raid_boss(defn: dict):
    """定義からレイド専用ボスのインスタンスを生成する。"""
    template = RAID_MONSTERS.get(defn["monster_id"])
    if template is None:
        return None
    boss = template.copy()
    boss.hp = boss.max_hp
    boss.is_boss = True
    boss.is_alive = True
    # フェーズ（HP閾値で発動するギミック）の状態を持たせる
    boss._raid_phases = [dict(p) for p in defn.get("phases", [])]
    boss._raid_phase_done = 0
    return boss


def check_phases(battle, log=None):
    """レイドボスのHPを見てフェーズ発動を判定し、効果を適用する。

    プレイヤー行動後／敵手番後に呼ぶ。発動したフェーズはログにメッセージを残す。
    """
    if not getattr(battle, "is_raid", False):
        return
    enemies = [e for e in battle.enemy_party if getattr(e, "is_boss", False)]
    if not enemies:
        return
    boss = enemies[0]
    phases = getattr(boss, "_raid_phases", None)
    if not phases or not boss.is_alive:
        return
    log = log if log is not None else battle.log
    ratio = boss.hp / boss.max_hp if boss.max_hp else 1.0
    done = getattr(boss, "_raid_phase_done", 0)
    for i, ph in enumerate(phases):
        if i < done:
            continue
        if ratio <= ph.get("at", 0):
            # 攻撃・魔力の強化
            if ph.get("attack_mult"):
                boss.base_attack = int(boss.base_attack * ph["attack_mult"])
            if ph.get("magic_mult"):
                boss.base_magic = int(boss.base_magic * ph["magic_mult"])
            # 割合回復
            if ph.get("heal"):
                boss.hp = min(boss.max_hp, boss.hp + int(boss.max_hp * ph["heal"]))
            msg = ph.get("message")
            if msg:
                log.append({"type": "boss", "message": msg})
            boss._raid_phase_done = i + 1
        else:
            break


def start_raid(player, raid_id: str, indices):
    """選択したメンバーでレイド戦闘を構築する。

    戻り値 (battle, error)。error は None / メッセージ文字列。
    """
    defn = get_raid(raid_id)
    if not defn:
        return None, "そのレイドは存在しない。"

    # 生贄（召喚アイテム）が必要なレイドは、所持を確認してから消費する
    requires = defn.get("requires") or []
    if requires:
        missing = [name for sid, name in requires if not _has_item(player, sid)]
        if missing:
            return None, "生贄が足りない… 必要: " + " / ".join(missing)

    available = collect_available(player)
    chosen = []
    seen = set()
    for i in indices:
        if 0 <= i < len(available) and i not in seen:
            chosen.append(available[i])
            seen.add(i)
        if len(chosen) >= MAX_RAID_PARTY:
            break

    if not chosen:
        return None, "出撃するモンスターを選んでください。"

    # 出撃メンバーは全回復・状態異常クリアで挑む（レイドの作法）
    for m in chosen:
        m.hp = m.max_hp
        m.mp = m.max_mp
        m.is_alive = True
        m.status_effects = []
        m.shield = 0
        m.atb_gauge = 0

    boss = build_raid_boss(defn)
    if boss is None:
        return None, "レイドボスの生成に失敗した。"

    # ここまで来たら生贄を消費して召喚
    for sid, _name in requires:
        _consume_item(player, sid)

    battle = start_atb_battle(chosen, [boss], player)
    battle.is_raid = True
    battle.raid_id = defn["id"]
    intro = "⚠ 禁忌の召喚……" if requires else "⚠ レイドボス "
    battle.log.append({"type": "boss", "message": f"{intro}{boss.name} が立ちはだかった！"})
    return battle, None


def _has_item(player, item_id: str) -> bool:
    return any(getattr(it, "item_id", None) == item_id for it in getattr(player, "items", []))


def _consume_item(player, item_id: str) -> bool:
    """player.items から item_id を1つ取り除く。"""
    items = getattr(player, "items", [])
    for i, it in enumerate(items):
        if getattr(it, "item_id", None) == item_id:
            del items[i]
            return True
    return False


def soul_status(player, requires):
    """生贄の所持状況を [{id,name,have}] で返す（ロビー表示用）。"""
    return [{"id": sid, "name": name, "have": _has_item(player, sid)} for sid, name in requires]
