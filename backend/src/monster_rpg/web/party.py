from flask import Blueprint, render_template, redirect, url_for, request, jsonify
import json
from .. import database_setup
from ..player import Player
from .. import save_manager
from ..monsters.monster_data import MONSTER_BOOK_DATA
from ..items.equipment import EquipmentInstance

party_bp = Blueprint('party', __name__)

@party_bp.route('/party/<int:user_id>', endpoint='party')
def party(user_id):
    """Show the player's party."""
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
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
                'stats': {
                    'attack': m.total_attack(),
                    'defense': m.total_defense(),
                    'speed': m.total_speed(),
                },
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
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
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
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
    monster = player.party_monsters[idx_int]
    equipment_inventory = [
        {
            'id': (e.instance_id if isinstance(e, EquipmentInstance) else getattr(e, 'equip_id', str(e))),
            'name': getattr(e, 'name', ''),
        }
        for e in player.equipment_inventory
    ]
    monster_equipment = {slot: eq.name for slot, eq in monster.equipment.items()}
    monster_stats = {
        'attack': monster.total_attack(),
        'defense': monster.total_defense(),
        'speed': monster.total_speed(),
    }
    return jsonify({
        'success': success,
        'equipment_inventory': equipment_inventory,
        'monster_equipment': monster_equipment,
        'monster_stats': monster_stats,
    })

@party_bp.route('/formation/<int:user_id>', methods=['GET', 'POST'], endpoint='formation')
def formation(user_id):
    """Edit the player's party formation with drag-and-drop."""
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        if 'reset' in request.form:
            player.reset_formation()
        elif request.form.get('order'):
            try:
                order_uids = json.loads(request.form.get('order'))
                reserve_uids = json.loads(request.form.get('reserve', '[]'))
            except json.JSONDecodeError:
                order_uids, reserve_uids = [], []
            all_monsters = player.party_monsters + player.reserve_monsters
            uid_map = {str(i): m for i, m in enumerate(all_monsters)}
            new_party = [uid_map[str(uid)] for uid in order_uids if str(uid) in uid_map]
            new_reserve = [uid_map[str(uid)] for uid in reserve_uids if str(uid) in uid_map]
            used = set(str(u) for u in order_uids + reserve_uids)
            for i, m in enumerate(all_monsters):
                if str(i) not in used:
                    new_reserve.append(m)
            if new_party:
                player.party_monsters = new_party
                player.reserve_monsters = new_reserve
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)

    all_monsters = player.party_monsters + player.reserve_monsters
    party_info = []
    reserve_info = []
    for uid, m in enumerate(all_monsters):
        detail = {
            'name': m.name,
            'level': m.level,
            'hp': m.hp,
            'max_hp': m.max_hp,
            'exp': m.exp,
            'exp_to_next': m.calculate_exp_to_next_level(),
            'image': url_for('static', filename='images/' + m.image_filename) if m.image_filename else '',
            'stats': {
                'attack': m.total_attack(),
                'defense': m.total_defense(),
                'speed': m.total_speed(),
            },
            'skills': m.get_skill_details(),
            'description': MONSTER_BOOK_DATA.get(m.monster_id).description if MONSTER_BOOK_DATA.get(m.monster_id) else 'このモンスターに関する詳しい説明はまだ見つかっていない。'
        }
        info = {'monster': m, 'detail': detail, 'uid': uid}
        if uid < len(player.party_monsters):
            party_info.append(info)
        else:
            reserve_info.append(info)

    return render_template('formation.html', party_info=party_info, reserve_info=reserve_info, user_id=user_id)


@party_bp.route('/manage/<int:user_id>', methods=['GET', 'POST'], endpoint='manage')
def manage(user_id):
    """Unified party view with drag-and-drop editing."""
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        if 'reset' in request.form:
            player.reset_formation()
        elif request.form.get('order'):
            try:
                order_uids = json.loads(request.form.get('order'))
                reserve_uids = json.loads(request.form.get('reserve', '[]'))
            except json.JSONDecodeError:
                order_uids, reserve_uids = [], []
            all_monsters = player.party_monsters + player.reserve_monsters
            uid_map = {str(i): m for i, m in enumerate(all_monsters)}
            new_party = [uid_map[str(uid)] for uid in order_uids if str(uid) in uid_map]
            new_reserve = [uid_map[str(uid)] for uid in reserve_uids if str(uid) in uid_map]
            used = set(str(u) for u in order_uids + reserve_uids)
            for i, m in enumerate(all_monsters):
                if str(i) not in used:
                    new_reserve.append(m)
            if new_party:
                player.party_monsters = new_party
                player.reserve_monsters = new_reserve
        save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)

    all_monsters = player.party_monsters + player.reserve_monsters
    party_info = []
    reserve_info = []
    for uid, m in enumerate(all_monsters):
        detail = {
            'name': m.name,
            'level': m.level,
            'hp': m.hp,
            'max_hp': m.max_hp,
            'exp': m.exp,
            'exp_to_next': m.calculate_exp_to_next_level(),
            'image': url_for('static', filename='images/' + m.image_filename) if m.image_filename else '',
            'stats': {
                'attack': m.total_attack(),
                'defense': m.total_defense(),
                'speed': m.total_speed(),
            },
            'skills': m.get_skill_details(),
            'description': MONSTER_BOOK_DATA.get(m.monster_id).description if MONSTER_BOOK_DATA.get(m.monster_id) else 'このモンスターに関する詳しい説明はまだ見つかっていない。',
        }
        if uid < len(player.party_monsters):
            detail.update({
                'index': uid,
                'equipment': {slot: eq.name for slot, eq in m.equipment.items()},
                'equipment_slots': m.equipment_slots,
            })
            party_info.append({'monster': m, 'detail': detail, 'uid': uid})
        else:
            reserve_info.append({'monster': m, 'detail': detail, 'uid': uid})

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

    return render_template('party_manage.html', party_info=party_info, reserve_info=reserve_info,
                           user_id=user_id, equipment_list=equipment_list)
