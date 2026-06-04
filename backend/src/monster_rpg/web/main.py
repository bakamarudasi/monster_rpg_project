from flask import Blueprint, render_template, redirect, url_for, request, flash
from ..map_data import LOCATIONS, get_map_overview, get_map_grid
from ..monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA
from .utils import save_player, with_player, discovered_locations

main_bp = Blueprint('main', __name__)


def _travel_to(player, user_id, dest):
    """player を dest へ移動させる。

    required_item ゲートを尊重し、出発地・到着地を「発見済み」に記録して保存する。
    戻り値は (成功したか, 対象 Location)。dest が不正なら (False, None)、
    必要アイテム不足で弾かれたら (False, loc)、移動できたら (True, loc)。
    """
    if dest not in LOCATIONS:
        return False, None
    loc = LOCATIONS[dest]
    if loc.required_item and not any(it.item_id == loc.required_item for it in player.items):
        return False, loc
    player.exploration_progress.setdefault(player.current_location_id, 0)
    player.current_location_id = dest
    player.exploration_progress.setdefault(dest, 0)
    save_player(player, user_id)
    return True, loc


@main_bp.route('/play/<int:user_id>', endpoint='play')
@with_player
def play(user_id, player):
    loc = LOCATIONS.get(player.current_location_id)
    connections = []
    if loc:
        for cmd, dest in loc.connections.items():
            dest_name = LOCATIONS.get(dest).name if dest in LOCATIONS else dest
            connections.append((cmd, dest, dest_name))
    return render_template(
        'play.html', player=player, loc=loc,
        connections=connections, user_id=user_id,
        map_grid=get_map_grid(), discovered=discovered_locations(player),
        current_loc_id=player.current_location_id
    )


@main_bp.route('/status/<int:user_id>', endpoint='status')
@with_player
def status(user_id, player):
    return render_template('status.html', player=player, user_id=user_id)


@main_bp.route('/monster_book/<int:user_id>', endpoint='monster_book')
@with_player
def monster_book(user_id, player):
    entries = []
    for mid, entry in MONSTER_BOOK_DATA.items():
        state = 'unknown'
        if mid in player.monster_book.captured:
            state = 'captured'
        elif mid in player.monster_book.seen:
            state = 'seen'
        image_url = None
        monster_obj = ALL_MONSTERS.get(mid)
        if monster_obj and monster_obj.image_filename:
            image_url = url_for('static', filename=f"images/{monster_obj.image_filename}")
        entries.append((entry, state, image_url))
    return render_template(
        'monster_book.html', entries=entries,
        completion=player.monster_book.completion_rate(), user_id=user_id
    )


@main_bp.route('/achievements/<int:user_id>', endpoint='achievements')
@with_player
def achievements(user_id, player):
    from ..achievements import ACHIEVEMENTS, BESTIARY_MILESTONES, check_achievements
    # 現在の状態で新規達成があれば解禁して保存（節目を見逃さない）
    if check_achievements(player):
        save_player(player, user_id)
    entries = [{
        'name': a['name'],
        'desc': a['desc'],
        'unlocked': a['id'] in player.achievements,
        'reward': a.get('reward', {}),
    } for a in ACHIEVEMENTS]
    captured = len(player.monster_book.captured)
    milestones = [{'n': n, 'reached': captured >= n} for n in BESTIARY_MILESTONES]
    unlocked = sum(1 for e in entries if e['unlocked'])
    return render_template(
        'achievements.html', entries=entries, milestones=milestones,
        captured=captured, total=len(MONSTER_BOOK_DATA),
        unlocked=unlocked, achievement_total=len(ACHIEVEMENTS), user_id=user_id,
    )


@main_bp.route('/quests/<int:user_id>', methods=['GET', 'POST'], endpoint='quests')
@with_player
def quests(user_id, player):
    from .. import quests as quest_mod
    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        qid = request.form.get('quest_id', '')
        if action == 'accept':
            _, message = quest_mod.accept_quest(player, qid)
        elif action == 'claim':
            _, message = quest_mod.claim_quest(player, qid)
        save_player(player, user_id)
    rows = quest_mod.quest_view(player)
    return render_template('quests.html', rows=rows, message=message, user_id=user_id)


@main_bp.route('/arena/<int:user_id>', methods=['GET', 'POST'], endpoint='arena')
@with_player
def arena(user_id, player):
    from .. import arena as arena_mod
    message = None
    if request.method == 'POST':
        try:
            tier = int(request.form.get('tier', -1))
        except (TypeError, ValueError):
            tier = -1
        _, message, _ = arena_mod.run_arena_tier(player, tier)
        save_player(player, user_id)
    rows = arena_mod.arena_view(player)
    return render_template('arena.html', rows=rows, message=message,
                           user_id=user_id, gold=player.gold)


@main_bp.route('/map/<int:user_id>', endpoint='world_map')
@with_player
def world_map(user_id, player):
    return render_template(
        'map.html', overview=get_map_overview(), progress=player.exploration_progress,
        locations=LOCATIONS, user_id=user_id, map_grid=get_map_grid(),
        current_loc_id=player.current_location_id,
        discovered=discovered_locations(player)
    )


@main_bp.route('/battle_log/<int:user_id>', endpoint='battle_log')
@with_player
def battle_log(user_id, player):
    log = getattr(player, 'last_battle_log', [])
    return render_template('battle_log.html', log=log, user_id=user_id)


@main_bp.route('/move/<int:user_id>', methods=['POST'], endpoint='move')
@with_player
def move(user_id, player):
    ok, loc = _travel_to(player, user_id, request.form.get('dest'))
    if loc and not ok:  # 必要アイテム不足で弾かれた
        msg = f"{loc.name} に入るには {loc.required_item} が必要だ。"
        return render_template('result.html', message=msg, user_id=user_id)
    return redirect(url_for('main.play', user_id=user_id))


@main_bp.route('/fast_travel/<int:user_id>', methods=['POST'], endpoint='fast_travel')
@with_player
def fast_travel(user_id, player):
    """発見済みの拠点へ地図から一気に移動する（ファストトラベル）。"""
    dest = request.form.get('dest')
    if dest not in discovered_locations(player):
        return redirect(url_for('main.play', user_id=user_id))
    ok, loc = _travel_to(player, user_id, dest)
    if loc and not ok:
        flash(f"{loc.name} に入るには {loc.required_item} が必要だ。", 'warn')
        return redirect(url_for('main.world_map', user_id=user_id))
    if ok:
        flash(f"{loc.name} へ転送した。", 'success')
    return redirect(url_for('main.play', user_id=user_id))


@main_bp.route('/save/<int:user_id>', methods=['POST'], endpoint='save')
@with_player
def save(user_id, player):
    save_player(player, user_id)
    flash('セーブしました', 'save')
    return redirect(url_for('main.play', user_id=user_id))
