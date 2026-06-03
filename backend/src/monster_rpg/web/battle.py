import copy
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from ..battle import start_atb_battle, STATUS_DEFINITIONS, Battle
from .utils import load_player, save_player
from ..monsters.monster_class import Monster
from ..services import battle_service
from ..skills.skills import ALL_SKILLS

def serialize_monster(m, unit_id):
    skills = []
    for sk in m.total_skills:
        skill_id = next((sid for sid, obj in ALL_SKILLS.items() if obj.name == getattr(sk, 'name', None)), None)
        skills.append({
            'id': skill_id,
            'name': getattr(sk, 'name', ''),
            'cost': getattr(sk, 'cost', 0),
            'skill_type': getattr(sk, 'skill_type', ''),
            'target': getattr(sk, 'target', 'enemy'),
            'scope': getattr(sk, 'scope', 'single'),
            'description': getattr(sk, 'description', '')
        })

    return {
        'unit_id': unit_id,
        'monster_id': m.monster_id,
        'name': m.name,
        'level': m.level,
        'hp': m.hp,
        'max_hp': m.max_hp,
        'mp': m.mp,
        'max_mp': m.max_mp,
        'attack': m.attack,
        'defense': m.defense,
        'speed': m.speed,
        'element': m.element,
        'atb_gauge': m.atb_gauge,
        'alive': m.is_alive,
        'image': url_for('static', filename='images/' + m.image_filename) if m.image_filename else None,
        'statuses': [
            {
                'name': e['name'],
                'remaining': e['remaining'],
                'display': STATUS_DEFINITIONS.get(e['name'], {}).get('message', e['name'])
            }
            for e in m.status_effects
        ],
        'skills': skills,
    }

def deserialize_monster(data):
    # This is a simplified deserialization. In a real application, you'd
    # need to fetch the full monster data from a database or data source
    # based on monster_id and then apply the dynamic battle state (HP, MP, ATB, statuses).
    # For now, we'll just create a dummy monster with the provided stats.
    # This assumes monster_id is enough to reconstruct the base monster.
    # You might need to pass more context or have a monster factory.
    skills = []
    for sk in data.get('skills', []):
        if isinstance(sk, dict):
            sid = sk.get('id') or sk.get('name')
        else:
            sid = sk
        if sid in ALL_SKILLS:
            skills.append(copy.deepcopy(ALL_SKILLS[sid]))

    monster = Monster(
        monster_id=data['monster_id'],
        name=data['name'],
        level=data['level'],
        hp=data['hp'],
        mp=data['mp'],
        attack=data['attack'],
        defense=data['defense'],
        speed=data['speed'],
        element=data.get('element'),
        skills=skills,
        image_filename=data.get('image').split('/')[-1] if data.get('image') else None  # Extract filename from URL
    )
    monster.max_hp = data['max_hp']
    monster.max_mp = data['max_mp']
    monster.atb_gauge = data['atb_gauge']
    monster.is_alive = data['alive']
    monster.status_effects = data['statuses']
    return monster

def turn_order_ids(monsters):
    ids = []
    for actor in monsters:
        if not actor.is_alive:
            continue
        if actor.unit_id is None:
            # unit_idがNoneの場合はスキップするか、適切なデフォルト値を設定する
            # ここではスキップする
            continue
        # Assuming player party monsters have 'ally' in their unit_id and enemy monsters have 'enemy'
        # This needs to be consistent with how unit_id is assigned in serialize_monster
        if 'ally' in actor.unit_id:
            ids.append(actor.unit_id)
        else:
            ids.append(actor.unit_id)
    return ids

def serialize_battle_state(player_party, enemy_party, log, current_actor_info, turn_order_monsters):
    """Return HP/MP and status info for all monsters in the battle."""

    def serialize_unit(m):
        return {
            'hp': m.hp,
            'max_hp': m.max_hp,
            'mp': m.mp,
            'max_mp': m.max_mp,
            'alive': m.is_alive,
            'status_effects': [
                {
                    'name': e['name'],
                    'remaining': e['remaining'],
                    'display': STATUS_DEFINITIONS.get(e['name'], {}).get('message', e['name'])
                }
                for e in m.status_effects
            ],
        }

    return {
        'player': [serialize_unit(m) for m in player_party],
        'enemy': [serialize_unit(m) for m in enemy_party],
        'log': log,
        'current_actor_info': current_actor_info,
        'turn_order_monsters': [serialize_monster(m, m.unit_id) for m in turn_order_monsters]
    }

# Active battles keyed by user_id
from typing import Any

active_battles: dict[int, Any] = {}

battle_bp = Blueprint('battle', __name__)

@battle_bp.route('/battle/<int:user_id>', methods=['GET', 'POST'], endpoint='battle')
def battle(user_id):
    battle_state = active_battles.get(user_id)

    player = load_player(user_id)
    if not player and isinstance(battle_state, Battle):
        player = battle_state.player
    if not player:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        data_src = request.get_json(silent=True)
        data_src = data_src if data_src is not None else request.form

        if data_src.get('continue_explore'):
            if user_id in active_battles:
                del active_battles[user_id]
            return redirect(url_for('explore.explore', user_id=user_id), code=307)

        if isinstance(battle_state, Battle):
            battle_obj = battle_state
            player_party = battle_obj.player_party
            enemy_party = battle_obj.enemy_party
            log = battle_obj.log
            turn_order_monsters = battle_obj.turn_order
            while not battle_obj.finished and (battle_obj.current_actor is None or battle_obj.current_actor not in battle_obj.player_party):
                battle_obj.advance_turn()
        else:
            if not battle_state:
                # This should ideally not happen if battle_state is properly managed
                return jsonify({'error': 'no_active_battle'}), 404

            # Deserialize monsters from the stored battle state
            player_party = [deserialize_monster(m_data) for m_data in battle_state['player_party_data']]
            enemy_party = [deserialize_monster(m_data) for m_data in battle_state['enemy_party_data']]
            log = battle_state['log']
            turn_order_monsters = [deserialize_monster(m_data) for m_data in battle_state['turn_order_monsters_data']]

            # Reconstruct the battle object for processing the turn
            battle_obj = start_atb_battle(player_party, enemy_party, player, log, turn_order_monsters)

        battle_obj.process_player_action(battle_service.build_player_action(data_src))

        # Process AI turns until player's turn or battle ends
        while not battle_obj.finished and battle_obj.current_actor and battle_obj.current_actor not in battle_obj.player_party:
            battle_obj.process_ai_turn()

        # Update the stored battle state
        if isinstance(battle_state, Battle):
            active_battles[user_id] = battle_obj
        else:
            # Keep key names consistent with the initial stored battle state
            active_battles[user_id] = {
                'player_party_data': [serialize_monster(m, f'ally-{i}') for i, m in enumerate(battle_obj.player_party)],
                'enemy_party_data': [serialize_monster(m, f'enemy-{i}') for i, m in enumerate(battle_obj.enemy_party)],
                'log': battle_obj.log,
                'turn': battle_obj.turn_count,
                'finished': battle_obj.finished,
                'outcome': battle_obj.outcome,
                'current_actor_info': serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None,
                'turn_order_monsters_data': [serialize_monster(m, m.unit_id) for m in battle_obj.turn_order]
            }
            save_player(player, user_id)

        if battle_obj.finished:
            msgs = battle_service.apply_battle_rewards(
                player, battle_obj.outcome, player_party, enemy_party, battle_obj.log
            )
            player.last_battle_log = msgs
            del active_battles[user_id]
            save_player(player, user_id)
            html = render_template('battle.html', messages=msgs, user_id=user_id)
            return jsonify({'hp_values': serialize_battle_state(player_party, enemy_party, log, serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None, battle_obj.turn_order), 'log': msgs, 'finished': True, 'turn': battle_obj.turn_count, 'html': html, 'turn_order': turn_order_ids(battle_obj.turn_order)})
        else:
            return jsonify({
                'hp_values': serialize_battle_state(battle_obj.player_party, battle_obj.enemy_party, battle_obj.log, serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None, battle_obj.turn_order),
                'log': battle_obj.log,
                'finished': False,
                'turn': battle_obj.turn_count,
                'current_actor': serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None,
                'turn_order': turn_order_ids(battle_obj.turn_order)
            })
    else: # GET request or initial battle setup
        if not battle_state:
            battle_obj, error = battle_service.start_new_battle(player)
            if error == 'no_location':
                return redirect(url_for('main.play', user_id=user_id))
            if error == 'no_enemies':
                return render_template('result.html', message='モンスターは現れなかった。', user_id=user_id)

            # Store the initial battle state
            active_battles[user_id] = {
                'player_party_data': [serialize_monster(m, f'ally-{i}') for i, m in enumerate(battle_obj.player_party)],
                'enemy_party_data': [serialize_monster(m, f'enemy-{i}') for i, m in enumerate(battle_obj.enemy_party)],
                'log': battle_obj.log,
                'turn': battle_obj.turn_count,
                'finished': battle_obj.finished,
                'outcome': battle_obj.outcome,
                'current_actor_info': serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None,
                'turn_order_monsters_data': [serialize_monster(m, m.unit_id) for m in battle_obj.turn_order]
            }
            save_player(player, user_id)
        elif isinstance(battle_state, Battle):
            battle_obj = battle_state
            while not battle_obj.finished and (battle_obj.current_actor is None or battle_obj.current_actor not in battle_obj.player_party):
                battle_obj.advance_turn()
        else:
            # If battle state exists, reconstruct battle_obj for rendering
            player_party = [deserialize_monster(m_data) for m_data in battle_state['player_party_data']]
            enemy_party = [deserialize_monster(m_data) for m_data in battle_state['enemy_party_data']]
            log = battle_state['log']
            turn_order_monsters = [deserialize_monster(m_data) for m_data in battle_state['turn_order_monsters_data']]
            battle_obj = start_atb_battle(player_party, enemy_party, player, log, turn_order_monsters)

        init_data = {
            'ally_info': [serialize_monster(m, f'ally-{i}') for i, m in enumerate(battle_obj.player_party)],
            'enemy_info': [serialize_monster(m, f'enemy-{i}') for i, m in enumerate(battle_obj.enemy_party)],
            'items': [{'name': it.name} for it in (player.items if player else [])],
            'turn': battle_obj.turn_count,
            'log': battle_obj.log,
            'current_actor': serialize_monster(battle_obj.current_actor, battle_obj.current_actor.unit_id) if battle_obj.current_actor else None,
            'turn_order': turn_order_ids(battle_obj.turn_order)
        }
        return render_template('battle_turn.html', user_id=user_id, init_data=init_data)


@battle_bp.route('/battle-json/<int:user_id>', methods=['GET'], endpoint='battle_json')
def battle_json(user_id):
    """Return current battle state as JSON without advancing the battle."""
    battle_state = active_battles.get(user_id)
    if not battle_state:
        return jsonify({'error': 'no_active_battle'}), 404

    if isinstance(battle_state, Battle):
        battle_obj = battle_state
        player_party = battle_obj.player_party
        enemy_party = battle_obj.enemy_party
        log = battle_obj.log
        turn_order_monsters = battle_obj.turn_order
        current_actor_obj = battle_obj.current_actor
    else:
        # Support both legacy and new key names
        if 'player_party' in battle_state:
            player_party = [deserialize_monster(m_data) for m_data in battle_state['player_party']]
            enemy_party = [deserialize_monster(m_data) for m_data in battle_state['enemy_party']]
            log = battle_state['log']
            turn_order_monsters = [deserialize_monster(m_data) for m_data in battle_state['turn_order']]
            current_actor_obj = deserialize_monster(battle_state['current_actor']) if battle_state['current_actor'] else None
            turn_count = battle_state['turn_count']
            finished = battle_state['finished']
            outcome = battle_state['outcome']
        else:
            player_party = [deserialize_monster(m_data) for m_data in battle_state['player_party_data']]
            enemy_party = [deserialize_monster(m_data) for m_data in battle_state['enemy_party_data']]
            log = battle_state['log']
            turn_order_monsters = [deserialize_monster(m_data) for m_data in battle_state['turn_order_monsters_data']]
            current_actor_obj = deserialize_monster(battle_state['current_actor_info']) if battle_state['current_actor_info'] else None
            turn_count = battle_state['turn']
            finished = battle_state['finished']
            outcome = battle_state['outcome']

    # Reconstruct a dummy battle_obj for serialization purposes only
    # This is a temporary object and its methods should not be called to advance the battle
    class DummyBattle:
        def __init__(self, player_party, enemy_party, log, turn_count, finished, outcome, current_actor, turn_order):
            self.player_party = player_party
            self.enemy_party = enemy_party
            self.log = log
            self.turn_count = turn_count
            self.finished = finished
            self.outcome = outcome
            self.current_actor = current_actor
            self.turn_order = turn_order

    dummy_battle_obj = DummyBattle(
        player_party,
        enemy_party,
        log,
        turn_count if not isinstance(battle_state, Battle) else battle_obj.turn_count,
        finished if not isinstance(battle_state, Battle) else battle_obj.finished,
        outcome if not isinstance(battle_state, Battle) else battle_obj.outcome,
        current_actor_obj,
        turn_order_monsters
    )

    if dummy_battle_obj.finished:
        html = render_template('battle.html', messages=dummy_battle_obj.log, user_id=user_id)
        return jsonify({
            'hp_values': serialize_battle_state(dummy_battle_obj.player_party, dummy_battle_obj.enemy_party, dummy_battle_obj.log, serialize_monster(dummy_battle_obj.current_actor, dummy_battle_obj.current_actor.unit_id) if dummy_battle_obj.current_actor else None, dummy_battle_obj.turn_order),
            'log': dummy_battle_obj.log,
            'finished': True,
            'turn': dummy_battle_obj.turn_count,
            'html': html,
            'turn_order': turn_order_ids(dummy_battle_obj.turn_order)
        })
    else:
        return jsonify({
            'hp_values': serialize_battle_state(dummy_battle_obj.player_party, dummy_battle_obj.enemy_party, dummy_battle_obj.log, serialize_monster(dummy_battle_obj.current_actor, dummy_battle_obj.current_actor.unit_id) if dummy_battle_obj.current_actor else None, dummy_battle_obj.turn_order),
            'log': dummy_battle_obj.log,
            'finished': False,
            'turn': dummy_battle_obj.turn_count,
            'current_actor': serialize_monster(dummy_battle_obj.current_actor, dummy_battle_obj.current_actor.unit_id) if dummy_battle_obj.current_actor else None,
            'turn_order': turn_order_ids(dummy_battle_obj.turn_order)
        })
