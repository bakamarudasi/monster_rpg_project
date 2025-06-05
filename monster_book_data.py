from dataclasses import dataclass
from typing import Dict

from monsters.monster_data import ALL_MONSTERS

@dataclass
class MonsterBookEntry:
    monster_id: str
    description: str = ""
    location_hint: str = ""
    synthesis_hint: str = ""
    reward: int = 0

# 既存モンスターすべての図鑑データを用意する。
# 各エントリの詳細は必要に応じて編集してください。
MONSTER_BOOK_DATA: Dict[str, MonsterBookEntry] = {
    mid: MonsterBookEntry(monster_id=mid) for mid in ALL_MONSTERS.keys()
}

# サンプルとしていくつかのモンスターには簡単な説明を記載
MONSTER_BOOK_DATA["slime"].description = "ぷるぷるした弱小モンスター。水属性で、初心者の相手に最適。"
MONSTER_BOOK_DATA["slime"].location_hint = "村の近くの草原などに出現"
MONSTER_BOOK_DATA["slime"].synthesis_hint = "別種族と掛け合わせると特殊なモンスターが生まれるかも。"

MONSTER_BOOK_DATA["wolf"].description = "俊敏な牙獣。群れで行動することが多い。"
MONSTER_BOOK_DATA["wolf"].location_hint = "妖精の森の奥地や丘陵街道に出現"
MONSTER_BOOK_DATA["wolf"].synthesis_hint = "水に関連したモンスターと相性が良い。"

MONSTER_BOOK_DATA["water_wolf"].description = "水辺に潜むウルフ。鋭い爪で襲いかかる。"
MONSTER_BOOK_DATA["water_wolf"].location_hint = "神秘の湖に出現"
MONSTER_BOOK_DATA["water_wolf"].synthesis_hint = "スライムとウルフを組み合わせると誕生するらしい。"
