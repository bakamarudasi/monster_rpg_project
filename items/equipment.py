from dataclasses import dataclass

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

# simple crafting recipes: item_id -> quantity
CRAFTING_RECIPES = {
    "bronze_sword": {"magic_stone": 1},
    "leather_armor": {"frost_crystal": 1},
}
