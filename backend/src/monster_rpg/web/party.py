from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from .. import database_setup
from ..player import Player
from ..monsters.monster_data import MONSTER_BOOK_DATA
from ..items.equipment import EquipmentInstance

party_bp = Blueprint('party', __name__)

@party_bp.route('/party/<int:user_id>', endpoint='party')
def party(user_id):
    """Show the player's party."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    party_info = []
    for idx, m in enumerate(player.party_monsters):
        party_info.append({
            'monster': m,
            'detail': {
                'name': m.name,
                'level': m.level,
                'hp': m.hp,
                'max_hp': m.max_hp,
                'exp': m.exp,
                'exp_to_next': m.calculate_exp_to_next_level(),
                'image': url_for('static', filename='images/' + m.image_filename) if m.image_filename else '',
                'stats': {'attack': m.attack, 'defense': m.defense, 'speed': m.speed},
                'skills': m.get_skill_details(),
                'description': MONSTER_BOOK_DATA.get(m.monster_id).description if MONSTER_BOOK_DATA.get(m.monster_id) else 'このモンスターに関する詳しい説明はまだ見つかっていない。',
                'index': idx,
                'equipment': {slot: eq.name for slot, eq in m.equipment.items()},
                'equipment_slots': m.equipment_slots,
            },
        })
    equipment_list = [
        {
            'id': (e.instance_id if isinstance(e, EquipmentInstance) else getattr(e, 'equip_id', str(e))),
            'name': getattr(e, 'name', ''),
            'slot': getattr(e, 'slot', ''),
            'attack': getattr(e, 'total_attack', getattr(e, 'attack', 0)),
            'defense': getattr(e, 'total_defense', getattr(e, 'defense', 0)),
        }
        for e in player.equipment_inventory
    ]
    return render_template('party.html', party_info=party_info, user_id=user_id, equipment_list=equipment_list)

@party_bp.route('/equip/<int:user_id>', methods=['POST'], endpoint='equip')
def equip(user_id):
    """Equip an item from inventory to a monster."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'success': False, 'error': 'player not found'}), 404
    if request.is_json:
        data = request.get_json(silent=True) or {}
        equip_id = data.get('equip_id')
        idx = data.get('monster_idx')
        slot = data.get('slot')
    else:
        equip_id = request.form.get('equip_id')
        idx = request.form.get('monster_idx')
        slot = request.form.get('slot')
    try:
        idx_int = int(idx)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'invalid index'}), 400
    if equip_id in [None, ''] and slot is None:
        return jsonify({'success': False, 'error': 'invalid equip_id'}), 400
    success = player.equip_to_monster(idx_int, equip_id if equip_id not in ['', None] else None, slot)
    if success:
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    monster = player.party_monsters[idx_int]
    equipment_inventory = [
        {
            'id': (e.instance_id if isinstance(e, EquipmentInstance) else getattr(e, 'equip_id', str(e))),
            'name': getattr(e, 'name', ''),
        }
        for e in player.equipment_inventory
    ]
    monster_equipment = {slot: eq.name for slot, eq in monster.equipment.items()}
    return jsonify({'success': success, 'equipment_inventory': equipment_inventory, 'monster_equipment': monster_equipment})

@party_bp.route('/formation/<int:user_id>', methods=['GET', 'POST'], endpoint='formation')
def formation(user_id):
    """Allow reordering of the player's party."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        try:
            idx = int(request.form.get('index', -1))
        except (TypeError, ValueError):
            idx = -1
        move = request.form.get('move')
        if move == 'up':
            player.move_monster(idx, idx - 1)
        elif move == 'down':
            player.move_monster(idx, idx + 1)
        if 'remove' in request.form:
            player.move_to_reserve(idx)
        if 'add_index' in request.form:
            try:
                add_idx = int(request.form.get('add_index'))
                player.move_from_reserve(add_idx)
            except (TypeError, ValueError):
                pass
        if 'reset' in request.form:
            player.reset_formation()
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return render_template('formation.html', player=player, user_id=user_id)
