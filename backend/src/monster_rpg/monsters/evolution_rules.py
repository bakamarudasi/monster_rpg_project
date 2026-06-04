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
    # ウルフはLv7でシャドウパンサー。覚醒すると陽光のグリフォンへ。
    "wolf": [
        {"level": 7, "evolves_to": "shadow_panther", "awaken_chance": 0.12, "awaken_into": "solar_griffon"},
    ],
    # ファイアパピーはLv12で焦土の猟犬へ
    "ember_pup": [
        {"level": 12, "evolves_to": "cinder_hound", "awaken_chance": 0.1},
    ],
    # 疾風のハリアーはLv14で雷帝の大鷲へ
    "gale_harrier": [
        {"level": 14, "evolves_to": "thunderlord_roc", "awaken_chance": 0.1},
    ],

    # === 追加進化系統 ===
    # 方針: 自然成長で行ける天井は「A止まり」。S級＝魔王枠は合成/特殊でのみ作る
    # プレステージ枠なので、進化先には据えない。
    # --- beast ---
    "bat": [{"level": 8, "evolves_to": "gale_harrier"}],
    "wild_rat": [{"level": 6, "evolves_to": "goblin"}],
    "goblin": [{"level": 12, "evolves_to": "wolf"}],
    "spark_mouse": [{"level": 16, "evolves_to": "thunder_eagle", "awaken_chance": 0.1}],
    "orc_warrior": [{"level": 18, "evolves_to": "troll_brute"}],
    "frost_owl": [{"level": 20, "evolves_to": "crystal_drake", "awaken_chance": 0.1}],
    # --- undead ---
    "skeleton_archer": [{"level": 14, "evolves_to": "undead_warrior"}],
    "undead_warrior": [{"level": 24, "evolves_to": "abyss_watcher"}],
    "gravetide_hollow": [{"level": 24, "evolves_to": "abyss_watcher"}],
    "bog_revenant": [{"level": 24, "evolves_to": "blighted_knight"}],
    # --- construct / elemental ---
    "crystal_golem": [{"level": 20, "evolves_to": "giant_golem"}],
    "storm_djinn": [{"level": 24, "evolves_to": "storm_golem"}],
    # --- spirit ---
    "meadow_sprite": [{"level": 8, "evolves_to": "spectral_raven"}],
    "spectral_raven": [{"level": 18, "evolves_to": "midnight_horror", "awaken_chance": 0.1}],
    "mist_wraith": [{"level": 24, "evolves_to": "midnight_horror"}],
    # --- dragon ---
    "sand_wyrm": [{"level": 20, "evolves_to": "wyrm_of_dunes"}],
    # --- aquatic ---
    "mire_toad": [{"level": 12, "evolves_to": "tide_serpent"}],
    "tide_serpent": [{"level": 22, "evolves_to": "coral_hydra"}],
    "mermaid_siren": [{"level": 26, "evolves_to": "kraken"}],
    # --- demon ---
    "imp": [{"level": 6, "evolves_to": "dust_imp"}],
    "dust_imp": [{"level": 18, "evolves_to": "blood_fiend", "awaken_chance": 0.1}],
    # --- slime ---
    "moss_slime": [{"level": 5, "evolves_to": "slime"}],
    # --- insect ---
    "flame_mantis": [{"level": 20, "evolves_to": "electro_mantis", "awaken_chance": 0.1}],
    "desert_scorpion": [{"level": 18, "evolves_to": "wyrm_of_dunes"}],
    # --- plant ---
    "walking_mushroom": [{"level": 8, "evolves_to": "thorn_lurker"}],
    "thorn_lurker": [{"level": 18, "evolves_to": "moonlit_dryad"}],

    # === 序盤モンスターの進化（既存の中位ラインへ接続して育成の奥行きを作る） ===
    "cinder_kit": [{"level": 6, "evolves_to": "ember_pup"}],
    "breeze_sprite": [{"level": 10, "evolves_to": "gale_harrier"}],
    "bubble_jelly": [{"level": 10, "evolves_to": "tide_serpent"}],
    "frost_pixie": [{"level": 12, "evolves_to": "frost_owl"}],
    "venom_spider": [{"level": 12, "evolves_to": "desert_scorpion"}],
    "shade_imp": [{"level": 12, "evolves_to": "spectral_raven"}],
    "lumen_moth": [{"level": 15, "evolves_to": "moonlit_dryad"}],
    "pebble_knight": [{"level": 16, "evolves_to": "crystal_golem"}],
    "thunder_pup": [{"level": 18, "evolves_to": "thunder_eagle", "awaken_chance": 0.08}],

    # === 中盤モンスターの進化（C/B → 既存の中〜上位ラインへ） ===
    "gust_wisp": [{"level": 18, "evolves_to": "tempest_hawk"}],
    "granite_ogre": [{"level": 18, "evolves_to": "troll_brute"}],
    "dust_djinn": [{"level": 18, "evolves_to": "sand_wyrm"}],
    "flame_imp": [{"level": 20, "evolves_to": "lava_elemental", "awaken_chance": 0.08}],
    "magma_serpent": [{"level": 28, "evolves_to": "inferno_wyrm", "awaken_chance": 0.08}],
    "wraith_knight": [{"level": 18, "evolves_to": "bone_drake"}],
    "reef_guardian": [{"level": 26, "evolves_to": "coral_hydra", "awaken_chance": 0.08}],
    "glacier_pixie": [{"level": 18, "evolves_to": "glacier_warden"}],
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
