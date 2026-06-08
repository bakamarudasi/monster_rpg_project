"""レイドボスの定義。

レイド専用の新モンスター（raid_monsters.json）を ALL_MONSTERS とは別に読み込み、
プレイヤーは最大9体（3編成×3）を率いて挑む。戦闘エンジン／UI／報酬処理は
通常戦闘（ATBバトル）をそのまま再利用する。レイド専用モンスターは図鑑や
スカウト・合成のプールには載らない（独立レジストリ）。
"""

import os

from .monsters.monster_data import load_monsters

# レイド専用モンスター（独立レジストリ）
_RAID_JSON = os.path.join(os.path.dirname(__file__), "monsters", "raid_monsters.json")
RAID_MONSTERS, RAID_MONSTER_BOOK = load_monsters(_RAID_JSON)


# 各レイドの定義
#   id         : レイド識別子（クリアフラグ raid_cleared:<id> に使用）
#   monster_id : raid_monsters.json 内のボス monster_id
#   element    : 表示用の属性
#   stars      : 難易度（★の数・表示用）
#   reward_gold: クリア時のボーナスゴールド
#   desc       : 説明文
RAID_BOSSES = [
    {
        "id": "ashen",
        "monster_id": "raid_ashen_dragon",
        "element": "火",
        "stars": 3,
        "reward_gold": 1500,
        "desc": "灼熱の息吹で全てを焼き尽くす炎の古竜。まずはここから。",
    },
    {
        "id": "kraken",
        "monster_id": "raid_abyssal_kraken",
        "element": "水",
        "stars": 4,
        "reward_gold": 3000,
        "desc": "深海より現れし無数の触手を持つ海の覇王。生半可な編成では沈む。",
    },
    {
        "id": "celestial",
        "monster_id": "raid_celestial_dragon",
        "element": "光",
        "stars": 5,
        "reward_gold": 6000,
        "desc": "全ての理を司る伝説の守護竜。9体の総力をもって挑め。",
    },
]


def _display_name(monster_id: str) -> str:
    m = RAID_MONSTERS.get(monster_id)
    return m.name if m else monster_id


# 表示名・レベルはボス本体から補完
for _b in RAID_BOSSES:
    _mon = RAID_MONSTERS.get(_b["monster_id"])
    _b["name"] = _mon.name if _mon else _b["monster_id"]
    _b["level"] = _mon.level if _mon else 1
    _b["max_hp"] = _mon.max_hp if _mon else 0


def get_raid(raid_id: str):
    """raid_id からレイド定義を取得（無ければ None）。"""
    return next((r for r in RAID_BOSSES if r["id"] == raid_id), None)
