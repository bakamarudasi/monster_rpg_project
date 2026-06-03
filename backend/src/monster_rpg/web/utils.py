from functools import wraps
from flask import redirect, url_for
from .. import database_setup, save_manager


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
