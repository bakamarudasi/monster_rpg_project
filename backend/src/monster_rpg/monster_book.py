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

    def show_book(self) -> None:
        print("===== モンスター図鑑 =====")
        for mid, entry in MONSTER_BOOK_DATA.items():
            if mid in self.captured:
                print(f"{entry.monster_id} [捕獲]")
                print(f"  {entry.description}")
                if entry.location_hint:
                    print(f"  出現場所: {entry.location_hint}")
                if entry.synthesis_hint:
                    print(f"  合成ヒント: {entry.synthesis_hint}")
            elif mid in self.seen:
                print(f"{entry.monster_id} [目撃]")
                print("  ??? 詳細は不明")
                if entry.location_hint:
                    print(f"  手掛かり: {entry.location_hint}")
            else:
                print("??? [未発見]")
        rate = self.completion_rate()
        print(f"発見率: {rate:.1f}%")
        print("=========================")
