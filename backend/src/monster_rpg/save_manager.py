"""Utility functions for saving and loading Player data."""

from __future__ import annotations

import sqlite3
import json
from typing import Optional

from .map_data import STARTING_LOCATION_ID
from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
from .items.item_data import ALL_ITEMS
from .items.equipment import (
    create_titled_equipment,
    EquipmentInstance,
    Equipment,
    ALL_EQUIPMENT,
)
from .items.titles import ALL_TITLES
from .monster_book import MonsterBook
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .player import Player


def save_game(player: "Player", db_name: str, user_id: Optional[int] = None) -> None:
    """Persist the player's state to ``db_name``."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    if user_id is not None:
        player.user_id = user_id
    if player.user_id is None:
        player.user_id = 1

    if player.db_id:
        cursor.execute(
            """
            UPDATE player_data
            SET name=?, player_level=?, exp=?, gold=?, current_location_id=?, user_id=?
            WHERE id=?
            """,
            (
                player.name,
                player.player_level,
                player.exp,
                player.gold,
                player.current_location_id,
                player.user_id,
                player.db_id,
            ),
        )
    else:
        cursor.execute(
            """
            INSERT INTO player_data (user_id, name, player_level, exp, gold, current_location_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                player.user_id,
                player.name,
                player.player_level,
                player.exp,
                player.gold,
                player.current_location_id,
            ),
        )
        player.db_id = cursor.lastrowid

    cursor.execute("DELETE FROM party_monsters WHERE player_id=?", (player.db_id,))
    for monster in player.party_monsters:
        cursor.execute(
            "INSERT INTO party_monsters (player_id, monster_id, level, exp, hp, max_hp, mp, max_mp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                player.db_id,
                monster.monster_id,
                monster.level,
                monster.exp,
                monster.hp,
                monster.max_hp,
                monster.mp,
                monster.max_mp,
            ),
        )

    cursor.execute("DELETE FROM storage_monsters WHERE player_id=?", (player.db_id,))
    for monster in player.reserve_monsters:
        cursor.execute(
            "INSERT INTO storage_monsters (player_id, monster_id, level, exp, hp, max_hp, mp, max_mp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                player.db_id,
                monster.monster_id,
                monster.level,
                monster.exp,
                monster.hp,
                monster.max_hp,
                monster.mp,
                monster.max_mp,
            ),
        )

    cursor.execute("DELETE FROM player_items WHERE player_id=?", (player.db_id,))
    for item in player.items:
        item_id = getattr(item, "item_id", str(item))
        cursor.execute(
            "INSERT INTO player_items (player_id, item_id) VALUES (?, ?)",
            (player.db_id, item_id),
        )

    cursor.execute("DELETE FROM player_equipment WHERE player_id=?", (player.db_id,))
    for equip in player.equipment_inventory:
        if hasattr(equip, "base_item"):
            equip_id = equip.base_item.equip_id
            title_id = equip.title.title_id if getattr(equip, "title", None) else None
            instance_id = getattr(equip, "instance_id", None)
            bonuses = json.dumps(equip.random_bonuses) if getattr(equip, "random_bonuses", None) else None
        else:
            equip_id = getattr(equip, "equip_id", str(equip))
            title_id = None
            instance_id = None
            bonuses = None
        cursor.execute(
            "INSERT INTO player_equipment (player_id, equip_id, title_id, instance_id, random_bonuses) VALUES (?, ?, ?, ?, ?)",
            (player.db_id, equip_id, title_id, instance_id, bonuses),
        )

    cursor.execute(
        "DELETE FROM exploration_progress WHERE player_id=?", (player.db_id,)
    )
    for loc_id, prog in player.exploration_progress.items():
        cursor.execute(
            "INSERT INTO exploration_progress (player_id, location_id, progress) VALUES (?, ?, ?)",
            (player.db_id, loc_id, prog),
        )

    cursor.execute(
        "DELETE FROM monster_book_status WHERE player_id=?",
        (player.db_id,),
    )
    all_ids = player.monster_book.seen.union(player.monster_book.captured)
    for mid in all_ids:
        cursor.execute(
            "INSERT INTO monster_book_status (player_id, monster_id, seen, captured) VALUES (?, ?, ?, ?)",
            (
                player.db_id,
                mid,
                int(mid in player.monster_book.seen),
                int(mid in player.monster_book.captured),
            ),
        )

    conn.commit()
    conn.close()
    print(f"{player.name} のデータがセーブされました。")


def load_game(db_name: str, user_id: int = 1) -> Optional["Player"]:
    """Load the most recent save for the given user id."""
    from .player import Player  # local import to avoid circular dependency
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, player_level, exp, gold, current_location_id, user_id FROM player_data WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (user_id,),
    )
    row = cursor.fetchone()

    if row:
        db_id, name, level, exp, gold, location_id, u_id = row
        loaded_player = Player(name, player_level=level, gold=gold, user_id=u_id)
        loaded_player.exp = exp
        loaded_player.current_location_id = location_id
        loaded_player.db_id = db_id

        cursor.execute(
            "SELECT monster_id, level, exp, hp, max_hp, mp, max_mp FROM party_monsters WHERE player_id=?",
            (db_id,),
        )
        for monster_id, m_level, m_exp, hp, max_hp, mp, max_mp in cursor.fetchall():
            if monster_id in ALL_MONSTERS:
                monster = ALL_MONSTERS[monster_id].copy()
                if monster.level < m_level:
                    monster.advance_to_level(m_level, verbose=False)
                monster.exp = m_exp
                if max_hp is not None:
                    monster.max_hp = max_hp
                if hp is not None:
                    monster.hp = hp
                if max_mp is not None:
                    monster.max_mp = max_mp
                if mp is not None:
                    monster.mp = mp
                loaded_player.party_monsters.append(monster)

        cursor.execute(
            "SELECT monster_id, level, exp, hp, max_hp, mp, max_mp FROM storage_monsters WHERE player_id=?",
            (db_id,),
        )
        for monster_id, m_level, m_exp, hp, max_hp, mp, max_mp in cursor.fetchall():
            if monster_id in ALL_MONSTERS:
                monster = ALL_MONSTERS[monster_id].copy()
                if monster.level < m_level:
                    monster.advance_to_level(m_level, verbose=False)
                monster.exp = m_exp
                if max_hp is not None:
                    monster.max_hp = max_hp
                if hp is not None:
                    monster.hp = hp
                if max_mp is not None:
                    monster.max_mp = max_mp
                if mp is not None:
                    monster.mp = mp
                loaded_player.reserve_monsters.append(monster)

        cursor.execute(
            "SELECT item_id FROM player_items WHERE player_id=?",
            (db_id,),
        )
        for (item_id,) in cursor.fetchall():
            if item_id in ALL_ITEMS:
                loaded_player.items.append(ALL_ITEMS[item_id])

        cursor.execute(
            "SELECT equip_id, title_id, instance_id, random_bonuses FROM player_equipment WHERE player_id=?",
            (db_id,),
        )
        for equip_id, title_id, instance_id, bonuses_json in cursor.fetchall():
            if equip_id in ALL_EQUIPMENT:
                base = ALL_EQUIPMENT[equip_id]
                if title_id and title_id in ALL_TITLES:
                    title = ALL_TITLES[title_id]
                    bonuses = json.loads(bonuses_json) if bonuses_json else {}
                    equip = EquipmentInstance(
                        base_item=base,
                        title=title,
                        random_bonuses=bonuses,
                        instance_id=instance_id,
                    )
                else:
                    equip = base
                loaded_player.equipment_inventory.append(equip)

        cursor.execute(
            "SELECT location_id, progress FROM exploration_progress WHERE player_id=?",
            (db_id,),
        )
        for loc_id, prog in cursor.fetchall():
            loaded_player.exploration_progress[loc_id] = prog

        cursor.execute(
            "SELECT monster_id, seen, captured FROM monster_book_status WHERE player_id=?",
            (db_id,),
        )
        for mid, seen, captured in cursor.fetchall():
            if seen:
                loaded_player.monster_book.seen.add(mid)
            if captured:
                loaded_player.monster_book.captured.add(mid)

        conn.close()
        print(f"{name} のデータがロードされました。")
        return loaded_player
    else:
        conn.close()
        print("セーブデータが見つかりませんでした。")
        return None
