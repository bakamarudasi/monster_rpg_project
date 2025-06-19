from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from .. import database_setup
from ..player import Player
from ..items.equipment import Equipment, EquipmentInstance
from ..monsters.monster_class import Monster
from ..items.item_data import ALL_ITEMS
from ..monsters.monster_data import ALL_MONSTERS
from ..map_data import LOCATIONS
from .utils import process_synthesis_payload

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/items/<int:user_id>', methods=['GET', 'POST'], endpoint='items')
def items(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    message = None
    if request.method == 'POST':
        try:
            idx = int(request.form.get('item_idx', -1))
            target_idx = int(request.form.get('target_idx', -1))
        except (TypeError, ValueError):
            idx = target_idx = -1
        if 0 <= idx < len(player.items) and 0 <= target_idx < len(player.party_monsters):
            item_name = player.items[idx].name
            success = player.use_item(idx, player.party_monsters[target_idx])
            message = f"{item_name} を使った。" if success else "アイテムを使えなかった。"
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return render_template('items.html', player=player, user_id=user_id, message=message)

@inventory_bp.route('/synthesize/<int:user_id>', methods=['GET', 'POST'], endpoint='synthesize')
def synthesize(user_id):
    """Display the synthesis page and handle legacy POST requests."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    message = None
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json(silent=True) or {}
            success, msg, result = process_synthesis_payload(player, data)
            if success:
                player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
            resp = {'success': success}
            if success:
                if isinstance(result, (Equipment, EquipmentInstance)):
                    resp.update({'result_type': 'equipment', 'name': result.name})
                elif isinstance(result, Monster):
                    resp.update({'result_type': 'monster', 'name': result.name})
                else:
                    resp.update({'result_type': 'item', 'name': getattr(result, 'name', '')})
            else:
                resp['error'] = msg
            return jsonify(resp)
        try:
            idx1 = int(request.form.get('mon1', -1))
            idx2 = int(request.form.get('mon2', -1))
        except (TypeError, ValueError):
            idx1 = idx2 = -1
        success, msg, _ = player.synthesize_monster(idx1, idx2)
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        message = msg
    return render_template('synthesize.html', player=player, user_id=user_id, message=message)

@inventory_bp.route('/synthesize_action/<int:user_id>', methods=['POST'], endpoint='synthesize_action')
def synthesize_action(user_id):
    """Handle monster synthesis via JSON payload."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'success': False, 'error': 'player not found'}), 404
    if not request.is_json:
        return jsonify({'success': False, 'error': 'json required'}), 400
    data = request.get_json(silent=True) or {}
    success, msg, result = process_synthesis_payload(player, data)
    if msg in {'invalid base index', 'invalid base id', 'invalid material index', 'invalid material id', 'invalid types'} and not success:
        return jsonify({'success': False, 'error': msg}), 400
    if success:
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        resp = {'success': True}
        if isinstance(result, (Equipment, EquipmentInstance)):
            resp.update({'result_type': 'equipment', 'name': result.name})
        elif isinstance(result, Monster):
            resp.update({'result_type': 'monster', 'name': result.name})
        else:
            resp.update({'result_type': 'item', 'name': getattr(result, 'name', '')})
        return jsonify(resp)
    return jsonify({'success': False, 'error': msg})

@inventory_bp.route('/shop/<int:user_id>', methods=['GET', 'POST'], endpoint='shop')
def shop(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_shop', False):
        return redirect(url_for('main.play', user_id=user_id))
    message = None
    if request.method == 'POST':
        if 'buy_item' in request.form:
            item_id = request.form['buy_item']
            price = loc.shop_items.get(item_id)
            if price is not None and player.buy_item(item_id, price):
                name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
                message = f"{name} を購入した。"
            else:
                message = '購入できなかった。'
        elif 'buy_monster' in request.form:
            monster_id = request.form['buy_monster']
            price = loc.shop_monsters.get(monster_id)
            if price is not None and player.buy_monster(monster_id, price):
                mname = ALL_MONSTERS[monster_id].name if monster_id in ALL_MONSTERS else monster_id
                message = f"{mname} を仲間にした。"
            else:
                message = '購入できなかった。'
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    entries = []
    for iid, pr in loc.shop_items.items():
        name = ALL_ITEMS[iid].name if iid in ALL_ITEMS else iid
        entries.append(('item', iid, name, pr))
    for mid, pr in loc.shop_monsters.items():
        mname = ALL_MONSTERS[mid].name if mid in ALL_MONSTERS else mid
        entries.append(('monster', mid, mname, pr))
    return render_template('shop.html', player=player, user_id=user_id, entries=entries, message=message)

@inventory_bp.route('/inn/<int:user_id>', methods=['POST'], endpoint='inn')
def inn(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_inn', False):
        return redirect(url_for('main.play', user_id=user_id))
    cost = getattr(loc, 'inn_cost', 10)
    success = player.rest_at_inn(cost)
    msg = '宿屋で休んだ。' if success else 'お金が足りない。'
    player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return render_template('result.html', message=msg, user_id=user_id)
