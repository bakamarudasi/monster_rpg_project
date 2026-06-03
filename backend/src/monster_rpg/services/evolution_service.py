"""進化のアプリケーションサービス。

ドメインの進化ロジック（Monster._try_evolution / evolution_rules）を Web から扱う薄い層。
覚醒進化の reveal 用データ（name / awakened / became_rare）を返し、保存は呼び出し側に委ねる。
"""

from __future__ import annotations

from ..monsters.evolution_rules import get_evolution_branches


def options(monster):
    """そのモンスターが現状で進化可能な分岐（条件を満たすもの）を返す。"""
    eligible = []
    for branch in get_evolution_branches(monster.monster_id):
        if monster.level < branch.get('level', 0):
            continue
        req_skill = branch.get('requires_skill')
        if req_skill and not any(getattr(s, 'name', '') == req_skill for s in monster.skills):
            continue
        req_equip = branch.get('requires_equipment')
        if req_equip and not monster._has_equipment(req_equip):
            continue
        eligible.append(branch)
    return eligible


def can_evolve(monster) -> bool:
    """進化可能か（パーティ画面の「進化できそうだ！」表示用）。"""
    return bool(options(monster))


def evolve(player, party_idx: int):
    """パーティのモンスターを進化させ、reveal 用データを返す。

    戻り値 (success, data)。data は {evolved, name, awakened, became_rare} など。
    """
    if not (0 <= party_idx < len(player.party_monsters)):
        return False, {'error': 'invalid index'}
    monster = player.party_monsters[party_idx]
    if not can_evolve(monster):
        return False, {'error': 'not_ready'}
    result = monster._try_evolution(log=None, verbose=False)
    if not result:
        return False, {'error': 'not_ready'}
    return True, {
        'evolved': True,
        'name': result['name'],
        'awakened': result['awakened'],
        'became_rare': result['became_rare'],
    }
