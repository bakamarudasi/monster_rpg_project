# Rules for monster evolution
# key: base monster_id, value: dict with 'level' requirement and 'evolves_to'
EVOLUTION_RULES = {
    "dragon_pup": {"level": 10, "evolves_to": "ashen_drake"},
    "phoenix_chick": {"level": 8, "evolves_to": "cinder_sentinel"},
    # スライムはヒールを覚えた状態でLv5になるとウォーターワルフに進化
    "slime": {
        "level": 5,
        "evolves_to": "water_wolf",
        "requires_skill": "ヒール",
    },
    # ウルフはLv7でシャドウパンサーへ進化
    "wolf": {"level": 7, "evolves_to": "shadow_panther"},
}
