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
    magic_defense: int = 0  # 魔法防御
    speed: int = 0  # Added speed stat
    critical_rate: int = 0  # 会心率（％ポイント）
    evasion_rate: int = 0   # 回避率（％ポイント）
    granted_skill_ids: List[str] = field(default_factory=list)  # 装備中に使えるスキル
    status_resist: Dict[str, float] = field(default_factory=dict)  # 状態異常耐性 (1.0=通常,0.0=無効)
    element_resist: Dict[str, float] = field(default_factory=dict)  # 属性ダメージ耐性

    @property
    def granted_skills(self) -> List:
        """装備している間だけ使えるようになるスキル（deepcopy して返す）。"""
        objs = []
        for sid in self.granted_skill_ids:
            if sid in ALL_SKILLS:
                objs.append(copy.deepcopy(ALL_SKILLS[sid]))
        return objs


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
    defense=2,
    speed=2,
)
RING_OF_REGENERATION = Equipment(
    "ring_of_regeneration",
    "再生の指輪",
    slot="accessory",
    category="accessory",
    rarity="rare",
    defense=2,
    granted_skill_ids=["regen"],  # 装備者がリジェネを使えるようになる
)
BOOTS_OF_HASTE = Equipment(
    "boots_of_haste",
    "ヘイストブーツ",
    slot="accessory",
    category="accessory",
    rarity="epic",
    speed=7,
    granted_skill_ids=["haste"],  # 味方の行動を早めるヘイストを習得
)
ELEMENTAL_GEM = Equipment(
    "elemental_gem",
    "属性の宝珠",
    slot="accessory",
    category="accessory",
    rarity="legendary",
    magic=6,
    granted_skill_ids=["fireball"],
)

# =====================================================================
# 追加装備：スキルを付与する装備＆多彩なステータス構成（種類拡張）
# =====================================================================

# --- 武器 ---
FLAME_BLADE = Equipment(
    "flame_blade", "炎刃の剣", slot="weapon", category="weapon",
    rarity="rare", attack=8, granted_skill_ids=["fireball"],
)
THUNDER_LANCE = Equipment(
    "thunder_lance", "雷神の槍", slot="weapon", category="weapon",
    rarity="rare", attack=9, speed=2, granted_skill_ids=["thunder_bolt"],
)
FROST_STAFF = Equipment(
    "frost_staff", "氷皇の杖", slot="weapon", category="weapon",
    rarity="rare", attack=2, magic=9, granted_skill_ids=["ice_spear"],
)
ASSASSIN_DAGGER = Equipment(
    "assassin_dagger", "暗殺者の短剣", slot="weapon", category="weapon",
    rarity="uncommon", attack=6, speed=8,
)
WAR_HAMMER = Equipment(
    "war_hammer", "ウォーハンマー", slot="weapon", category="weapon",
    rarity="rare", attack=15, speed=-4,
)
VORPAL_BLADE = Equipment(
    "vorpal_blade", "ヴォーパルブレード", slot="weapon", category="weapon",
    rarity="legendary", attack=14, speed=4, granted_skill_ids=["rapid_slash"],
)

# --- 防具 ---
AEGIS_SHIELD = Equipment(
    "aegis_shield", "守護の大盾", slot="armor", category="armor",
    rarity="epic", defense=14, granted_skill_ids=["barrier"],
)
ANGEL_ROBE = Equipment(
    "angel_robe", "天使の羽衣", slot="armor", category="armor",
    rarity="rare", defense=5, magic=6, granted_skill_ids=["heal"],
)
BERSERKER_MAIL = Equipment(
    "berserker_mail", "狂戦士の鎧", slot="armor", category="armor",
    rarity="rare", attack=6, defense=8, speed=2,
)
NINJA_GARB = Equipment(
    "ninja_garb", "忍びの装束", slot="armor", category="armor",
    rarity="uncommon", defense=4, speed=8,
)
PHOENIX_CLOAK = Equipment(
    "phoenix_cloak", "不死鳥のマント", slot="armor", category="armor",
    rarity="epic", defense=6, magic=4, granted_skill_ids=["revive"],
)

# --- アクセサリ ---
GAUNTLET_OF_FLURRY = Equipment(
    "gauntlet_of_flurry", "連撃の籠手", slot="accessory", category="accessory",
    rarity="rare", attack=4, speed=4, granted_skill_ids=["rapid_slash"],
)
SAGE_ORB = Equipment(
    "sage_orb", "賢者の宝珠", slot="accessory", category="accessory",
    rarity="rare", magic=6, granted_skill_ids=["spell_charge"],
)
BERSERKER_BAND = Equipment(
    "berserker_band", "猛者の腕輪", slot="accessory", category="accessory",
    rarity="rare", attack=6, granted_skill_ids=["power_charge"],
)
GUARDIAN_CHARM = Equipment(
    "guardian_charm", "守り手の護符", slot="accessory", category="accessory",
    rarity="uncommon", defense=5, granted_skill_ids=["decoy"],
)
ARCANE_LOOP = Equipment(
    "arcane_loop", "秘術の輪", slot="accessory", category="accessory",
    rarity="rare", magic=8, speed=-2,
)

# --- 耐性アクセサリ ---
WARD_OF_PURITY = Equipment(
    "ward_of_purity", "浄化の護符", slot="accessory", category="accessory",
    rarity="rare", defense=2,
    status_resist={"poison": 0.0, "spore_poison": 0.0, "curse": 0.5},
)
STALWART_BADGE = Equipment(
    "stalwart_badge", "不動の徽章", slot="accessory", category="accessory",
    rarity="rare", defense=3,
    status_resist={"stun": 0.0, "paralyze": 0.5, "sleep": 0.5, "fear": 0.5},
)
FLAME_WARD = Equipment(
    "flame_ward", "炎除けの護符", slot="accessory", category="accessory",
    rarity="uncommon", defense=2,
    status_resist={"burn": 0.0}, element_resist={"火": 0.5},
)
FROST_WARD = Equipment(
    "frost_ward", "氷除けの護符", slot="accessory", category="accessory",
    rarity="uncommon", defense=2,
    status_resist={"freeze": 0.0}, element_resist={"氷": 0.5},
)

# --- 兜（helmet スロット） ---
IRON_HELM = Equipment(
    "iron_helm", "鉄兜", slot="helmet", category="helmet", rarity="common", defense=4,
)
HORNED_HELM = Equipment(
    "horned_helm", "角兜", slot="helmet", category="helmet", rarity="uncommon", attack=3, defense=3,
)
SAGE_CIRCLET = Equipment(
    "sage_circlet", "賢者のサークレット", slot="helmet", category="helmet",
    rarity="rare", magic=6, defense=1,
)
DRAGON_HELM = Equipment(
    "dragon_helm", "竜の兜", slot="helmet", category="helmet",
    rarity="epic", defense=8, granted_skill_ids=["stone_skin"],
)

# --- 靴（boots スロット） ---
TRAVELER_BOOTS = Equipment(
    "traveler_boots", "旅人のブーツ", slot="boots", category="boots", rarity="common", speed=3,
)
IRON_GREAVES = Equipment(
    "iron_greaves", "鉄のグリーヴ", slot="boots", category="boots", rarity="uncommon", defense=5, speed=-1,
)
SWIFT_BOOTS = Equipment(
    "swift_boots", "疾風のブーツ", slot="boots", category="boots", rarity="rare", speed=8,
)
WINDWALKERS = Equipment(
    "windwalkers", "風渡りの靴", slot="boots", category="boots",
    rarity="epic", speed=9, granted_skill_ids=["teleport"],
)

# --- 新ステータス装備（会心 / 回避 / 魔防） ---
KEEN_BLADE = Equipment(
    "keen_blade", "鋭刃の剣", slot="weapon", category="weapon",
    rarity="uncommon", attack=9, critical_rate=10,
)
WARDING_ROBE = Equipment(
    "warding_robe", "魔よけのローブ", slot="armor", category="armor",
    rarity="uncommon", defense=7, magic_defense=12,
)
DRIFTER_CLOAK = Equipment(
    "drifter_cloak", "夜風の外套", slot="accessory", category="accessory",
    rarity="uncommon", speed=3, evasion_rate=12,
)
RUNE_AMULET = Equipment(
    "rune_amulet", "守紋の護符", slot="accessory", category="accessory",
    rarity="uncommon", magic_defense=8,
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
    enhance_level: int = 0

    @property
    def name(self) -> str:
        base = f"{self.title.name} {self.base_item.name}" if self.title else self.base_item.name
        if self.enhance_level > 0:
            base += f"+{self.enhance_level}"
        return base

    @property
    def slot(self) -> str:
        return self.base_item.slot

    @property
    def total_attack(self) -> int:
        bonus = self.title.stat_bonuses.get("attack", 0) if self.title else 0
        bonus += self._bonus_for("attack")
        bonus += self._enhance_bonus("attack")
        base = int(self.base_item.attack * self.stat_multiplier)
        return base + bonus

    @property
    def total_defense(self) -> int:
        bonus = self.title.stat_bonuses.get("defense", 0) if self.title else 0
        bonus += self._bonus_for("defense")
        bonus += self._enhance_bonus("defense")
        base = int(self.base_item.defense * self.stat_multiplier)
        return base + bonus

    @property
    def total_speed(self) -> int:
        bonus = self.title.stat_bonuses.get("speed", 0) if self.title else 0
        bonus += self._bonus_for("speed")
        bonus += self._enhance_bonus("speed")
        base = int(self.base_item.speed * self.stat_multiplier) # Use base_item.speed
        return base + bonus

    @property
    def granted_skills(self) -> List:
        objs = list(self.base_item.granted_skills)  # 元装備のスキルも引き継ぐ
        seen = {getattr(s, "name", None) for s in objs}
        if self.title:
            for sid in self.title.added_skills:
                obj = ALL_SKILLS.get(sid)
                if obj is not None and obj.name not in seen:
                    objs.append(copy.deepcopy(obj))
                    seen.add(obj.name)
        return objs

    @property
    def total_magic(self) -> int:
        bonus = self.title.stat_bonuses.get("magic", 0) if self.title else 0
        bonus += self._bonus_for("magic")
        bonus += self._enhance_bonus("magic")
        base = int(self.base_item.magic * self.stat_multiplier) # Use base_item.magic
        return base + bonus

    @property
    def total_magic_defense(self) -> int:
        bonus = self.title.stat_bonuses.get("magic_defense", 0) if self.title else 0
        bonus += self._bonus_for("magic_defense")
        bonus += self._enhance_bonus("magic_defense")
        base = int(getattr(self.base_item, "magic_defense", 0) * self.stat_multiplier)
        return base + bonus

    @property
    def total_critical_rate(self) -> int:
        """会心率（％ポイント）。ベース＋称号＋ランダム副ステ＋強化。"""
        bonus = self.title.stat_bonuses.get("critical_rate", 0) if self.title else 0
        bonus += self._bonus_for("critical_rate")
        bonus += self._enhance_bonus("critical_rate")
        return getattr(self.base_item, "critical_rate", 0) + bonus

    @property
    def total_evasion_rate(self) -> int:
        """回避率（％ポイント）。ベース＋称号＋ランダム副ステ＋強化。"""
        bonus = self.title.stat_bonuses.get("evasion_rate", 0) if self.title else 0
        bonus += self._bonus_for("evasion_rate")
        bonus += self._enhance_bonus("evasion_rate")
        return getattr(self.base_item, "evasion_rate", 0) + bonus

    # ------------------------------------------------------------------
    def _enhance_bonus(self, stat: str) -> int:
        """強化レベル(+N)による上昇。基礎値の約10%/レベル（最低+1/レベル）。"""
        if self.enhance_level <= 0:
            return 0
        base = getattr(self.base_item, stat, 0) or 0
        if base <= 0:
            return 0
        per_level = max(1, round(base * 0.1))
        return per_level * self.enhance_level

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


# 装備が持ちうるステータスと表示ラベル（魔防・会心率・回避率を含む）
EQUIPMENT_STAT_LABELS = [
    ("attack", "攻"), ("defense", "防"), ("magic", "魔"),
    ("magic_defense", "魔防"), ("speed", "速"),
    ("critical_rate", "会心率"), ("evasion_rate", "回避率"),
]
_PERCENT_STATS = {"critical_rate", "evasion_rate"}


def equipment_stat_summary(equip) -> list[dict]:
    """装備のゼロでないステータスを表示用に列挙する。

    EquipmentInstance は total_*、素の Equipment は属性値を見る。会心率/回避率は % 付き。
    戻り値は [{'key','label','value','display'}] の順序付きリスト。
    """
    summary = []
    for key, label in EQUIPMENT_STAT_LABELS:
        total_attr = getattr(equip, f"total_{key}", None)
        value = total_attr if total_attr is not None else getattr(equip, key, 0)
        value = int(value or 0)
        if value == 0:
            continue
        sign = "+" if value > 0 else ""
        unit = "%" if key in _PERCENT_STATS else ""
        summary.append({
            "key": key,
            "label": label,
            "value": value,
            "display": f"{label}{sign}{value}{unit}",
        })
    return summary


def _choose_amount(entry: Dict[str, Any]) -> int:
    """Return a stat amount using tiers if provided."""
    if "tiers" in entry:
        tier_weighted = []
        for tier in entry["tiers"]:
            tier_weighted.extend([tier] * tier.get("weight", 1))
        tier_choice = random.choice(tier_weighted)
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

# 追加装備のクラフトレシピ（スキル付与装備など）
CRAFTING_RECIPES["flame_blade"] = {"fire_crystal": 2, "steel_ingot": 1}
CRAFTING_RECIPES["thunder_lance"] = {"thunder_core": 2, "steel_ingot": 1}
CRAFTING_RECIPES["frost_staff"] = {"frost_crystal": 2, "magic_stone": 1}
CRAFTING_RECIPES["assassin_dagger"] = {"weapon_core_common": 2, "tough_leather": 1}
CRAFTING_RECIPES["war_hammer"] = {"steel_ingot": 4}
CRAFTING_RECIPES["vorpal_blade"] = {"weapon_core_rare": 2, "celestial_feather": 1}
CRAFTING_RECIPES["aegis_shield"] = {"armor_fragment_rare": 2, "dragon_scale": 1}
CRAFTING_RECIPES["angel_robe"] = {"armor_fragment_rare": 1, "celestial_feather": 1}
CRAFTING_RECIPES["berserker_mail"] = {"steel_ingot": 2, "tough_leather": 2}
CRAFTING_RECIPES["ninja_garb"] = {"tough_leather": 3, "armor_fragment_common": 1}
CRAFTING_RECIPES["phoenix_cloak"] = {"celestial_feather": 2, "fire_crystal": 1}
CRAFTING_RECIPES["gauntlet_of_flurry"] = {"weapon_core_common": 1, "power_fragment": 1}
CRAFTING_RECIPES["sage_orb"] = {"magic_stone": 2, "abyss_shard": 1}
CRAFTING_RECIPES["berserker_band"] = {"power_fragment": 2, "steel_ingot": 1}
CRAFTING_RECIPES["guardian_charm"] = {"armor_fragment_common": 2, "magic_stone": 1}
CRAFTING_RECIPES["arcane_loop"] = {"magic_stone": 1, "abyss_shard": 1}
CRAFTING_RECIPES["ward_of_purity"] = {"antidote": 2, "magic_stone": 1}
CRAFTING_RECIPES["stalwart_badge"] = {"armor_fragment_rare": 1, "magic_stone": 2}
CRAFTING_RECIPES["flame_ward"] = {"fire_crystal": 1, "magic_stone": 1}
CRAFTING_RECIPES["frost_ward"] = {"frost_crystal": 1, "magic_stone": 1}
# 兜・靴
CRAFTING_RECIPES["iron_helm"] = {"steel_ingot": 2}
CRAFTING_RECIPES["horned_helm"] = {"steel_ingot": 1, "tough_leather": 1}
CRAFTING_RECIPES["sage_circlet"] = {"magic_stone": 2, "armor_fragment_common": 1}
CRAFTING_RECIPES["dragon_helm"] = {"dragon_scale": 1, "armor_fragment_rare": 1}
CRAFTING_RECIPES["traveler_boots"] = {"tough_leather": 2}
CRAFTING_RECIPES["iron_greaves"] = {"steel_ingot": 2, "tough_leather": 1}
CRAFTING_RECIPES["swift_boots"] = {"tough_leather": 1, "celestial_feather": 1}
CRAFTING_RECIPES["windwalkers"] = {"celestial_feather": 2, "speed_seed": 1}
# 新ステータス装備（会心 / 回避 / 魔防）
CRAFTING_RECIPES["keen_blade"] = {"weapon_core_common": 1, "steel_ingot": 1}
CRAFTING_RECIPES["warding_robe"] = {"armor_fragment_common": 1, "magic_stone": 1}
CRAFTING_RECIPES["drifter_cloak"] = {"tough_leather": 2, "celestial_feather": 1}
CRAFTING_RECIPES["rune_amulet"] = {"magic_stone": 1, "armor_fragment_common": 1}

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
    FLAME_BLADE.equip_id: FLAME_BLADE,
    THUNDER_LANCE.equip_id: THUNDER_LANCE,
    FROST_STAFF.equip_id: FROST_STAFF,
    ASSASSIN_DAGGER.equip_id: ASSASSIN_DAGGER,
    WAR_HAMMER.equip_id: WAR_HAMMER,
    VORPAL_BLADE.equip_id: VORPAL_BLADE,
    AEGIS_SHIELD.equip_id: AEGIS_SHIELD,
    ANGEL_ROBE.equip_id: ANGEL_ROBE,
    BERSERKER_MAIL.equip_id: BERSERKER_MAIL,
    NINJA_GARB.equip_id: NINJA_GARB,
    PHOENIX_CLOAK.equip_id: PHOENIX_CLOAK,
    GAUNTLET_OF_FLURRY.equip_id: GAUNTLET_OF_FLURRY,
    SAGE_ORB.equip_id: SAGE_ORB,
    BERSERKER_BAND.equip_id: BERSERKER_BAND,
    GUARDIAN_CHARM.equip_id: GUARDIAN_CHARM,
    ARCANE_LOOP.equip_id: ARCANE_LOOP,
    WARD_OF_PURITY.equip_id: WARD_OF_PURITY,
    STALWART_BADGE.equip_id: STALWART_BADGE,
    FLAME_WARD.equip_id: FLAME_WARD,
    FROST_WARD.equip_id: FROST_WARD,
    IRON_HELM.equip_id: IRON_HELM,
    HORNED_HELM.equip_id: HORNED_HELM,
    SAGE_CIRCLET.equip_id: SAGE_CIRCLET,
    DRAGON_HELM.equip_id: DRAGON_HELM,
    TRAVELER_BOOTS.equip_id: TRAVELER_BOOTS,
    IRON_GREAVES.equip_id: IRON_GREAVES,
    SWIFT_BOOTS.equip_id: SWIFT_BOOTS,
    WINDWALKERS.equip_id: WINDWALKERS,
    KEEN_BLADE.equip_id: KEEN_BLADE,
    WARDING_ROBE.equip_id: WARDING_ROBE,
    DRIFTER_CLOAK.equip_id: DRIFTER_CLOAK,
    RUNE_AMULET.equip_id: RUNE_AMULET,
}
