"""レイドボスの定義。

既存モンスターをベースに、レベル・HP・攻撃力を大幅強化した「単体の強敵」。
プレイヤーは最大9体（3編成×3）を率いて挑む。戦闘エンジン／UI／報酬処理は
通常戦闘（ATBバトル）をそのまま再利用する。
"""

# 各レイドボスの定義
#   id         : レイド識別子（クリアフラグ raid_cleared:<id> に使用）
#   name       : 表示名
#   base       : ベースにする既存モンスターの monster_id
#   level      : このレベルまで成長させる
#   hp_mult    : 最大HPの倍率（レイドボスらしい超高HP）
#   stat_mult  : 攻撃・防御・魔力・魔防の倍率
#   element    : 表示用の属性
#   stars      : 難易度（★の数・表示用）
#   reward_gold: 初回／クリア時のボーナスゴールド
#   desc       : 説明文
RAID_BOSSES = [
    {
        "id": "ashen",
        "name": "業火竜 グレンドラ",
        "base": "ashen_drake",
        "level": 25,
        "hp_mult": 6.0,
        "stat_mult": 1.3,
        "element": "火",
        "stars": 3,
        "reward_gold": 1500,
        "desc": "灼熱の息吹で全てを焼き尽くす炎の覇竜。まずはここから。",
    },
    {
        "id": "kraken",
        "name": "深淵の海王 クラーケン",
        "base": "kraken",
        "level": 35,
        "hp_mult": 7.5,
        "stat_mult": 1.4,
        "element": "水",
        "stars": 4,
        "reward_gold": 3000,
        "desc": "深海より現れし無数の触手を持つ巨獣。生半可な編成では沈む。",
    },
    {
        "id": "celestial",
        "name": "天空覇竜 セレスティア",
        "base": "celestial_dragon",
        "level": 50,
        "hp_mult": 10.0,
        "stat_mult": 1.6,
        "element": "光",
        "stars": 5,
        "reward_gold": 6000,
        "desc": "全ての理を司る伝説の守護竜。9体の総力をもって挑め。",
    },
]


def get_raid(raid_id: str):
    """raid_id からレイド定義を取得（無ければ None）。"""
    return next((r for r in RAID_BOSSES if r["id"] == raid_id), None)
