from typing import Set
from .monsters.monster_data import MONSTER_BOOK_DATA

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

