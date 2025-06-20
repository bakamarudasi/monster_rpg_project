from flask import Blueprint, jsonify, request

from .. import database_setup
from ..player import Player
from .. import save_manager
from ..trading import list_item, list_monster_from_reserve, get_listings, buy_listing

market_bp = Blueprint('market', __name__)


@market_bp.route('/market/listings')
def listings():
    return jsonify(get_listings())


@market_bp.route('/market/list_item/<int:user_id>', methods=['POST'])
def list_item_route(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'error': 'player not found'}), 404
    if not request.is_json:
        return jsonify({'error': 'json required'}), 400
    data = request.get_json(silent=True) or {}
    idx = int(data.get('item_idx', -1))
    price = int(data.get('price', -1))
    success = list_item(player, idx, price)
    if success:
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400


@market_bp.route('/market/list_monster/<int:user_id>', methods=['POST'])
def list_monster_route(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'error': 'player not found'}), 404
    if not request.is_json:
        return jsonify({'error': 'json required'}), 400
    data = request.get_json(silent=True) or {}
    idx = int(data.get('reserve_idx', -1))
    price = int(data.get('price', -1))
    success = list_monster_from_reserve(player, idx, price)
    if success:
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400


@market_bp.route('/market/buy/<int:user_id>/<int:listing_id>', methods=['POST'])
def buy_route(user_id, listing_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'error': 'player not found'}), 404
    success = buy_listing(player, listing_id)
    if success:
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400
