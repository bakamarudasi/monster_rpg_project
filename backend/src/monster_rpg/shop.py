# shop.py
from .player import Player
from .monsters import ALL_MONSTERS
from .map_data import Location
from .items.item_data import ALL_ITEMS


def open_shop(player: Player, location: Location):
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
