"""レイド（最大9体 VS レイドボス1体）のアプリケーションサービス。

戦闘エンジン（Battle / ATB）と Web の /battle ルート・UI・報酬処理を
そのまま再利用し、ここでは「ボスの生成」と「出撃メンバーの編成」だけを担う。
Flask 非依存。
"""

from __future__ import annotations

from ..exploration import get_monster_instance_copy
from ..battle import start_atb_battle
from ..raid_data import get_raid

# 1回のレイドに出撃できる最大数（3編成 × 3体）
MAX_RAID_PARTY = 9


def collect_available(player) -> list:
    """レイドに出せる手持ち＋控えモンスターの一覧（実体）を返す。"""
    return list(player.party_monsters) + list(player.reserve_monsters)


def build_raid_boss(defn: dict):
    """定義からレイドボスのインスタンスを生成する（既存モンスターを大幅強化）。"""
    boss = get_monster_instance_copy(defn["base"])
    if boss is None:
        return None

    target = defn.get("level", boss.level)
    if boss.level < target:
        # ログを汚さないよう verbose=False で一気に成長
        boss.advance_to_level(target, verbose=False)

    sm = defn.get("stat_mult")
    if sm:
        boss.base_attack = int(boss.base_attack * sm)
        boss.base_defense = int(boss.base_defense * sm)
        boss.base_magic = int(boss.base_magic * sm)
        boss.base_magic_defense = int(boss.base_magic_defense * sm)

    boss.max_hp = int(boss.max_hp * defn.get("hp_mult", 6.0))
    boss.hp = boss.max_hp
    boss.is_boss = True
    boss.is_alive = True
    boss.name = defn.get("name", boss.name)
    return boss


def start_raid(player, raid_id: str, indices):
    """選択したメンバーでレイド戦闘を構築する。

    戻り値 (battle, error)。error は None / メッセージ文字列。
    """
    defn = get_raid(raid_id)
    if not defn:
        return None, "そのレイドは存在しない。"

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

    battle = start_atb_battle(chosen, [boss], player)
    battle.is_raid = True
    battle.raid_id = defn["id"]
    battle.log.append({"type": "boss", "message": f"⚠ レイドボス {boss.name} が立ちはだかった！"})
    return battle, None
