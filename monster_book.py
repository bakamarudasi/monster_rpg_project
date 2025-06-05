# monster_book.py
"""Simple Monster Encyclopedia management."""

import json
import os
from monsters.monster_data import ALL_MONSTERS
from synthesis_rules import SYNTHESIS_RECIPES


# Predefined descriptions for some monsters
MONSTER_DESCRIPTIONS = {
    "slime": "ぷるぷるした基本モンスター。初心者の登竜門。",
    "goblin": "悪戯好きな小鬼。集団で現れることが多い。",
    "wolf": "群れで狩りを行う俊敏な獣。",
}


def _build_synthesis_hints():
    """Create mapping from monster_id to synthesis hint text."""
    hints = {mid: "" for mid in ALL_MONSTERS}
    for (id1, id2), result in SYNTHESIS_RECIPES.items():
        n1 = ALL_MONSTERS[id1].name if id1 in ALL_MONSTERS else id1
        n2 = ALL_MONSTERS[id2].name if id2 in ALL_MONSTERS else id2
        hint = f"{n1} と {n2} を合成"
        if hints.get(result):
            hints[result] += " / " + hint
        else:
            hints[result] = hint
    return hints


SYNTHESIS_HINTS = _build_synthesis_hints()


class MonsterBook:
    def __init__(self):
        self.entries = {mid: {"seen": False, "captured": False} for mid in ALL_MONSTERS}
        self.reward_claimed = False

    def register_seen(self, monster_id: str):
        if monster_id in self.entries:
            self.entries[monster_id]["seen"] = True

    def register_captured(self, monster_id: str, player=None):
        if monster_id in self.entries:
            self.entries[monster_id]["seen"] = True
            already = self.entries[monster_id]["captured"]
            self.entries[monster_id]["captured"] = True
            if player and not self.reward_claimed and self.is_complete() and not already:
                player.gold += 1000
                self.reward_claimed = True
                print("図鑑をコンプリート！ 1000G を手に入れた！")

    def is_complete(self) -> bool:
        return all(info["captured"] for info in self.entries.values())

    def completion_rate(self) -> float:
        total = len(self.entries)
        seen = sum(1 for v in self.entries.values() if v["seen"])
        return (seen / total) * 100 if total else 0.0

    def display(self):
        print("===== モンスター図鑑 =====")
        print(f"発見率: {self.completion_rate():.1f}%")
        for mid in ALL_MONSTERS:
            entry = self.entries.get(mid, {})
            monster = ALL_MONSTERS[mid]
            if entry.get("seen"):
                status = "捕獲" if entry.get("captured") else "発見"
                print(f"\n{monster.name} ({status})")
                desc = MONSTER_DESCRIPTIONS.get(mid, "???")
                print(f"  {desc}")
                hint = SYNTHESIS_HINTS.get(mid)
                if hint:
                    print(f"  合成ヒント: {hint}")
            else:
                print("\n??? 未発見")
        print("========================")

    @staticmethod
    def _book_path(db_name: str) -> str:
        return db_name + "_monsterbook.json"

    def save(self, db_name: str, user_id: int):
        path = self._book_path(db_name)
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[str(user_id)] = self.entries
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, db_name: str, user_id: int):
        book = cls()
        path = cls._book_path(db_name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if str(user_id) in data:
                    book.entries.update(data[str(user_id)])
        return book
