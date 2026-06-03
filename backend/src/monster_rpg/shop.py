"""ショップ／宿屋ドメイン：アイテム・モンスターの購入と宿泊。

購入/宿泊ロジックは長らく party_manager に同居していたが、ここ（shop.py）に集約した。
CLI 用の対話ショップ画面 open_shop もここに置く。Web からは services.shop_service が
これらを（Player ファサード経由で）呼ぶ。Flask 非依存。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .monsters.monster_data import ALL_MONSTERS
from .items.item_data import ALL_ITEMS

if TYPE_CHECKING:  # pragma: no cover
    from .player import Player
    from .map_data import Location


def buy_item(player: "Player", item_id: str, price: int) -> bool:
    if player.gold < price:
        print("お金が足りない！")
        return False
    if item_id not in ALL_ITEMS:
        print("そのアイテムは存在しない。")
        return False
    player.gold -= price
    player.items.append(ALL_ITEMS[item_id])
    print(f"{ALL_ITEMS[item_id].name} を {price}G で購入した。")
    return True


def buy_monster(player: "Player", monster_id: str, price: int) -> bool:
    if player.gold < price:
        print("お金が足りない！")
        return False
    if monster_id not in ALL_MONSTERS:
        print("そのモンスターは存在しない。")
        return False
    player.gold -= price
    player.add_monster_to_party(monster_id)
    print(f"{ALL_MONSTERS[monster_id].name} を {price}G で仲間にした。")
    return True


def rest_at_inn(player: "Player", cost: int) -> bool:
    if player.gold >= cost:
        player.gold -= cost
        print(f"{cost}G を支払い、宿屋に泊まった。")
        for monster in player.party_monsters:
            monster.hp = monster.max_hp
            monster.mp = monster.max_mp
            monster.is_alive = True
        print("パーティは完全に回復した！")
        return True
    else:
        print("お金が足りない！宿屋に泊まれない...")
        return False


def open_shop(player: "Player", location: "Location"):
    """CLI 用の対話ショップ画面。"""
    if not getattr(location, 'has_shop', False):
        print("ここにはお店はない。")
        return

    while True:
        print("\n===== ショップ =====")
        print(f"所持金: {player.gold}G")
        options = []
        idx = 1
        for item_id, price in getattr(location, 'shop_items', {}).items():
            item = ALL_ITEMS.get(item_id)
            if item:
                options.append(('item', item_id, price))
                print(f"{idx}: {item.name} - {price}G")
                idx += 1
        for monster_id, price in getattr(location, 'shop_monsters', {}).items():
            monster = ALL_MONSTERS.get(monster_id)
            if monster:
                options.append(('monster', monster_id, price))
                print(f"{idx}: {monster.name} - {price}G")
                idx += 1
        print("0: やめる")

        choice = input("購入する番号を選んでください: ")
        if not choice.isdigit():
            print("数字で入力してください。")
            continue
        c = int(choice)
        if c == 0:
            break
        if 1 <= c <= len(options):
            kind, obj_id, price = options[c-1]
            if kind == 'item':
                player.buy_item(obj_id, price)
            else:
                player.buy_monster(obj_id, price)
        else:
            print("無効な選択です。")
