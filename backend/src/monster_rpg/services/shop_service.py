"""ショップ（購入）と宿屋のアプリケーションサービス。

ルートに散らばっていた「価格を引く→ドメイン呼び出し→結果メッセージを組む」処理を集約し、
ルートは『サービスを呼ぶ→セーブ→表示』だけにする。Flask には依存しない（loc は Location）。
"""

from __future__ import annotations

from ..items.item_data import ALL_ITEMS
from ..monsters.monster_data import ALL_MONSTERS


def buy_item(player, loc, item_id: str):
    """ショップでアイテムを購入する。戻り値 (success, message)。"""
    price = loc.shop_items.get(item_id)
    if price is not None and player.buy_item(item_id, price):
        item = ALL_ITEMS.get(item_id)
        return True, f"{item.name if item else item_id} を購入した。"
    return False, '購入できなかった。'


def buy_monster(player, loc, monster_id: str):
    """ショップでモンスターを購入（仲間化）する。戻り値 (success, message)。"""
    price = loc.shop_monsters.get(monster_id)
    if price is not None and player.buy_monster(monster_id, price):
        mon = ALL_MONSTERS.get(monster_id)
        return True, f"{mon.name if mon else monster_id} を仲間にした。"
    return False, '購入できなかった。'


def rest_at_inn(player, loc):
    """宿屋で休む。戻り値 (success, message)。"""
    cost = getattr(loc, 'inn_cost', 10)
    if player.rest_at_inn(cost):
        return True, '宿屋で休んだ。'
    return False, 'お金が足りない。'
