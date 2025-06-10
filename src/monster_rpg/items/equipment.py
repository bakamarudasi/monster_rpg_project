from dataclasses import dataclass, field
import uuid
import random
from typing import List

from .titles import Title, ALL_TITLES
from ..skills.skills import ALL_SKILLS

@dataclass
class Equipment:
    equip_id: str
    name: str
    slot: str
    attack: int = 0
    defense: int = 0


BRONZE_SWORD = Equipment("bronze_sword", "ブロンズソード", slot="weapon", attack=3)
LEATHER_ARMOR = Equipment("leather_armor", "レザーアーマー", slot="armor", defense=2)

ALL_EQUIPMENT = {
    BRONZE_SWORD.equip_id: BRONZE_SWORD,
    LEATHER_ARMOR.equip_id: LEATHER_ARMOR,
}


@dataclass
class EquipmentInstance:
    """Actual equipment with an optional Title attached."""
    base_item: Equipment
    title: Title | None
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
        return self.base_item.attack + bonus

    @property
    def total_defense(self) -> int:
        bonus = self.title.stat_bonuses.get("defense", 0) if self.title else 0
        return self.base_item.defense + bonus

    @property
    def total_speed(self) -> int:
        return self.title.stat_bonuses.get("speed", 0) if self.title else 0

    @property
    def granted_skills(self) -> List:
        if not self.title:
            return []
        objs = []
        for sid in self.title.added_skills:
            if sid in ALL_SKILLS:
                objs.append(ALL_SKILLS[sid])
        return objs


def create_titled_equipment(base_equip_id: str) -> EquipmentInstance | None:
    """Create EquipmentInstance with random title."""
    if base_equip_id not in ALL_EQUIPMENT:
        return None
    base_item = ALL_EQUIPMENT[base_equip_id]
    possible_titles = list(ALL_TITLES.values())
    chosen = random.choice(possible_titles)
    return EquipmentInstance(base_item=base_item, title=chosen)

# simple crafting recipes: item_id -> quantity
CRAFTING_RECIPES = {
    "bronze_sword": {"magic_stone": 1},
    "leather_armor": {"frost_crystal": 1},
}
