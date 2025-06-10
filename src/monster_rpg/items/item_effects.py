from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .item_data import Item

if TYPE_CHECKING:
    from ..monsters.monster_class import Monster


def apply_item_effect(item: Item, target: Optional[Monster]) -> bool:
    """Apply an item's effect to a target Monster.

    Returns True if the effect was applied successfully.
    """
    if not getattr(item, "usable", False):
        print(f"{item.name} はここでは使えない。")
        return False

    effect = getattr(item, "effect", {})
    if not effect:
        print("このアイテムはまだ効果が実装されていない。")
        return False

    etype = effect.get("type")

    if etype == "heal_hp":
        if target is None:
            print("対象モンスターがいません。")
            return False
        if not target.is_alive:
            print(f"{target.name} は倒れているため回復できない。")
            return False
        amount = effect.get("amount", 0)
        before = target.hp
        target.hp = min(target.max_hp, target.hp + amount)
        healed = target.hp - before
        print(f"{target.name} のHPが {healed} 回復した。")
        return True

    if etype == "heal_mp":
        if target is None:
            print("対象モンスターがいません。")
            return False
        amount = effect.get("amount", 0)
        before = target.mp
        target.mp = min(target.max_mp, target.mp + amount)
        restored = target.mp - before
        print(f"{target.name} のMPが {restored} 回復した。")
        return True

    if etype == "heal_full":
        if target is None:
            print("対象モンスターがいません。")
            return False
        if not target.is_alive:
            print(f"{target.name} は倒れているため回復できない。")
            return False
        target.hp = target.max_hp
        target.mp = target.max_mp
        print(f"{target.name} のHPとMPが全回復した！")
        return True

    if etype == "revive":
        if target is None:
            print("対象モンスターがいません。")
            return False
        if target.is_alive:
            print(f"{target.name} はまだ倒れていない。")
            return False
        target.is_alive = True
        amount = effect.get("amount", "half")
        if amount == "half":
            target.hp = target.max_hp // 2
        else:
            try:
                target.hp = min(target.max_hp, int(amount))
            except (TypeError, ValueError):
                target.hp = target.max_hp // 2
        print(f"{target.name} が復活した！ HPが半分回復した。")
        return True

    if etype == "cure_status":
        if target is None:
            print("対象モンスターがいません。")
            return False
        status = effect.get("status")
        before = len(target.status_effects)
        target.status_effects = [e for e in target.status_effects if e["name"] != status]
        if len(target.status_effects) < before:
            print(f"{target.name} の {status} が治った。")
            return True
        print(f"{target.name} は {status} 状態ではない。")
        return False

    print("このアイテムはまだ効果が実装されていない。")
    return False
