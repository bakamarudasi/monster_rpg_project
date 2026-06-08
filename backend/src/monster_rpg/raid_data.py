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
        # phases: HPが at(割合) 以下で1度だけ発動。攻撃/魔力の倍率・割合回復・演出メッセージ
        "phases": [
            {"at": 0.5, "attack_mult": 1.3, "message": "🔥 イグドラが激昂した！ 攻撃が上がった！"},
            {"at": 0.2, "attack_mult": 1.25, "message": "🔥 イグドラ暴走！ 全身が業火に包まれる！"},
        ],
    },
    {
        "id": "kraken",
        "monster_id": "raid_abyssal_kraken",
        "element": "水",
        "stars": 4,
        "reward_gold": 3000,
        "desc": "深海より現れし無数の触手を持つ海の覇王。生半可な編成では沈む。",
        "phases": [
            {"at": 0.5, "magic_mult": 1.3, "heal": 0.15, "message": "🌊 アビスクラーケンが深海の力で再生した！"},
            {"at": 0.25, "attack_mult": 1.3, "message": "🌊 触手が荒れ狂う！ 攻撃が激化した！"},
        ],
    },
    {
        "id": "celestial",
        "monster_id": "raid_celestial_dragon",
        "element": "光",
        "stars": 5,
        "reward_gold": 6000,
        "desc": "全ての理を司る伝説の守護竜。9体の総力をもって挑め。",
        "phases": [
            {"at": 0.66, "magic_mult": 1.25, "message": "✨ セレスフィアが聖なる加護をまとった！"},
            {"at": 0.33, "attack_mult": 1.3, "magic_mult": 1.2, "heal": 0.1, "message": "✨ 天空の怒り！ セレスフィアが真の力を解放した！"},
        ],
    },
    {
        "id": "omega",
        "monster_id": "raid_omega",
        "element": "闇",
        "stars": 7,
        "reward_gold": 30000,
        "desc": "3体の魂を捧げし時、禁忌の竜神が目覚める……Lv99の極限。",
        "ultimate": True,
        # 生贄: 3体のレイドボスの魂を消費して召喚する
        "requires": [
            ("soul_ashen", "業火竜の魂"),
            ("soul_kraken", "海王の魂"),
            ("soul_celestial", "天竜の魂"),
        ],
        "phases": [
            {"at": 0.75, "magic_mult": 1.2, "message": "🐉 オメガ＝バハムートが覚醒の咆哮を上げた！"},
            {"at": 0.5, "attack_mult": 1.25, "magic_mult": 1.2, "heal": 0.1, "message": "🐉 次元が歪む……オメガが真の姿を現す！"},
            {"at": 0.2, "attack_mult": 1.4, "magic_mult": 1.4, "message": "🐉 最終形態！ 全てを終わらせる滅びの光！"},
        ],
    },
]


def _display_name(monster_id: str) -> str:
    m = RAID_MONSTERS.get(monster_id)
    return m.name if m else monster_id


# 表示名・レベル・稀少ドロップはボス本体から補完
for _b in RAID_BOSSES:
    _mon = RAID_MONSTERS.get(_b["monster_id"])
    _b["name"] = _mon.name if _mon else _b["monster_id"]
    _b["level"] = _mon.level if _mon else 1
    _b["max_hp"] = _mon.max_hp if _mon else 0
    # ドロップ表の中で最もレアな（=最低確率の legendary）専用装備を「稀少ドロップ」として表示
    _b["drop_name"] = None
    _b["drop_rate"] = None
    if _mon:
        _rares = [(it, rate) for it, rate in _mon.drop_items
                  if getattr(it, "rarity", "") == "legendary"]
        if _rares:
            _it, _rate = min(_rares, key=lambda x: x[1])
            _b["drop_name"] = _it.name
            _b["drop_rate"] = round(_rate * 100)


def get_raid(raid_id: str):
    """raid_id からレイド定義を取得（無ければ None）。"""
    return next((r for r in RAID_BOSSES if r["id"] == raid_id), None)
