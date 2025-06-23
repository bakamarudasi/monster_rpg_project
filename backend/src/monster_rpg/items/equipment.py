from dataclasses import dataclass, field
import uuid
import random
import json
import os
from typing import List, Dict, Any
import copy

from .titles import Title, ALL_TITLES
from ..skills.skills import ALL_SKILLS

# Load random stat rules
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "equipment_random_stats.json")
try:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        RANDOM_STAT_CONFIG: Dict[str, Any] = json.load(f)
except FileNotFoundError:
    RANDOM_STAT_CONFIG = {"random_stat_pools_by_category": {}}

@dataclass
class Equipment:
    equip_id: str
    name: str
    slot: str
    category: str
    attack: int = 0
    defense: int = 0


BRONZE_SWORD = Equipment(
    "bronze_sword",
    "ブロンズソード",
    slot="weapon",
    category="weapon",
    attack=3,
)
LEATHER_ARMOR = Equipment(
    "leather_armor",
    "レザーアーマー",
    slot="armor",
    category="armor",
    defense=2,
)

ALL_EQUIPMENT = {
    BRONZE_SWORD.equip_id: BRONZE_SWORD,
    LEATHER_ARMOR.equip_id: LEATHER_ARMOR,
}


@dataclass
class EquipmentInstance:
    """Actual equipment with optional Title and random bonuses."""
    base_item: Equipment
    title: Title | None
    random_bonuses: Dict[str, Any] = field(default_factory=dict)
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def name(self) -> str:
        if self.title:
            return f"{self.title.name} {self.base_item.name}"
        return self.base_item.name

    @property
    def slot(self) -> str:
        return self.base_item.slot

    @property
    def total_attack(self) -> int:
        bonus = self.title.stat_bonuses.get("attack", 0) if self.title else 0
        bonus += self._bonus_for("attack")
        return self.base_item.attack + bonus

    @property
    def total_defense(self) -> int:
        bonus = self.title.stat_bonuses.get("defense", 0) if self.title else 0
        bonus += self._bonus_for("defense")
        return self.base_item.defense + bonus

    @property
    def total_speed(self) -> int:
        bonus = self.title.stat_bonuses.get("speed", 0) if self.title else 0
        bonus += self._bonus_for("speed")
        return bonus

    @property
    def granted_skills(self) -> List:
        if not self.title:
            return []
        objs = []
        for sid in self.title.added_skills:
            if sid in ALL_SKILLS:
                objs.append(copy.deepcopy(ALL_SKILLS[sid]))
        return objs

    # ------------------------------------------------------------------
    def _bonus_for(self, stat: str) -> int:
        total = 0
        if self.random_bonuses:
            main = self.random_bonuses.get("main_stat")
            if main and main.get("stat") == stat:
                total += int(main.get("amount", 0))
            for sub in self.random_bonuses.get("sub_stats", []):
                if sub.get("stat") == stat:
                    total += int(sub.get("amount", 0))
        return total


def _generate_random_bonuses(category: str) -> Dict[str, Any]:
    pools = RANDOM_STAT_CONFIG.get("random_stat_pools_by_category", {}).get(category, {})
    result: Dict[str, Any] = {}
    main_pool = pools.get("main_stat_pool", [])
    if main_pool:
        weighted = []
        for entry in main_pool:
            weighted.extend([entry] * entry.get("weight", 1))
        choice = random.choice(weighted)
        amount = random.randint(choice.get("min", 1), choice.get("max", 1))
        result["main_stat"] = {"stat": choice["stat"], "amount": amount}
    sub_pool = pools.get("sub_stat_pool", [])
    if sub_pool:
        weighted = []
        for entry in sub_pool:
            weighted.extend([entry] * entry.get("weight", 1))
        count_cfg = pools.get("sub_stat_count", {"initial_min": 0, "initial_max": 0})
        num = random.randint(count_cfg.get("initial_min", 0), count_cfg.get("initial_max", 0))
        chosen_stats = []
        stats_used = set()
        while weighted and len(chosen_stats) < num:
            entry = random.choice(weighted)
            if entry["stat"] in stats_used:
                weighted = [e for e in weighted if e["stat"] != entry["stat"]]
                continue
            amount = random.randint(entry.get("min", 1), entry.get("max", 1))
            chosen_stats.append({"stat": entry["stat"], "amount": amount})
            stats_used.add(entry["stat"])
            weighted = [e for e in weighted if e["stat"] != entry["stat"]]
        if chosen_stats:
            result["sub_stats"] = chosen_stats
    return result


def create_titled_equipment(base_equip_id: str) -> EquipmentInstance | None:
    """Create EquipmentInstance with random title and bonuses."""
    if base_equip_id not in ALL_EQUIPMENT:
        return None
    base_item = ALL_EQUIPMENT[base_equip_id]
    possible_titles = list(ALL_TITLES.values())
    chosen = random.choice(possible_titles)
    bonuses = _generate_random_bonuses(base_item.category)
    return EquipmentInstance(base_item=base_item, title=chosen, random_bonuses=bonuses)

# simple crafting recipes: item_id -> quantity
CRAFTING_RECIPES = {
    "bronze_sword": {"magic_stone": 1},
    "leather_armor": {"frost_crystal": 1},
}
