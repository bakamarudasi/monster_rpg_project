from __future__ import annotations

import sqlite3
from typing import List, Dict, Any

from . import database_setup
from .player import Player
from .items.item_data import ALL_ITEMS
from .monsters.monster_data import ALL_MONSTERS
from .monsters.monster_class import Monster


def _connect():
    return sqlite3.connect(database_setup.DATABASE_NAME, timeout=5)


def list_item(player: Player, item_idx: int, price: int) -> bool:
    """List an item from the player's inventory for sale."""
    if not (0 <= item_idx < len(player.items)) or price < 0:
        return False
    item = player.items.pop(item_idx)
    item_id = getattr(item, "item_id", "")
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO market_listings (seller_id, item_type, item_id, price)
            VALUES (?, 'item', ?, ?)
            """,
            (player.user_id, item_id, price),
        )
        conn.commit()
    return True


def list_monster_from_reserve(player: Player, reserve_idx: int, price: int) -> bool:
    """List a monster from the player's reserve for sale."""
    if not (0 <= reserve_idx < len(player.reserve_monsters)) or price < 0:
        return False
    mon = player.reserve_monsters.pop(reserve_idx)
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO market_listings (
                seller_id, item_type, item_id, price,
                monster_level, monster_exp, monster_hp, monster_max_hp,
                monster_mp, monster_max_mp
            ) VALUES (?, 'monster', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                player.user_id,
                mon.monster_id,
                price,
                mon.level,
                mon.exp,
                mon.hp,
                mon.max_hp,
                mon.mp,
                mon.max_mp,
            ),
        )
        conn.commit()
    return True


def get_listings() -> List[Dict[str, Any]]:
    """Return all unsold listings."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, seller_id, item_type, item_id, price, monster_level,"
            " monster_exp, monster_hp, monster_max_hp, monster_mp, monster_max_mp"
            " FROM market_listings WHERE is_sold=0"
        )
        rows = cur.fetchall()
    listings = []
    for row in rows:
        (
            lid,
            seller_id,
            item_type,
            item_id,
            price,
            m_level,
            m_exp,
            m_hp,
            m_max_hp,
            m_mp,
            m_max_mp,
        ) = row
        listings.append(
            {
                "id": lid,
                "seller_id": seller_id,
                "item_type": item_type,
                "item_id": item_id,
                "price": price,
                "monster_level": m_level,
                "monster_exp": m_exp,
                "monster_hp": m_hp,
                "monster_max_hp": m_max_hp,
                "monster_mp": m_mp,
                "monster_max_mp": m_max_mp,
            }
        )
    return listings


def buy_listing(player: Player, listing_id: int) -> bool:
    """Purchase the given listing for the player."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT seller_id, item_type, item_id, price, monster_level,"
            " monster_exp, monster_hp, monster_max_hp, monster_mp, monster_max_mp, is_sold"
            " FROM market_listings WHERE id=?",
            (listing_id,),
        )
        row = cur.fetchone()
        if not row:
            return False
        (
            seller_id,
            item_type,
            item_id,
            price,
            m_level,
            m_exp,
            m_hp,
            m_max_hp,
            m_mp,
            m_max_mp,
            is_sold,
        ) = row
        if seller_id == player.user_id:
            return False
        if is_sold or player.gold < price:
            return False
        # deduct gold and add to seller
        cur.execute(
            "UPDATE player_data SET gold = gold + ? WHERE user_id=?",
            (price, seller_id),
        )
        player.gold -= price
        if item_type == "item":
            if item_id in ALL_ITEMS:
                player.items.append(ALL_ITEMS[item_id])
        else:
            if item_id in ALL_MONSTERS:
                mon = ALL_MONSTERS[item_id].copy()
                if mon.level < m_level:
                    mon.advance_to_level(m_level, verbose=False)
                mon.exp = m_exp
                mon.hp = m_hp if m_hp is not None else mon.max_hp
                mon.max_hp = m_max_hp if m_max_hp is not None else mon.max_hp
                mon.mp = m_mp if m_mp is not None else mon.max_mp
                mon.max_mp = m_max_mp if m_max_mp is not None else mon.max_mp
                player.party_monsters.append(mon)
        cur.execute(
            "UPDATE market_listings SET is_sold=1, buyer_id=? WHERE id=?",
            (player.user_id, listing_id),
        )
        conn.commit()
    return True
