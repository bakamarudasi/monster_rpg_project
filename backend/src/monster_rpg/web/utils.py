from functools import wraps
from flask import redirect, url_for
from .. import database_setup, save_manager
from ..player import Player
from ..items.equipment import Equipment


def load_player(user_id):
    """セーブデータから Player をロードする。

    永続化先（DATABASE_NAME）への結合をこの一箇所に閉じ込め、
    各ルートが DB 名を直接知らなくて済むようにする。
    """
    return save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)


def save_player(player, user_id):
    """Player をセーブする（永続化先の結合は load_player と同様にここへ集約）。"""
    return save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)


def with_player(view):
    """user_id から Player をロードして view に渡すデコレータ。

    プレイヤーが見つからなければ auth.index へリダイレクトする。
    デコレートされた view は ``def view(user_id, player, ...)`` の形で受け取る。
    （JSON を返す AJAX ルートには使わず、そちらは load_player を直接使う）
    """
    @wraps(view)
    def wrapper(user_id, *args, **kwargs):
        player = load_player(user_id)
        if not player:
            return redirect(url_for('auth.index'))
        return view(user_id, player, *args, **kwargs)
    return wrapper


def discovered_locations(player) -> set[str]:
    """発見済み（ファストトラベル可能）なロケーションIDの集合を返す。"""
    discovered = set(player.exploration_progress.keys())
    discovered.add(player.current_location_id)
    return discovered


def process_synthesis_payload(player: Player, data: dict):
    """Common logic for synthesis routes using the unified JSON format."""
    base_type = data.get("base_type")
    base_id = data.get("base_id")
    material_type = data.get("material_type")
    material_id = data.get("material_id")

    if base_type == "monster":
        try:
            base_idx = int(base_id)
        except (TypeError, ValueError):
            return False, "invalid base index", None
    else:
        if not isinstance(base_id, str):
            return False, "invalid base id", None

    if material_type == "monster":
        try:
            mat_idx = int(material_id)
        except (TypeError, ValueError):
            return False, "invalid material index", None
    else:
        if not isinstance(material_id, str):
            return False, "invalid material id", None

    if base_type == "monster" and material_type == "monster":
        inherit = data.get("inherit_skills")
        if inherit is not None and not isinstance(inherit, list):
            inherit = None
        return player.synthesize_monster(base_idx, mat_idx, inherit_skill_ids=inherit)
    if base_type == "monster" and material_type == "item":
        return player.synthesize_monster_with_item(base_idx, material_id)
    if base_type == "item" and material_type == "monster":
        return player.synthesize_monster_with_item(mat_idx, base_id)
    if base_type == "item" and material_type == "item":
        return player.synthesize_items(base_id, material_id)
    return False, "invalid types", None
