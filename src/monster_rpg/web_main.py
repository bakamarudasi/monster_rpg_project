"""Simple web interface for the Monster RPG game."""

try:
    from flask import (
        Flask,
        request,
        redirect,
        url_for,
        render_template,
        jsonify,
        session,
    )
except ImportError as e:  # pragma: no cover - dependency check
    raise SystemExit(
        "Flask is required to run this web interface. "
        "Install dependencies with 'pip install -r requirements.txt'."
    ) from e
import random

import sqlite3
from . import database_setup
from .player import Player
from .monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA
from .items.item_data import ALL_ITEMS
from .map_data import LOCATIONS, get_map_overview, get_map_grid, load_locations
from .exploration import generate_enemy_party

app = Flask(__name__)
app.secret_key = "dev-secret"

database_setup.initialize_database()
load_locations()

# Active battles keyed by user_id. Each value is a Battle instance
active_battles: dict[int, "Battle"] = {}


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
        """Calculate turn order for the new turn."""
        alive = [m for m in self.player_party + self.enemy_party if m.is_alive]
        self.turn_order = sorted(alive, key=lambda m: m.total_speed(), reverse=True)
        self.current_index = 0
        self.log.append({"type": "info", "message": f"-- Turn {self.turn} --"})

    def current_actor(self):
        """Return the monster whose action is pending."""
        while self.current_index < len(self.turn_order):
            actor = self.turn_order[self.current_index]
            if actor.is_alive:
                return actor
            self.current_index += 1
        return None

    def _check_end(self) -> bool:
        if not any(e.is_alive for e in self.enemy_party):
            self.finished = True
            self.outcome = "win"
            return True
        if not any(p.is_alive for p in self.player_party):
            self.finished = True
            self.outcome = "lose"
            return True
        return False

    def _enemy_action(self, actor):
        target = next((m for m in self.player_party if m.is_alive), None)
        if not target:
            return
        dmg = max(1, actor.attack - target.defense)
        target.hp -= dmg
        self.log.append({
            "type": "player_damage",
            "message": f"{actor.name}のこうげき！{target.name}は{dmg}のダメージを受けた！",
        })
        if target.hp <= 0:
            target.is_alive = False
            self.log.append({"type": "info", "message": f"{target.name}はたおれてしまった…"})

    def _player_action(self, actor, action: dict | None):
        act = action or {"type": "attack", "target_enemy": 0}
        if act.get("type") == "run":
            if random.random() < 0.5:
                self.log.append({"type": "info", "message": "うまく逃げ切れた！"})
                self.finished = True
                self.outcome = "fled"
                return
            self.log.append({"type": "info", "message": "しかし逃げられなかった！"})
            return

        if act.get("type") == "skill":
            s_idx = act.get("skill")
            if s_idx is None or s_idx >= len(actor.skills):
                self.log.append({"type": "info", "message": f"{actor.name} はスキルを使えなかった"})
                return
            skill = actor.skills[s_idx]
            if actor.mp < skill.cost:
                self.log.append({"type": "info", "message": f"{actor.name} は {skill.name} を使うMPが足りない"})
                return
            actor.mp -= skill.cost
            if skill.target == "ally":
                t_idx = act.get("target_ally", 0)
                if 0 <= t_idx < len(self.player_party) and self.player_party[t_idx].is_alive:
                    target = self.player_party[t_idx]
                else:
                    target = actor
                if skill.skill_type == "heal":
                    before = target.hp
                    target.hp = min(target.max_hp, target.hp + skill.power)
                    healed = target.hp - before
                    self.log.append({"type": "info", "message": f"{actor.name} は {target.name} を {skill.name} で {healed} 回復した"})
                else:
                    self.log.append({"type": "info", "message": f"{skill.name} の効果はまだ実装されていない"})
            else:
                t_idx = act.get("target_enemy", -1)
                if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
                    target = self.enemy_party[t_idx]
                else:
                    target = next((e for e in self.enemy_party if e.is_alive), None)
                if not target:
                    return
                dmg = max(1, skill.power - target.defense)
                target.hp -= dmg
                self.log.append({
                    "type": "player_attack",
                    "message": f"{actor.name} の\u300c{skill.name}\u300d！{target.name}に{dmg}のダメージ！",
                })
                if target.hp <= 0:
                    target.is_alive = False
                    self.log.append({"type": "info", "message": f"{target.name}をたおした！"})
            return

        if act.get("type") == "scout":
            t_idx = act.get("target_enemy", -1)
            if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
                target = self.enemy_party[t_idx]
            else:
                target = next((e for e in self.enemy_party if e.is_alive), None)
            if not target:
                return
            self.log.append({"type": "info", "message": f"{actor.name} は {target.name} をスカウトしている..."})
            rate = getattr(target, "scout_rate", 0.25)
            if random.random() < rate:
                self.log.append({"type": "info", "message": f"{target.name} は仲間になりたそうにこちらを見ている！"})
                if self.player:
                    self.player.add_monster_to_party(target)
                target.is_alive = False
            else:
                self.log.append({"type": "info", "message": f"{target.name} は警戒している。仲間にならなかった。"})
            return

        # default attack
        t_idx = act.get("target_enemy", -1)
        if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
            target = self.enemy_party[t_idx]
        else:
            target = next((e for e in self.enemy_party if e.is_alive), None)
        if not target:
            return
        dmg = max(1, actor.attack - target.defense)
        target.hp -= dmg
        self.log.append({"type": "player_attack", "message": f"{actor.name}のこうげき！{target.name}に{dmg}のダメージ！"})
        if target.hp <= 0:
            target.is_alive = False
            self.log.append({"type": "info", "message": f"{target.name}をたおした！"})

    def step(self, action: dict | None = None):
        """Process a single actor's action."""
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
    """Auto resolve a battle using sequential mechanics."""
    battle = Battle(player_party, enemy_party)
    while not battle.finished:
        actor = battle.current_actor()
        if actor in battle.player_party:
            tgt = next((i for i, e in enumerate(battle.enemy_party) if e.is_alive), -1)
            battle.step({"type": "attack", "target_enemy": tgt})
        else:
            battle.step()
    return battle.outcome or "lose", battle.log


def handle_battle(player: Player, location) -> list[str]:
    """Generate enemies and run a simple battle, returning log messages."""
    msgs: list[str] = []
    enemies = generate_enemy_party(location, player)
    if not enemies:
        msgs.append("モンスターは現れなかった。")
        return msgs
    enemy_names = ", ".join(e.name for e in enemies)
    msgs.append(f"{enemy_names} が現れた！")
    party = player.party_monsters
    outcome, battle_log = run_simple_battle(party, enemies)
    msgs.extend([e["message"] if isinstance(e, dict) else e for e in battle_log])
    if outcome == "win":
        total_exp = sum(e.level * 10 for e in enemies)
        gold_gain = sum(e.level * 5 for e in enemies)
        alive_members = [m for m in party if m.is_alive]
        if alive_members and total_exp:
            share = total_exp // len(alive_members)
            for m in alive_members:
                m.gain_exp(share)
        player.gold += gold_gain
        msgs.append(f"勝利した！ {gold_gain}G を得た。")
    else:
        msgs.append("敗北してしまった...")
    player.last_battle_log = msgs
    return msgs

@app.route('/')
def index():
    """Show the landing page for starting or loading a game."""
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start_game():
    """Create a new player and start the game."""
    name = request.form.get('username', 'Hero')
    try:
        user_id = database_setup.create_user(name, 'pw')
    except sqlite3.IntegrityError:
        msg = "既に同じ名前の人が存在しています"
        return render_template('result.html', message=msg, user_id=None)
    player = Player(name=name, user_id=user_id, gold=100)
    for mid in ("slime", "goblin", "wolf"):
        if mid in ALL_MONSTERS:
            player.add_monster_to_party(mid)
    player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    session['user_id'] = user_id
    return redirect(url_for('play', user_id=user_id))

@app.route('/load', methods=['POST'])
def load_existing():
    """Load an existing player by user id."""
    user_id = request.form.get('user_id')
    try:
        u_id = int(user_id)
    except (ValueError, TypeError):
        return 'invalid user id', 400
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=u_id)
    if not player:
        return 'save not found', 404
    session['user_id'] = u_id
    return redirect(url_for('play', user_id=u_id))


@app.route('/login', methods=['POST'])
def login():
    """Authenticate an existing user by username/password."""
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template(
            "result.html",
            message="ユーザー名またはパスワードが不正です",
            user_id=None,
        )

    user_id = database_setup.get_user_id(username, password)
    if not user_id:
        return render_template(
            "result.html",
            message="ユーザー名またはパスワードが違います",
            user_id=None,
        )

    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return render_template(
            "result.html",
            message="セーブデータが見つかりません",
            user_id=None,
        )

    session['user_id'] = user_id
    return redirect(url_for('play', user_id=user_id))

@app.route('/play/<int:user_id>')
def play(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    loc = LOCATIONS.get(player.current_location_id)
    connections = []
    if loc:
        for cmd, dest in loc.connections.items():
            dest_name = LOCATIONS.get(dest).name if dest in LOCATIONS else dest
            connections.append((cmd, dest, dest_name))
    return render_template(
        "play.html",
        player=player,
        loc=loc,
        connections=connections,
        user_id=user_id,
    )

@app.route('/status/<int:user_id>')
def status(user_id):
    """Display player status."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template("status.html", player=player, user_id=user_id)

@app.route('/party/<int:user_id>')
def party(user_id):
    """Show the player's party."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template("party.html", player=player, user_id=user_id)


@app.route('/monster_book/<int:user_id>')
def monster_book(user_id):
    """Show the player's monster encyclopedia."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
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
        'monster_book.html',
        entries=entries,
        completion=completion,
        user_id=user_id,
    )

@app.route('/formation/<int:user_id>', methods=['GET', 'POST'])
def formation(user_id):
    """Allow reordering of the player's party."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
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


@app.route('/items/<int:user_id>', methods=['GET', 'POST'])
def items(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
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


@app.route('/synthesize/<int:user_id>', methods=['GET', 'POST'])
def synthesize(user_id):
    """Combine two monsters from the player's party."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    message = None
    if request.method == 'POST':
        idx1 = idx2 = -1
        if request.is_json:
            data = request.get_json(silent=True) or {}
            try:
                idx1 = int(data.get('mon1', -1))
                idx2 = int(data.get('mon2', -1))
            except (TypeError, ValueError):
                idx1 = idx2 = -1
        else:
            try:
                idx1 = int(request.form.get('mon1', -1))
                idx2 = int(request.form.get('mon2', -1))
            except (TypeError, ValueError):
                idx1 = idx2 = -1
        success, msg, new_mon = player.synthesize_monster(idx1, idx2)
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        if request.is_json:
            new_mon_dict = None
            if new_mon:
                new_mon_dict = {
                    'name': new_mon.name,
                    'monster_id': getattr(new_mon, 'monster_id', None),
                    'level': new_mon.level,
                }
            return jsonify({'success': success, 'message': msg, 'new_monster': new_mon_dict})
        message = msg
    return render_template('synthesize.html', player=player, user_id=user_id, message=message)


@app.route('/shop/<int:user_id>', methods=['GET', 'POST'])
def shop(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_shop', False):
        return redirect(url_for('play', user_id=user_id))

    message = None
    if request.method == 'POST':
        if 'buy_item' in request.form:
            item_id = request.form['buy_item']
            price = loc.shop_items.get(item_id)
            if price is not None and player.buy_item(item_id, price):
                name = ALL_ITEMS[item_id].name if item_id in ALL_ITEMS else item_id
                message = f"{name} を購入した。"
            else:
                message = "購入できなかった。"
        elif 'buy_monster' in request.form:
            monster_id = request.form['buy_monster']
            price = loc.shop_monsters.get(monster_id)
            if price is not None and player.buy_monster(monster_id, price):
                mname = ALL_MONSTERS[monster_id].name if monster_id in ALL_MONSTERS else monster_id
                message = f"{mname} を仲間にした。"
            else:
                message = "購入できなかった。"
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)

    entries = []
    for iid, pr in loc.shop_items.items():
        name = ALL_ITEMS[iid].name if iid in ALL_ITEMS else iid
        entries.append(('item', iid, name, pr))
    for mid, pr in loc.shop_monsters.items():
        mname = ALL_MONSTERS[mid].name if mid in ALL_MONSTERS else mid
        entries.append(('monster', mid, mname, pr))
    return render_template('shop.html', player=player, user_id=user_id, entries=entries, message=message)


@app.route('/inn/<int:user_id>', methods=['POST'])
def inn(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_inn', False):
        return redirect(url_for('play', user_id=user_id))
    cost = getattr(loc, 'inn_cost', 10)
    success = player.rest_at_inn(cost)
    msg = '宿屋で休んだ。' if success else 'お金が足りない。'
    player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return render_template('result.html', message=msg, user_id=user_id)


@app.route('/explore/<int:user_id>', methods=['POST'])
def explore(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc:
        return redirect(url_for('play', user_id=user_id))

    messages = []
    before = player.get_exploration(player.current_location_id)
    gained = random.randint(15, 30)
    after = player.increase_exploration(player.current_location_id, gained)
    messages.append(f"探索度 {before}% -> {after}%")

    # Locations often define enemies via `enemy_pool` instead of
    # `possible_enemies`. The previous condition only checked
    # `possible_enemies`, preventing battles from triggering when
    # `enemy_pool` was present but `possible_enemies` was empty.
    if (loc.possible_enemies or getattr(loc, "enemy_pool", None)) and random.random() < loc.encounter_rate:
        enemies = generate_enemy_party(loc, player)
        if enemies:
            battle_obj = Battle(player.party_monsters, enemies, player)
            battle_obj.log.append({"type": "info", "message": f"探索度 {before}% -> {after}%"})
            enemy_names = ", ".join(e.name for e in enemies)
            battle_obj.log.append({"type": "info", "message": f"{enemy_names} が現れた！"})
            active_battles[user_id] = battle_obj

            # Process enemy turns automatically until it's the player's turn
            while (
                not battle_obj.finished
                and battle_obj.current_actor() not in battle_obj.player_party
            ):
                battle_obj.step()

            player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
            return render_template(
                'battle_turn.html',
                user_id=user_id,
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

    player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return render_template(
        'explore.html',
        messages=messages,
        user_id=user_id,
        progress=after,
        player=player,
    )


@app.route('/battle/<int:user_id>', methods=['GET', 'POST'])
def battle(user_id):
    """Interactive battle view. State is kept on the server."""
    battle_obj = active_battles.get(user_id)
    if battle_obj:
        player = battle_obj.player
    else:
        player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
        if not player:
            return redirect(url_for('index'))

    if not battle_obj:
        if request.method == 'POST':
            return redirect(url_for('battle', user_id=user_id))
        loc = LOCATIONS.get(player.current_location_id)
        if not loc:
            return redirect(url_for('play', user_id=user_id))
        enemies = generate_enemy_party(loc, player)
        if not enemies:
            msg = 'モンスターは現れなかった。'
            return render_template('result.html', message=msg, user_id=user_id)
        battle_obj = Battle(player.party_monsters, enemies, player)
        enemy_names = ", ".join(e.name for e in enemies)
        battle_obj.log.append({"type": "info", "message": f"{enemy_names} が現れた！"})
        active_battles[user_id] = battle_obj
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)

    if request.method == 'POST':
        current_actor = battle_obj.current_actor()
        if current_actor in battle_obj.player_party:
            act_val = request.form.get('action', 'attack')
            action: dict
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
        # ignore posts when it's not player's turn

        # After the player's action, process enemy turns automatically
        while not battle_obj.finished and battle_obj.current_actor() not in battle_obj.player_party:
            battle_obj.step()
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)

    else:
        # GET request - resolve enemy actions until a player turn
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
                for item_obj, rate in getattr(enemy, "drop_items", []):
                    if random.random() < rate:
                        player.items.append(item_obj)
                        msgs.append({"type": "info", "message": f"{item_obj.name} を手に入れた！"})
            msgs.append({"type": "info", "message": f"勝利した！ {gold_gain}G を得た。"})
        else:
            msgs.append({"type": "info", "message": "敗北してしまった..."})
        player.last_battle_log = msgs
        del active_battles[user_id]
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
        if request.method == 'POST':
            html = render_template('battle.html', messages=msgs, user_id=user_id)
            hp_vals = {
                'player': [{'hp': m.hp, 'max_hp': m.max_hp, 'alive': m.is_alive} for m in battle_obj.player_party],
                'enemy': [{'hp': m.hp, 'max_hp': m.max_hp, 'alive': m.is_alive} for m in battle_obj.enemy_party],
            }
            return jsonify({'hp_values': hp_vals, 'log': battle_obj.log, 'finished': True, 'turn': battle_obj.turn, 'html': html})
        return render_template('battle.html', messages=msgs, user_id=user_id)

    current_actor = battle_obj.current_actor()
    if request.method == 'POST':
        hp_vals = {
            'player': [{'hp': m.hp, 'max_hp': m.max_hp, 'alive': m.is_alive} for m in battle_obj.player_party],
            'enemy': [{'hp': m.hp, 'max_hp': m.max_hp, 'alive': m.is_alive} for m in battle_obj.enemy_party],
        }
        actor = battle_obj.current_actor()
        actor_data = None
        if actor and actor in battle_obj.player_party:
            actor_data = {
                'name': actor.name,
                'skills': [
                    {
                        'name': sk.name,
                        'target': getattr(sk, 'target', 'enemy'),
                        'scope': getattr(sk, 'scope', 'single'),
                    }
                    for sk in actor.skills
                ],
            }
        return jsonify(
            {
                'hp_values': hp_vals,
                'log': battle_obj.log,
                'finished': False,
                'turn': battle_obj.turn,
                'current_actor': actor_data,
            }
        )
    return render_template(
        'battle_turn.html',
        user_id=user_id,
        battle=battle_obj,
        player_party=battle_obj.player_party,
        enemy_party=battle_obj.enemy_party,
        log=battle_obj.log,
        current_actor=current_actor,
    )


@app.route('/map/<int:user_id>')
def world_map(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    overview = get_map_overview()
    map_grid = get_map_grid()
    return render_template(
        'map.html',
        overview=overview,
        progress=player.exploration_progress,
        locations=LOCATIONS,
        user_id=user_id,
        map_grid=map_grid,
        current_loc_id=player.current_location_id,
    )


@app.route('/battle_log/<int:user_id>')
def battle_log(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    log = getattr(player, 'last_battle_log', [])
    return render_template('battle_log.html', log=log, user_id=user_id)

@app.route('/move/<int:user_id>', methods=['POST'])
def move(user_id):
    """Move the player to another location."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return redirect(url_for('index'))
    dest = request.form.get('dest')
    if dest in LOCATIONS:
        player.current_location_id = dest
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('play', user_id=user_id))

@app.route('/save/<int:user_id>', methods=['POST'])
def save(user_id):
    """Persist the current player state to the database."""
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if player:
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('play', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
