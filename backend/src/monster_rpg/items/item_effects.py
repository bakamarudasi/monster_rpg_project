from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .item_data import Item
from ..skills.skill_actions import apply_effects

if TYPE_CHECKING:
    from ..monsters.monster_class import Monster


def apply_item_effect(item: Item, target: Optional[Monster]) -> bool:
    """Apply an item's effect to a target Monster.

    Returns True if the effect was applied successfully.
    """
    if not getattr(item, "usable", False):
        print(f"{item.name} はここでは使えない。")
        return False

    effects = getattr(item, "effects", [])
    if not effects:
        print("このアイテムはまだ効果が実装されていない。")
        return False
    if target is None:
        print("対象モンスターがいません。")
        return False
    for eff in effects:
        apply_effects(target, target, [eff], None)
    return True
