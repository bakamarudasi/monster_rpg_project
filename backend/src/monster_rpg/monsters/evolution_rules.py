# Rules for monster evolution.
#
# 各 base monster_id に「進化分岐(branch)のリスト」を対応させる。
# 旧形式（単一 dict）も後方互換でサポートする（_normalize がリスト化する）。
#
# branch のキー:
#   evolves_to         : 進化先 monster_id（必須）
#   level              : 必要レベル（既定 0）
#   requires_skill     : 必要スキル名（任意）
#   requires_equipment : 装備していると満たす equip_id もしくはカテゴリ（任意・触媒進化用）
#   awaken_chance      : 覚醒抽選確率 0..1（任意）。当たると★レア個体化する
#   awaken_into        : 覚醒成功時に化ける上位 monster_id（任意。無ければ同形で★）
#
# 条件は上から順に評価し、最初に満たした枝へ進化する。

EVOLUTION_RULES = {
    "dragon_pup": [
        {"level": 10, "evolves_to": "ashen_drake", "awaken_chance": 0.12},
    ],
    "phoenix_chick": [
        {"level": 8, "evolves_to": "cinder_sentinel", "awaken_chance": 0.12},
    ],
    # スライムはヒールを覚えた状態でLv5になるとウォーターウルフに進化
    "slime": [
        {"level": 5, "evolves_to": "water_wolf", "requires_skill": "ヒール"},
    ],
    # ウルフはLv7でシャドウパンサーへ進化
    "wolf": [
        {"level": 7, "evolves_to": "shadow_panther"},
    ],
}


def _normalize(rule):
    """単一 dict / リスト / None を、分岐 dict のリストに正規化する。"""
    if rule is None:
        return []
    if isinstance(rule, dict):
        return [rule]
    return list(rule)


def get_evolution_branches(monster_id):
    """指定 monster_id の進化分岐を正規化したリストで返す（無ければ []）。"""
    return _normalize(EVOLUTION_RULES.get(monster_id))
