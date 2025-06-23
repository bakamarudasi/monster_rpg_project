"""Player data model with minimal game management logic."""

from __future__ import annotations

import logging
from .map_data import STARTING_LOCATION_ID
from .monsters.monster_class import Monster
from .monster_book import MonsterBook

from . import save_manager, party_manager, synthesis_manager

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, name: str, player_level: int = 1, gold: int = 50, user_id: int | None = None):
        self.name = name
        self.player_level = player_level
        self.exp = 0
        self.party_monsters: list[Monster] = []
        self.reserve_monsters: list[Monster] = []
        self.gold = gold
        self.items = []
        self.equipment_inventory = []
        self.current_location_id = STARTING_LOCATION_ID
        self.db_id: int | None = None
        self.user_id = user_id
        self.exploration_progress: dict[str, int] = {}
        self.monster_book = MonsterBook()
        self.last_battle_log: list[str] = []

    # --- Persistence -----------------------------------------------------
    def save_game(self, db_name: str, user_id: int | None = None) -> None:
        save_manager.save_game(self, db_name, user_id)

    @staticmethod
    def load_game(db_name: str, user_id: int = 1) -> "Player | None":
        return save_manager.load_game(db_name, user_id)

    # --- Status helpers --------------------------------------------------
    def show_status(self) -> None:
        print(f"===== {self.name} のステータス =====")
        print(f"レベル: {self.player_level}")
        print(f"経験値: {self.exp}")
        print(f"所持金: {self.gold} G")
        print(f"手持ちモンスター: {len(self.party_monsters)}体")
        if self.party_monsters:
            print("--- パーティーメンバー ---")
            for i, monster in enumerate(self.party_monsters):
                print(f"  {i+1}. {monster.name} (ID: {monster.monster_id}, Lv.{monster.level})")
            print("------------------------")
        else:
            print("  (まだ仲間モンスターがいません)")
        print("=" * 26)

    def get_exploration(self, location_id: str) -> int:
        return self.exploration_progress.get(location_id, 0)

    def increase_exploration(self, location_id: str, amount: int) -> int:
        current = self.exploration_progress.get(location_id, 0)
        new_value = min(100, current + amount)
        self.exploration_progress[location_id] = new_value
        return new_value

    # --- Party management ------------------------------------------------
    def add_monster_to_party(self, monster_id_or_object):
        return party_manager.add_monster_to_party(self, monster_id_or_object)

    def show_all_party_monsters_status(self) -> None:
        party_manager.show_all_party_monsters_status(self)

    def move_monster(self, from_idx: int, to_idx: int) -> bool:
        return party_manager.move_monster(self, from_idx, to_idx)

    def move_to_reserve(self, party_idx: int) -> bool:
        return party_manager.move_to_reserve(self, party_idx)

    def move_from_reserve(self, reserve_idx: int) -> bool:
        return party_manager.move_from_reserve(self, reserve_idx)

    def reset_formation(self) -> None:
        party_manager.reset_formation(self)

    def show_items(self) -> None:
        party_manager.show_items(self)

    def use_item(self, item_idx: int, target_monster: Monster) -> bool:
        return party_manager.use_item(self, item_idx, target_monster)

    def rest_at_inn(self, cost: int) -> bool:
        return party_manager.rest_at_inn(self, cost)

    def buy_item(self, item_id: str, price: int) -> bool:
        return party_manager.buy_item(self, item_id, price)

    def buy_monster(self, monster_id: str, price: int) -> bool:
        return party_manager.buy_monster(self, monster_id, price)

    def craft_equipment(self, equip_id: str):
        return party_manager.craft_equipment(self, equip_id)

    def equip_to_monster(self, party_idx: int, equip_id: str | None = None, slot: str | None = None) -> bool:
        return party_manager.equip_to_monster(self, party_idx, equip_id, slot)

    def disassemble_equipment(self, equip_id: str) -> bool:
        return party_manager.disassemble_equipment(self, equip_id)

    def limit_break_equipment(self, equip_id: str) -> bool:
        return party_manager.limit_break_equipment(self, equip_id)

    # --- Synthesis -------------------------------------------------------
    def synthesize_monster(self, monster1_idx: int, monster2_idx: int, item_id: str | None = None):
        return synthesis_manager.synthesize_monster(self, monster1_idx, monster2_idx, item_id)

    def synthesize_monster_with_item(self, monster_idx: int, item_id: str):
        return synthesis_manager.synthesize_monster_with_item(self, monster_idx, item_id)

    def synthesize_items(self, item1_id: str, item2_id: str):
        return synthesis_manager.synthesize_items(self, item1_id, item2_id)
