from flask import Blueprint, render_template, redirect, url_for, request
from .. import database_setup
from ..player import Player
from .. import save_manager
from ..map_data import LOCATIONS, get_map_overview, get_map_grid
from ..monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA

main_bp = Blueprint('main', __name__)

@main_bp.route('/play/<int:user_id>', endpoint='play')
def play(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    connections = []
    if loc:
        for cmd, dest in loc.connections.items():
            dest_name = LOCATIONS.get(dest).name if dest in LOCATIONS else dest
            connections.append((cmd, dest, dest_name))
    return render_template(
        'play.html', player=player, loc=loc,
        connections=connections, user_id=user_id
    )

@main_bp.route('/status/<int:user_id>', endpoint='status')
def status(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    return render_template('status.html', player=player, user_id=user_id)

@main_bp.route('/monster_book/<int:user_id>', endpoint='monster_book')
def monster_book(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    entries = []
    for mid, entry in MONSTER_BOOK_DATA.items():
        status = 'unknown'
        if mid in player.monster_book.captured:
            status = 'captured'
        elif mid in player.monster_book.seen:
            status = 'seen'
        image_url = None
        monster_obj = ALL_MONSTERS.get(mid)
        if monster_obj and monster_obj.image_filename:
            image_url = url_for('static', filename=f"images/{monster_obj.image_filename}")
        entries.append((entry, status, image_url))
    completion = player.monster_book.completion_rate()
    return render_template(
        'monster_book.html', entries=entries, completion=completion, user_id=user_id
    )

@main_bp.route('/map/<int:user_id>', endpoint='world_map')
def world_map(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    overview = get_map_overview()
    map_grid = get_map_grid()
    return render_template(
        'map.html', overview=overview, progress=player.exploration_progress,
        locations=LOCATIONS, user_id=user_id, map_grid=map_grid,
        current_loc_id=player.current_location_id
    )

@main_bp.route('/battle_log/<int:user_id>', endpoint='battle_log')
def battle_log(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    log = getattr(player, 'last_battle_log', [])
    return render_template('battle_log.html', log=log, user_id=user_id)

@main_bp.route('/move/<int:user_id>', methods=['POST'], endpoint='move')
def move(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    dest = request.form.get('dest')
    if dest in LOCATIONS:
        loc = LOCATIONS[dest]
        req = getattr(loc, 'required_item', None)
        if req and not any(it.item_id == req for it in player.items):
            msg = f"{loc.name} に入るには {req} が必要だ。"
            return render_template('result.html', message=msg, user_id=user_id)
        player.current_location_id = dest
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('main.play', user_id=user_id))

@main_bp.route('/save/<int:user_id>', methods=['POST'], endpoint='save')
def save(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if player:
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('main.play', user_id=user_id))
