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
    rarity: str = "common"
    attack: int = 0
    defense: int = 0
    magic: int = 0  # Added magic stat
    speed: int = 0  # Added speed stat


BRONZE_SWORD = Equipment(
    "bronze_sword",
    "ブロンズソード",
    slot="weapon",
    category="weapon",
    rarity="common",
    attack=3,
)
LEATHER_ARMOR = Equipment(
    "leather_armor",
    "レザーアーマー",
    slot="armor",
    category="armor",
    rarity="common",
    defense=2,
)

# New Equipment Definitions (10 types)
STEEL_SWORD = Equipment(
    "steel_sword",
    "鋼の剣",
    slot="weapon",
    category="weapon",
    rarity="uncommon",
    attack=7,
)
FIRE_STAFF = Equipment(
    "fire_staff",
    "炎の杖",
    slot="weapon",
    category="weapon",
    rarity="rare",
    attack=3,
    magic=8,
)
DAGGER_OF_SWIFTNESS = Equipment(
    "dagger_of_swiftness",
    "俊足の短剣",
    slot="weapon",
    category="weapon",
    rarity="uncommon",
    attack=4,
    speed=5,
)
GREAT_AXE = Equipment(
    "great_axe",
    "グレートアックス",
    slot="weapon",
    category="weapon",
    rarity="rare",
    attack=12,
    speed=-2,
)
CHAINMAIL = Equipment(
    "chainmail",
    "鎖帷子",
    slot="armor",
    category="armor",
    rarity="uncommon",
    defense=7,
)
MAGE_ROBE = Equipment(
    "mage_robe",
    "魔術師のローブ",
    slot="armor",
    category="armor",
    rarity="rare",
    defense=4,
    magic=6,
)
TOWER_SHIELD = Equipment(
    "tower_shield",
    "タワーシールド",
    slot="armor",
    category="armor",
    rarity="epic",
    defense=15,
    speed=-3,
)
POWER_RING = Equipment(
    "power_ring",
    "力の指輪",
    slot="accessory",
    category="accessory",
    rarity="uncommon",
    attack=3,
)
DEFENSE_AMULET = Equipment(
    "defense_amulet",
    "守りのアミュレット",
    slot="accessory",
    category="accessory",
    rarity="uncommon",
    defense=3,
)
MANA_ORB = Equipment(
    "mana_orb",
    "魔力オーブ",
    slot="accessory",
    category="accessory",
    rarity="rare",
    magic=5,
)

SILVER_SWORD = Equipment(
    "silver_sword",
    "銀の剣",
    slot="weapon",
    category="weapon",
    rarity="uncommon",
    attack=5,
)

MAGIC_STAFF = Equipment(
    "magic_staff",
    "魔法の杖",
    slot="weapon",
    category="weapon",
    rarity="common",
    attack=2,
    magic=5,
)

IRON_ARMOR = Equipment(
    "iron_armor",
    "鉄の鎧",
    slot="armor",
    category="armor",
    rarity="uncommon",
    defense=5,
)

ROBE_OF_WISDOM = Equipment(
    "robe_of_wisdom",
    "知恵のローブ",
    slot="armor",
    category="armor",
    rarity="rare",
    defense=3,
    magic=7,
)

SPEED_RING = Equipment(
    "speed_ring",
    "速さの指輪",
    slot="accessory",
    category="accessory",
    rarity="uncommon",
    speed=4,
)

# New Equipment Definitions (10 types)
MYTHRIL_SWORD = Equipment(
    "mythril_sword",
    "ミスリルソード",
    slot="weapon",
    category="weapon",
    rarity="rare",
    attack=10,
    speed=3,
)
DARK_SCEPTER = Equipment(
    "dark_scepter",
    "闇の笏",
    slot="weapon",
    category="weapon",
    rarity="epic",
    attack=5,
    magic=12,
)
GLAIVE_OF_LIGHT = Equipment(
    "glaive_of_light",
    "光の戦鎌",
    slot="weapon",
    category="weapon",
    rarity="epic",
    attack=9,
    magic=9,
)
PLATE_ARMOR = Equipment(
    "plate_armor",
    "プレートアーマー",
    slot="armor",
    category="armor",
    rarity="epic",
    defense=12,
)
SILK_ROBE = Equipment(
    "silk_robe",
    "絹のローブ",
    slot="armor",
    category="armor",
    rarity="uncommon",
    defense=2,
    magic=4,
)
DRAGON_SHIELD = Equipment(
    "dragon_shield",
    "ドラゴンの盾",
    slot="armor",
    category="armor",
    rarity="legendary",
    defense=20,
)
AMULET_OF_FORTUNE = Equipment(
    "amulet_of_fortune",
    "幸運のお守り",
    slot="accessory",
    category="accessory",
    rarity="rare",
)
RING_OF_REGENERATION = Equipment(
    "ring_of_regeneration",
    "再生の指輪",
    slot="accessory",
    category="accessory",
    rarity="rare",
)
BOOTS_OF_HASTE = Equipment(
    "boots_of_haste",
    "ヘイストブーツ",
    slot="accessory",
    category="accessory",
    rarity="epic",
    speed=7,
)
ELEMENTAL_GEM = Equipment(
    "elemental_gem",
    "属性の宝珠",
    slot="accessory",
    category="accessory",
    rarity="legendary",
)


@dataclass
class EquipmentInstance:
    """Actual equipment with optional Title and random bonuses."""
    base_item: Equipment
    title: Title | None
    random_bonuses: Dict[str, Any] = field(default_factory=dict)
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    synthesis_rank: int = 0
    stat_multiplier: float = 1.0
    sub_stat_slots: int = 0

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
        base = int(self.base_item.attack * self.stat_multiplier)
        return base + bonus

    @property
    def total_defense(self) -> int:
        bonus = self.title.stat_bonuses.get("defense", 0) if self.title else 0
        bonus += self._bonus_for("defense")
        base = int(self.base_item.defense * self.stat_multiplier)
        return base + bonus

    @property
    def total_speed(self) -> int:
        bonus = self.title.stat_bonuses.get("speed", 0) if self.title else 0
        bonus += self._bonus_for("speed")
        base = int(self.base_item.speed * self.stat_multiplier) # Use base_item.speed
        return base + bonus

    @property
    def granted_skills(self) -> List:
        if not self.title:
            return []
        objs = []
        for sid in self.title.added_skills:
            if sid in ALL_SKILLS:
                objs.append(copy.deepcopy(ALL_SKILLS[sid]))
        return objs

    @property
    def total_magic(self) -> int:
        bonus = self.title.stat_bonuses.get("magic", 0) if self.title else 0
        bonus += self._bonus_for("magic")
        base = int(self.base_item.magic * self.stat_multiplier) # Use base_item.magic
        return base + bonus

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


def _choose_amount(entry: Dict[str, Any]) -> int:
    """Return a stat amount using tiers if provided."""
    if "tiers" in entry:
        tier_weighted = []
        for tier in entry["tiers"]:
            tier_weighted.extend([tier] * tier.get("weight", 1))
        tier_choice = random.choice(tier_weighted);
        if "amount" in tier_choice:
            return tier_choice["amount"]
        return random.randint(tier_choice.get("min", 1), tier_choice.get("max", 1))
    return random.randint(entry.get("min", 1), entry.get("max", 1))


def _generate_random_sub_stat(category: str, used: set[str] | None = None) -> Dict[str, Any] | None:
    """Return a single random sub stat for the given category."""
    pools = RANDOM_STAT_CONFIG.get("random_stat_pools_by_category", {}).get(category, {})
    sub_pool = pools.get("sub_stat_pool", [])
    if not sub_pool:
        return None
    weighted = []
    used = used or set()
    for entry in sub_pool:
        if entry["stat"] not in used:
            weighted.extend([entry] * entry.get("weight", 1))
    if not weighted:
        return None
    choice = random.choice(weighted)
    amount = _choose_amount(choice)
    return {"stat": choice["stat"], "amount": amount}


def _generate_random_bonuses(category: str) -> Dict[str, Any]:
    pools = RANDOM_STAT_CONFIG.get("random_stat_pools_by_category", {}).get(category, {})
    result: Dict[str, Any] = {}
    main_pool = pools.get("main_stat_pool", [])
    if main_pool:
        weighted = []
        for entry in main_pool:
            weighted.extend([entry] * entry.get("weight", 1))
        choice = random.choice(weighted)
        amount = _choose_amount(choice)
        result["main_stat"] = {"stat": choice["stat"], "amount": amount}
    sub_pool = pools.get("sub_stat_pool", [])
    if sub_pool:
        count_cfg = pools.get("sub_stat_count", {"initial_min": 0, "initial_max": 0})
        num = random.randint(count_cfg.get("initial_min", 0), count_cfg.get("initial_max", 0))
        chosen_stats = []
        stats_used = set()
        while len(chosen_stats) < num:
            bonus = _generate_random_sub_stat(category, stats_used)
            if not bonus:
                break
            chosen_stats.append(bonus)
            stats_used.add(bonus["stat"])
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
    slots = len(bonuses.get("sub_stats", []))
    return EquipmentInstance(
        base_item=base_item,
        title=chosen,
        random_bonuses=bonuses,
        sub_stat_slots=slots,
    )

# simple crafting recipes: item_id -> quantity
CRAFTING_RECIPES = {
    "bronze_sword": {"magic_stone": 1},
    "leather_armor": {"frost_crystal": 1},
    "steel_sword": {"steel_ingot": 2, "bronze_sword": 1},
    "fire_staff": {"fire_crystal": 3, "magic_stone": 1},
    "chainmail": {"steel_ingot": 3, "leather_armor": 1},
    "power_ring": {"power_fragment": 1, "magic_stone": 1},
}

# New crafting recipes
CRAFTING_RECIPES["mythril_sword"] = {"steel_sword": 1, "celestial_feather": 1}
CRAFTING_RECIPES["dark_scepter"] = {"magic_staff": 1, "abyss_shard": 2}
CRAFTING_RECIPES["plate_armor"] = {"chainmail": 1, "dragon_scale": 1}
CRAFTING_RECIPES["boots_of_haste"] = {"speed_ring": 1, "celestial_feather": 1}
CRAFTING_RECIPES["elemental_gem"] = {"fire_crystal": 1, "frost_crystal": 1, "thunder_core": 1}

ALL_EQUIPMENT = {
    BRONZE_SWORD.equip_id: BRONZE_SWORD,
    LEATHER_ARMOR.equip_id: LEATHER_ARMOR,
    SILVER_SWORD.equip_id: SILVER_SWORD,
    MAGIC_STAFF.equip_id: MAGIC_STAFF,
    IRON_ARMOR.equip_id: IRON_ARMOR,
    ROBE_OF_WISDOM.equip_id: ROBE_OF_WISDOM,
    SPEED_RING.equip_id: SPEED_RING,
    STEEL_SWORD.equip_id: STEEL_SWORD,
    FIRE_STAFF.equip_id: FIRE_STAFF,
    DAGGER_OF_SWIFTNESS.equip_id: DAGGER_OF_SWIFTNESS,
    GREAT_AXE.equip_id: GREAT_AXE,
    CHAINMAIL.equip_id: CHAINMAIL,
    MAGE_ROBE.equip_id: MAGE_ROBE,
    TOWER_SHIELD.equip_id: TOWER_SHIELD,
    POWER_RING.equip_id: POWER_RING,
    DEFENSE_AMULET.equip_id: DEFENSE_AMULET,
    MANA_ORB.equip_id: MANA_ORB,
    MYTHRIL_SWORD.equip_id: MYTHRIL_SWORD,
    DARK_SCEPTER.equip_id: DARK_SCEPTER,
    GLAIVE_OF_LIGHT.equip_id: GLAIVE_OF_LIGHT,
    PLATE_ARMOR.equip_id: PLATE_ARMOR,
    SILK_ROBE.equip_id: SILK_ROBE,
    DRAGON_SHIELD.equip_id: DRAGON_SHIELD,
    AMULET_OF_FORTUNE.equip_id: AMULET_OF_FORTUNE,
    RING_OF_REGENERATION.equip_id: RING_OF_REGENERATION,
    BOOTS_OF_HASTE.equip_id: BOOTS_OF_HASTE,
    ELEMENTAL_GEM.equip_id: ELEMENTAL_GEM,
}
