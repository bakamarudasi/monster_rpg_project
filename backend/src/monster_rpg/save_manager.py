"""Utility functions for saving and loading Player data."""

from __future__ import annotations

import sqlite3
import json
import uuid
from typing import Optional

from .map_data import STARTING_LOCATION_ID
from .monsters.monster_class import Monster
from .monsters.monster_data import ALL_MONSTERS
from .skills.skills import ALL_SKILLS
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
    with sqlite3.connect(db_name, check_same_thread=False) as conn:
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

        def _skill_ids(monster):
            ids = []
            for sk in (getattr(monster, "skills", None) or []):
                nm = getattr(sk, "name", None)
                sid = next((k for k, obj in ALL_SKILLS.items() if getattr(obj, "name", None) == nm), None)
                if sid is not None:
                    ids.append(sid)
            return ids

        def _monster_row(monster):
            pb = getattr(monster, "permanent_bonuses", {}) or {}
            return (
                player.db_id,
                monster.monster_id,
                monster.level,
                monster.exp,
                monster.hp,
                monster.max_hp,
                monster.mp,
                monster.max_mp,
                int(pb.get("attack", 0)),
                int(pb.get("defense", 0)),
                int(pb.get("speed", 0)),
                int(pb.get("magic", 0)),
                int(getattr(monster, "plus_value", 0)),
                int(bool(getattr(monster, "is_rare", False))),
                json.dumps(_skill_ids(monster)),
            )

        _monster_cols = (
            "(player_id, monster_id, level, exp, hp, max_hp, mp, max_mp, "
            "bonus_attack, bonus_defense, bonus_speed, bonus_magic, plus_value, is_rare, skills) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )

        cursor.execute("DELETE FROM party_monsters WHERE player_id=?", (player.db_id,))
        for monster in player.party_monsters:
            cursor.execute("INSERT INTO party_monsters " + _monster_cols, _monster_row(monster))

        cursor.execute("DELETE FROM storage_monsters WHERE player_id=?", (player.db_id,))
        for monster in player.reserve_monsters:
            cursor.execute("INSERT INTO storage_monsters " + _monster_cols, _monster_row(monster))

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
                bonuses = (
                    json.dumps(equip.random_bonuses) if getattr(equip, "random_bonuses", None) else None
                )
            else:
                equip_id = getattr(equip, "equip_id", str(equip))
                title_id = None
                instance_id = None
                bonuses = None
            cursor.execute(
                "INSERT INTO player_equipment (player_id, equip_id, title_id, instance_id, random_bonuses, synthesis_rank, stat_multiplier, sub_stat_slots, enhance_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    player.db_id,
                    equip_id,
                    title_id,
                    instance_id,
                    bonuses,
                    getattr(equip, "synthesis_rank", 0),
                    getattr(equip, "stat_multiplier", 1.0),
                    getattr(equip, "sub_stat_slots", 0),
                    getattr(equip, "enhance_level", 0),
                ),
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

        print(f"{player.name} のデータがセーブされました。")


def load_game(db_name: str, user_id: int = 1) -> Optional["Player"]:
    """Load the most recent save for the given user id."""
    from .player import Player  # local import to avoid circular dependency
    with sqlite3.connect(db_name, check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, player_level, exp, gold, current_location_id, user_id FROM player_data WHERE user_id=? ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()

        if row:
            db_id, name, level, exp, gold, location_id, u_id = row
            loaded_player = Player(
                name,
                player_level=level,
                gold=gold,
                user_id=u_id,
            )
            loaded_player.exp = exp
            loaded_player.current_location_id = location_id
            loaded_player.db_id = db_id

            def _build_saved_monster(row):
                (monster_id, m_level, m_exp, hp, max_hp, mp, max_mp,
                 b_atk, b_def, b_spd, b_mag, plus_value, is_rare, skills_json) = row
                if monster_id not in ALL_MONSTERS:
                    return None
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
                # 永続強化（種・配合の＋値）を復元
                monster.permanent_bonuses = {
                    "attack": b_atk or 0,
                    "defense": b_def or 0,
                    "speed": b_spd or 0,
                    "magic": b_mag or 0,
                }
                monster.plus_value = plus_value or 0
                monster.is_rare = bool(is_rare)
                # 習得スキル（配合の継承など）を復元
                if skills_json:
                    try:
                        skill_ids = json.loads(skills_json)
                    except (ValueError, TypeError):
                        skill_ids = []
                    if skill_ids:
                        import copy as _copy
                        restored = [
                            _copy.deepcopy(ALL_SKILLS[sid])
                            for sid in skill_ids if sid in ALL_SKILLS
                        ]
                        if restored:
                            monster.skills = restored
                return monster

            _saved_cols = ("monster_id, level, exp, hp, max_hp, mp, max_mp, "
                           "bonus_attack, bonus_defense, bonus_speed, bonus_magic, plus_value, is_rare, skills")

            cursor.execute(
                f"SELECT {_saved_cols} FROM party_monsters WHERE player_id=?",
                (db_id,),
            )
            for row in cursor.fetchall():
                monster = _build_saved_monster(row)
                if monster is not None:
                    loaded_player.party_monsters.append(monster)

            cursor.execute(
                f"SELECT {_saved_cols} FROM storage_monsters WHERE player_id=?",
                (db_id,),
            )
            for row in cursor.fetchall():
                monster = _build_saved_monster(row)
                if monster is not None:
                    loaded_player.reserve_monsters.append(monster)

            cursor.execute(
                "SELECT item_id FROM player_items WHERE player_id=?",
                (db_id,),
            )
            for (item_id,) in cursor.fetchall():
                if item_id in ALL_ITEMS:
                    loaded_player.items.append(ALL_ITEMS[item_id])

            cursor.execute(
                "SELECT equip_id, title_id, instance_id, random_bonuses, synthesis_rank, stat_multiplier, sub_stat_slots, enhance_level FROM player_equipment WHERE player_id=?",
                (db_id,),
            )
            for equip_id, title_id, instance_id, bonuses_json, rank, mult, slots, enhance_level in cursor.fetchall():
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
                            synthesis_rank=rank or 0,
                            stat_multiplier=mult or 1.0,
                            sub_stat_slots=slots or 0,
                            enhance_level=enhance_level or 0,
                        )
                    else:
                        equip = EquipmentInstance(
                            base_item=base,
                            title=None,
                            random_bonuses=json.loads(bonuses_json) if bonuses_json else {},
                            instance_id=instance_id or str(uuid.uuid4()),
                            synthesis_rank=rank or 0,
                            stat_multiplier=mult or 1.0,
                            sub_stat_slots=slots or 0,
                            enhance_level=enhance_level or 0,
                        )
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

            print(f"{name} のデータがロードされました。")
            return loaded_player

        print("セーブデータが見つかりませんでした。")
        return None
