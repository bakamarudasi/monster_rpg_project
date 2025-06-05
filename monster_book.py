from dataclasses import dataclass
from typing import Dict, Set

@dataclass
class MonsterBookEntry:
    monster_id: str
    description: str
    synthesis_hint: str = ""
    reward: int = 0

# 図鑑に登録するモンスター情報
MONSTER_BOOK_DATA: Dict[str, MonsterBookEntry] = {
    "slime": MonsterBookEntry(
        monster_id="slime",
        description="ぷるぷるした弱小モンスター。水属性で、初心者の相手に最適。",
        synthesis_hint="別種族と掛け合わせると特殊なモンスターが生まれるかも。",
    ),
    "wolf": MonsterBookEntry(
        monster_id="wolf",
        description="俊敏な牙獣。群れで行動することが多い。",
        synthesis_hint="水に関連したモンスターと相性が良い。",
    ),
    "water_wolf": MonsterBookEntry(
        monster_id="water_wolf",
        description="水辺に潜むウルフ。鋭い爪で襲いかかる。",
        synthesis_hint="スライムとウルフを組み合わせると誕生するらしい。",
    ),
}

class MonsterBook:
    """プレイヤー毎に所持するモンスター図鑑。"""

    def __init__(self) -> None:
        self.seen: Set[str] = set()
        self.captured: Set[str] = set()

    def record_seen(self, monster_id: str) -> None:
        if monster_id in MONSTER_BOOK_DATA:
            self.seen.add(monster_id)

    def record_captured(self, monster_id: str) -> None:
        if monster_id in MONSTER_BOOK_DATA:
            self.seen.add(monster_id)
            self.captured.add(monster_id)

    def completion_rate(self) -> float:
        total = len(MONSTER_BOOK_DATA)
        return (len(self.captured) / total) * 100 if total else 0.0

    def show_book(self) -> None:
        print("===== モンスター図鑑 =====")
        for mid, entry in MONSTER_BOOK_DATA.items():
            if mid in self.seen:
                status = "捕獲" if mid in self.captured else "目撃"
                print(f"{entry.monster_id} [{status}]")
                print(f"  {entry.description}")
                if entry.synthesis_hint:
                    print(f"  合成ヒント: {entry.synthesis_hint}")
            else:
                print("??? [未発見]")
        rate = self.completion_rate()
        print(f"発見率: {rate:.1f}%")
        print("=========================")
