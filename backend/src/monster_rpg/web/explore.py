import random
from flask import Blueprint, render_template, redirect, url_for
from .. import database_setup
from ..player import Player
from .. import save_manager
from ..map_data import LOCATIONS
from ..exploration import generate_enemy_party, get_monster_instance_copy
from .battle import Battle, active_battles

explore_bp = Blueprint('explore', __name__)

@explore_bp.route('/explore/<int:user_id>', methods=['POST'], endpoint='explore')
def explore(user_id):
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc:
        return redirect(url_for('main.play', user_id=user_id))
    messages = []
    before = player.get_exploration(player.current_location_id)
    gained = random.randint(15, 30)
    after = player.increase_exploration(player.current_location_id, gained)
    messages.append(f'探索度 {before}% -> {after}%')
    if before < 100 <= after:
        if getattr(loc, 'hidden_connections', {}):
            loc.connections.update(loc.hidden_connections)
            messages.append('新たな道が開けた！')
        if getattr(loc, 'boss_enemy_id', None):
            boss_id = loc.boss_enemy_id
            boss_mon = get_monster_instance_copy(boss_id)
            boss = [boss_mon] if boss_mon else []
            if boss:
                battle_obj = Battle(player.party_monsters, boss, player)
                battle_obj.log.append({'type': 'info', 'message': 'ボスが姿を現した！'})
                active_battles[user_id] = battle_obj
                while not battle_obj.finished and battle_obj.current_actor() not in battle_obj.player_party:
                    battle_obj.step()
                save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
                return render_template(
                    'battle_turn.html',
                    user_id=user_id,
                    player=player,
                    battle=battle_obj,
                    player_party=battle_obj.player_party,
                    enemy_party=battle_obj.enemy_party,
                    log=battle_obj.log,
                    current_actor=battle_obj.current_actor(),
                )
    if (loc.possible_enemies or getattr(loc, 'enemy_pool', None)) and random.random() < loc.encounter_rate:
        enemies = generate_enemy_party(loc, player)
        if enemies:
            battle_obj = Battle(player.party_monsters, enemies, player)
            battle_obj.log.append({'type': 'info', 'message': f'探索度 {before}% -> {after}%'})
            enemy_names = ', '.join(e.name for e in enemies)
            battle_obj.log.append({'type': 'info', 'message': f'{enemy_names} が現れた！'})
            active_battles[user_id] = battle_obj
            while not battle_obj.finished and battle_obj.current_actor() not in battle_obj.player_party:
                battle_obj.step()
            save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
            return render_template(
                'battle_turn.html',
                user_id=user_id,
                player=player,
                battle=battle_obj,
                player_party=battle_obj.player_party,
                enemy_party=battle_obj.enemy_party,
                log=battle_obj.log,
                current_actor=battle_obj.current_actor(),
            )
        else:
            messages.append('モンスターは現れなかった。')
    else:
        messages.append('モンスターは現れなかった。')
    save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
    return render_template('explore.html', messages=messages, user_id=user_id, progress=after, player=player)
