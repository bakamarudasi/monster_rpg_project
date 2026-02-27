"""Achievement system (実績システム).

Tracks player accomplishments and awards titles/bonuses.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional


# ---------------------------------------------------------------------------
# Achievement definitions
# ---------------------------------------------------------------------------

ACHIEVEMENT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    # --- バトル系 ---
    "first_victory": {
        "name": "初勝利",
        "description": "はじめてのバトルに勝利した",
        "category": "battle",
        "reward_gold": 50,
        "icon": "sword",
    },
    "win_10": {
        "name": "戦士の目覚め",
        "description": "バトルに10回勝利した",
        "category": "battle",
        "reward_gold": 200,
        "icon": "sword",
    },
    "win_50": {
        "name": "歴戦の勇者",
        "description": "バトルに50回勝利した",
        "category": "battle",
        "reward_gold": 1000,
        "icon": "crown",
    },
    "win_100": {
        "name": "不敗の英雄",
        "description": "バトルに100回勝利した",
        "category": "battle",
        "reward_gold": 3000,
        "icon": "trophy",
    },
    "no_damage_win": {
        "name": "無傷の勝利",
        "description": "ダメージを受けずにバトルに勝利した",
        "category": "battle",
        "reward_gold": 500,
        "icon": "shield",
    },
    "combo_master": {
        "name": "コンボマスター",
        "description": "コンボスキルを10回発動した",
        "category": "battle",
        "reward_gold": 800,
        "icon": "star",
    },
    "weather_warrior": {
        "name": "天候の覇者",
        "description": "全種類の天候でバトルに勝利した",
        "category": "battle",
        "reward_gold": 1500,
        "icon": "cloud",
    },

    # --- モンスター系 ---
    "first_scout": {
        "name": "はじめてのスカウト",
        "description": "モンスターをはじめてスカウトした",
        "category": "monster",
        "reward_gold": 100,
        "icon": "heart",
    },
    "monster_10": {
        "name": "モンスターコレクター",
        "description": "10種類のモンスターを図鑑に登録した",
        "category": "monster",
        "reward_gold": 300,
        "icon": "book",
    },
    "monster_30": {
        "name": "モンスターマスター",
        "description": "30種類のモンスターを図鑑に登録した",
        "category": "monster",
        "reward_gold": 2000,
        "icon": "book",
    },
    "max_level": {
        "name": "最強への道",
        "description": "モンスターをレベル50に到達させた",
        "category": "monster",
        "reward_gold": 1000,
        "icon": "star",
    },
    "evolution_first": {
        "name": "進化の瞬間",
        "description": "はじめてモンスターを進化させた",
        "category": "monster",
        "reward_gold": 300,
        "icon": "sparkle",
    },

    # --- 合成系 ---
    "first_synthesis": {
        "name": "はじめての合成",
        "description": "モンスターの合成を初めて行った",
        "category": "synthesis",
        "reward_gold": 200,
        "icon": "flask",
    },
    "synthesis_10": {
        "name": "合成職人",
        "description": "合成を10回行った",
        "category": "synthesis",
        "reward_gold": 500,
        "icon": "flask",
    },
    "synthesis_s_rank": {
        "name": "伝説の合成師",
        "description": "Sランクモンスターを合成で生み出した",
        "category": "synthesis",
        "reward_gold": 2000,
        "icon": "crown",
    },

    # --- 探索系 ---
    "explorer_5": {
        "name": "旅人",
        "description": "5つのエリアを訪れた",
        "category": "explore",
        "reward_gold": 200,
        "icon": "map",
    },
    "explorer_all": {
        "name": "世界の探索者",
        "description": "全てのエリアを訪れた",
        "category": "explore",
        "reward_gold": 3000,
        "icon": "globe",
    },

    # --- 経済系 ---
    "rich_1000": {
        "name": "お金持ち",
        "description": "所持金1000Gを超えた",
        "category": "economy",
        "reward_gold": 100,
        "icon": "coin",
    },
    "rich_10000": {
        "name": "大富豪",
        "description": "所持金10000Gを超えた",
        "category": "economy",
        "reward_gold": 500,
        "icon": "gem",
    },
}


class AchievementManager:
    """Tracks and manages player achievements."""

    def __init__(self):
        self.unlocked: Dict[str, bool] = {}
        self.stats: Dict[str, int] = {
            "battles_won": 0,
            "combos_triggered": 0,
            "monsters_scouted": 0,
            "syntheses_done": 0,
            "evolutions_done": 0,
            "areas_visited": 0,
            "weather_wins": {},  # weather_id -> bool
        }
        self.pending_rewards: List[Dict[str, Any]] = []

    def check_and_unlock(
        self,
        achievement_id: str,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        """Check if an achievement should be unlocked and unlock it.

        Returns True if newly unlocked.
        """
        if achievement_id in self.unlocked:
            return False
        if achievement_id not in ACHIEVEMENT_DEFINITIONS:
            return False

        self.unlocked[achievement_id] = True
        defn = ACHIEVEMENT_DEFINITIONS[achievement_id]
        reward = defn.get("reward_gold", 0)
        self.pending_rewards.append({
            "achievement_id": achievement_id,
            "gold": reward,
        })

        if log is not None:
            log.append({
                'type': 'achievement',
                'message': f"★実績解除★「{defn['name']}」 {defn['description']} (報酬: {reward}G)",
            })
        return True

    def record_battle_win(
        self,
        no_damage: bool = False,
        weather_id: Optional[str] = None,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Record a battle victory and check related achievements."""
        self.stats["battles_won"] = self.stats.get("battles_won", 0) + 1
        wins = self.stats["battles_won"]

        if wins >= 1:
            self.check_and_unlock("first_victory", log)
        if wins >= 10:
            self.check_and_unlock("win_10", log)
        if wins >= 50:
            self.check_and_unlock("win_50", log)
        if wins >= 100:
            self.check_and_unlock("win_100", log)
        if no_damage:
            self.check_and_unlock("no_damage_win", log)

        if weather_id:
            weather_wins = self.stats.get("weather_wins", {})
            if not isinstance(weather_wins, dict):
                weather_wins = {}
            weather_wins[weather_id] = True
            self.stats["weather_wins"] = weather_wins
            from .weather import WEATHER_DEFINITIONS
            if len(weather_wins) >= len(WEATHER_DEFINITIONS):
                self.check_and_unlock("weather_warrior", log)

    def record_combo(self, log: Optional[List[Dict[str, str]]] = None) -> None:
        """Record a combo trigger."""
        self.stats["combos_triggered"] = self.stats.get("combos_triggered", 0) + 1
        if self.stats["combos_triggered"] >= 10:
            self.check_and_unlock("combo_master", log)

    def record_scout(self, log: Optional[List[Dict[str, str]]] = None) -> None:
        """Record a successful scout."""
        self.stats["monsters_scouted"] = self.stats.get("monsters_scouted", 0) + 1
        if self.stats["monsters_scouted"] >= 1:
            self.check_and_unlock("first_scout", log)

    def record_synthesis(
        self,
        result_rank: Optional[str] = None,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Record a synthesis."""
        self.stats["syntheses_done"] = self.stats.get("syntheses_done", 0) + 1
        count = self.stats["syntheses_done"]
        if count >= 1:
            self.check_and_unlock("first_synthesis", log)
        if count >= 10:
            self.check_and_unlock("synthesis_10", log)
        if result_rank == "S":
            self.check_and_unlock("synthesis_s_rank", log)

    def record_evolution(self, log: Optional[List[Dict[str, str]]] = None) -> None:
        """Record a monster evolution."""
        self.stats["evolutions_done"] = self.stats.get("evolutions_done", 0) + 1
        if self.stats["evolutions_done"] >= 1:
            self.check_and_unlock("evolution_first", log)

    def record_monster_book(
        self,
        total_seen: int,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Check monster book achievements."""
        if total_seen >= 10:
            self.check_and_unlock("monster_10", log)
        if total_seen >= 30:
            self.check_and_unlock("monster_30", log)

    def record_level(
        self,
        level: int,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Check level-related achievements."""
        if level >= 50:
            self.check_and_unlock("max_level", log)

    def record_gold(
        self,
        gold: int,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Check gold-related achievements."""
        if gold >= 1000:
            self.check_and_unlock("rich_1000", log)
        if gold >= 10000:
            self.check_and_unlock("rich_10000", log)

    def record_areas_visited(
        self,
        count: int,
        total_areas: int = 20,
        log: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Check exploration achievements."""
        self.stats["areas_visited"] = count
        if count >= 5:
            self.check_and_unlock("explorer_5", log)
        if count >= total_areas:
            self.check_and_unlock("explorer_all", log)

    def collect_rewards(self) -> int:
        """Collect all pending gold rewards. Returns total gold."""
        total = sum(r.get("gold", 0) for r in self.pending_rewards)
        self.pending_rewards.clear()
        return total

    def get_unlocked_list(self) -> List[Dict[str, Any]]:
        """Return list of unlocked achievements with details."""
        result = []
        for aid in self.unlocked:
            defn = ACHIEVEMENT_DEFINITIONS.get(aid, {})
            result.append({
                "id": aid,
                "name": defn.get("name", aid),
                "description": defn.get("description", ""),
                "category": defn.get("category", ""),
                "icon": defn.get("icon", ""),
            })
        return result

    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Return all achievements with unlocked status."""
        result = []
        for aid, defn in ACHIEVEMENT_DEFINITIONS.items():
            result.append({
                "id": aid,
                "name": defn.get("name", aid),
                "description": defn.get("description", ""),
                "category": defn.get("category", ""),
                "icon": defn.get("icon", ""),
                "unlocked": aid in self.unlocked,
                "reward_gold": defn.get("reward_gold", 0),
            })
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unlocked": dict(self.unlocked),
            "stats": dict(self.stats),
            "pending_rewards": list(self.pending_rewards),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AchievementManager":
        mgr = cls()
        mgr.unlocked = data.get("unlocked", {})
        mgr.stats = data.get("stats", {})
        mgr.pending_rewards = data.get("pending_rewards", [])
        return mgr
