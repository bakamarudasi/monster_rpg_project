import random
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from .. import database_setup
from ..player import Player
from ..items.equipment import Equipment, EquipmentInstance
from ..monsters.monster_class import Monster
from ..map_data import LOCATIONS
from ..exploration import generate_enemy_party


class Battle:
    """Stateful battle that processes actions sequentially."""

    def __init__(self, player_party: list, enemy_party: list, player: Player | None = None):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.player = player
        self.log: list[dict] = []
        self.turn = 1
        self.turn_order: list = []
        self.current_index = 0
        self.finished = False
        self.outcome: str | None = None
        self._prepare_turn()

    def _prepare_turn(self):
        alive = [m for m in self.player_party + self.enemy_party if m.is_alive]
        self.turn_order = sorted(alive, key=lambda m: m.total_speed(), reverse=True)
        self.current_index = 0
        self.log.append({'type': 'info', 'message': f'-- Turn {self.turn} --'})

    def current_actor(self):
        while self.current_index < len(self.turn_order):
            actor = self.turn_order[self.current_index]
            if actor.is_alive:
                return actor
            self.current_index += 1
        return None

    def _check_end(self) -> bool:
        if not any(e.is_alive for e in self.enemy_party):
            self.finished = True
            self.outcome = 'win'
            return True
        if not any(p.is_alive for p in self.player_party):
            self.finished = True
            self.outcome = 'lose'
            return True
        return False

    def _enemy_action(self, actor):
        target = next((m for m in self.player_party if m.is_alive), None)
        if not target:
            return
        dmg = max(1, actor.attack - target.defense)
        target.hp -= dmg
        self.log.append({'type': 'player_damage', 'message': f'{actor.name}のこうげき！{target.name}は{dmg}のダメージを受けた！'})
        if target.hp <= 0:
            target.is_alive = False
            self.log.append({'type': 'info', 'message': f'{target.name}はたおれてしまった…'})

    def _player_action(self, actor, action: dict | None):
        act = action or {'type': 'attack', 'target_enemy': 0}
        if act.get('type') == 'run':
            if random.random() < 0.5:
                self.log.append({'type': 'info', 'message': 'うまく逃げ切れた！'})
                self.finished = True
                self.outcome = 'fled'
                return
            self.log.append({'type': 'info', 'message': 'しかし逃げられなかった！'})
            return
        if act.get('type') == 'skill':
            s_idx = act.get('skill')
            if s_idx is None or s_idx >= len(actor.skills):
                self.log.append({'type': 'info', 'message': f'{actor.name} はスキルを使えなかった'})
                return
            skill = actor.skills[s_idx]
            if actor.mp < skill.cost:
                self.log.append({'type': 'info', 'message': f'{actor.name} は MP がたりない！'})
                return
            actor.mp -= skill.cost
            t_idx = act.get('target_enemy', -1)
            if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
                target = self.enemy_party[t_idx]
            else:
                target = next((e for e in self.enemy_party if e.is_alive), None)
            if not target:
                return
            dmg = max(1, skill.power - target.defense)
            target.hp -= dmg
            self.log.append({'type': 'player_attack', 'message': f'{actor.name}の{skill.name}! {target.name}に{dmg}のダメージ!'})
            if target.hp <= 0:
                target.is_alive = False
                self.log.append({'type': 'info', 'message': f'{target.name}をたおした！'})
            return
        if act.get('type') == 'scout':
            t_idx = act.get('target_enemy', -1)
            if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
                target = self.enemy_party[t_idx]
            else:
                target = next((e for e in self.enemy_party if e.is_alive), None)
            if not target:
                return
            self.log.append({'type': 'info', 'message': f'{actor.name} は {target.name} をスカウトしている...'})
            rate = getattr(target, 'scout_rate', 0.25)
            if random.random() < rate:
                self.log.append({'type': 'info', 'message': f'{target.name} は仲間になりたそうにこちらを見ている！'})
                if self.player:
                    self.player.add_monster_to_party(target)
                target.is_alive = False
            else:
                self.log.append({'type': 'info', 'message': f'{target.name} は警戒している。仲間にならなかった。'})
            return
        t_idx = act.get('target_enemy', -1)
        if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
            target = self.enemy_party[t_idx]
        else:
            target = next((e for e in self.enemy_party if e.is_alive), None)
        if not target:
            return
        dmg = max(1, actor.attack - target.defense)
        target.hp -= dmg
        self.log.append({'type': 'player_attack', 'message': f'{actor.name}のこうげき！{target.name}に{dmg}のダメージ！'})
        if target.hp <= 0:
            target.is_alive = False
            self.log.append({'type': 'info', 'message': f'{target.name}をたおした！'})

    def step(self, action: dict | None = None):
        if self.finished:
            return
        actor = self.current_actor()
        if actor is None:
            self.turn += 1
            self._prepare_turn()
            actor = self.current_actor()
            if actor is None:
                return
        if actor in self.enemy_party:
            self._enemy_action(actor)
        else:
            self._player_action(actor, action)
        if self._check_end():
            return
        self.current_index += 1
        if self.current_index >= len(self.turn_order):
            self.turn += 1
            if not self._check_end():
                self._prepare_turn()

def run_simple_battle(player_party: list, enemy_party: list):
    battle = Battle(player_party, enemy_party)
    while not battle.finished:
        actor = battle.current_actor()
        if actor in battle.player_party:
            tgt = next((i for i, e in enumerate(battle.enemy_party) if e.is_alive), -1)
            battle.step({'type': 'attack', 'target_enemy': tgt})
        else:
            battle.step()
    return battle.outcome or 'lose', battle.log

def handle_battle(player: Player, location) -> list[str]:
    msgs: list[str] = []
    enemies = generate_enemy_party(location, player)
    if not enemies:
        msgs.append('モンスターは現れなかった。')
        return msgs
    enemy_names = ', '.join(e.name for e in enemies)
    msgs.append(f'{enemy_names} が現れた！')
    party = player.party_monsters
    outcome, battle_log = run_simple_battle(party, enemies)
    msgs.extend([e['message'] if isinstance(e, dict) else e for e in battle_log])
    if outcome == 'win':
        total_exp = sum(e.level * 10 for e in enemies)
        gold_gain = sum(e.level * 5 for e in enemies)
        alive_members = [m for m in party if m.is_alive]
        if alive_members and total_exp:
            share = total_exp // len(alive_members)
            for m in alive_members:
                m.gain_exp(share)
        player.gold += gold_gain
        msgs.append(f'勝利した！ {gold_gain}G を得た。')
    else:
        msgs.append('敗北してしまった...')
    player.last_battle_log = msgs
    return msgs

# Active battles keyed by user_id
active_battles: dict[int, Battle] = {}

battle_bp = Blueprint('battle', __name__)

@battle_bp.route('/battle/<int:user_id>', methods=['GET', 'POST'], endpoint='battle')
def battle(user_id):
    battle_obj = active_battles.get(user_id)
    if battle_obj:
        player = battle_obj.player
    else:
        player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
        if not player:
            return redirect(url_for('auth.index'))
    if not battle_obj:
        if request.method == 'POST':
            if request.form.get('continue_explore'):
                return redirect(url_for('explore.explore', user_id=user_id), code=307)
            return redirect(url_for('battle.battle', user_id=user_id))
        loc = LOCATIONS.get(player.current_location_id)
        if not loc:
            return redirect(url_for('main.play', user_id=user_id))
        enemies = generate_enemy_party(loc, player)
        if not enemies:
            msg = 'モンスターは現れなかった。'
            return render_template('result.html', message=msg, user_id=user_id)
        battle_obj = Battle(player.party_monsters, enemies, player)
        enemy_names = ', '.join(e.name for e in enemies)
        battle_obj.log.append({'type': 'info', 'message': f'{enemy_names} が現れた！'})
        active_battles[user_id] = battle_obj
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    if request.method == 'POST':
        current_actor = battle_obj.current_actor()
        if current_actor in battle_obj.player_party:
            act_val = request.form.get('action', 'attack')
            if act_val == 'run':
                action = {'type': 'run'}
            elif act_val.startswith('skill'):
                try:
                    s_idx = int(act_val[5:])
                except ValueError:
                    s_idx = 0
                tgt_e = request.form.get('target_enemy', '-1')
                tgt_a = request.form.get('target_ally', '0')
                try:
                    tgt_e = int(tgt_e)
                except ValueError:
                    tgt_e = -1
                try:
                    tgt_a = int(tgt_a)
                except ValueError:
                    tgt_a = 0
                action = {'type': 'skill', 'skill': s_idx, 'target_enemy': tgt_e, 'target_ally': tgt_a}
            elif act_val == 'scout':
                tgt = request.form.get('target_enemy', '-1')
                try:
                    tgt = int(tgt)
                except ValueError:
                    tgt = -1
                action = {'type': 'scout', 'target_enemy': tgt}
            else:
                tgt = request.form.get('target_enemy', '-1')
                try:
                    tgt = int(tgt)
                except ValueError:
                    tgt = -1
                action = {'type': 'attack', 'target_enemy': tgt}
            battle_obj.step(action)
            player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        while not battle_obj.finished and battle_obj.current_actor() not in battle_obj.player_party:
            battle_obj.step()
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    else:
        while not battle_obj.finished and battle_obj.current_actor() not in battle_obj.player_party:
            battle_obj.step()
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    if battle_obj.finished:
        outcome = battle_obj.outcome
        msgs = battle_obj.log[:]
        if outcome == 'win':
            total_exp = sum(e.level * 10 for e in battle_obj.enemy_party)
            gold_gain = sum(e.level * 5 for e in battle_obj.enemy_party)
            alive_members = [m for m in player.party_monsters if m.is_alive]
            if alive_members and total_exp:
                share = total_exp // len(alive_members)
                for m in alive_members:
                    m.gain_exp(share)
            player.gold += gold_gain
            for enemy in battle_obj.enemy_party:
                for item_obj, rate in getattr(enemy, 'drop_items', []):
                    if random.random() < rate:
                        if isinstance(item_obj, (Equipment, EquipmentInstance)):
                            player.equipment_inventory.append(item_obj)
                        else:
                            player.items.append(item_obj)
                        msgs.append({'type': 'info', 'message': f'{item_obj.name} を手に入れた！'})
            msgs.append({'type': 'info', 'message': f'勝利した！ {gold_gain}G を得た。'})
        else:
            msgs.append({'type': 'info', 'message': '敗北してしまった...'})
        player.last_battle_log = msgs
        del active_battles[user_id]
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        if request.form.get('continue_explore'):
            return redirect(url_for('explore.explore', user_id=user_id))
        if request.method == 'POST':
            html = render_template('battle.html', messages=msgs, user_id=user_id)
            hp_vals = {
                'player': [{'hp': m.hp, 'max_hp': m.max_hp, 'mp': m.mp, 'max_mp': m.max_mp, 'alive': m.is_alive} for m in battle_obj.player_party],
                'enemy': [{'hp': m.hp, 'max_hp': m.max_hp, 'mp': m.mp, 'max_mp': m.max_mp, 'alive': m.is_alive} for m in battle_obj.enemy_party],
            }
            return jsonify({'hp_values': hp_vals, 'log': battle_obj.log, 'finished': True, 'turn': battle_obj.turn, 'html': html})
        return render_template('battle.html', messages=msgs, user_id=user_id)
    current_actor = battle_obj.current_actor()
    if request.method == 'POST':
        hp_vals = {
            'player': [{'hp': m.hp, 'max_hp': m.max_hp, 'mp': m.mp, 'max_mp': m.max_mp, 'alive': m.is_alive} for m in battle_obj.player_party],
            'enemy': [{'hp': m.hp, 'max_hp': m.max_hp, 'mp': m.mp, 'max_mp': m.max_mp, 'alive': m.is_alive} for m in battle_obj.enemy_party],
        }
        actor = battle_obj.current_actor()
        actor_data = None
        if actor and actor in battle_obj.player_party:
            idx = battle_obj.player_party.index(actor)
            actor_data = {
                'name': actor.name,
                'unit_id': f'ally-{idx}',
                'skills': [{'name': sk.name, 'target': getattr(sk, 'target', 'enemy'), 'scope': getattr(sk, 'scope', 'single')} for sk in actor.skills],
            }
        return jsonify({'hp_values': hp_vals, 'log': battle_obj.log, 'finished': False, 'turn': battle_obj.turn, 'current_actor': actor_data})
    return render_template('battle_turn.html', user_id=user_id, battle=battle_obj, player_party=battle_obj.player_party, enemy_party=battle_obj.enemy_party, log=battle_obj.log, current_actor=current_actor)
