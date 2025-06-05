"""Simple web interface for the Monster RPG game."""

try:
    from flask import Flask, request, redirect, url_for, render_template
except ImportError as e:  # pragma: no cover - dependency check
    raise SystemExit(
        "Flask is required to run this web interface. "
        "Install dependencies with 'pip install -r requirements.txt'."
    ) from e
import random

import database_setup
import sqlite3
from player import Player
from monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA
from items.item_data import ALL_ITEMS
from map_data import LOCATIONS, get_map_overview
from exploration import generate_enemy_party

app = Flask(__name__)

database_setup.initialize_database()

# In-memory store of active players keyed by user_id
active_players: dict[int, Player] = {}

# Active battles keyed by user_id. Each value is a Battle instance
active_battles: dict[int, "Battle"] = {}


class Battle:
    """Stateful battle handling one turn at a time."""

    def __init__(self, player_party: list, enemy_party: list):
        self.player_party = player_party
        self.enemy_party = enemy_party
        self.log: list[str] = []
        self.turn = 1
        self.finished = False
        self.outcome: str | None = None

    def next_turn(self, targets: list[int]):
        """Process one turn using provided target indexes for each player monster."""
        if self.finished:
            return
        self.log.append(f"-- Turn {self.turn} --")

        # Player side
        for idx, actor in enumerate(self.player_party):
            if not actor.is_alive:
                continue
            t_idx = targets[idx] if idx < len(targets) else -1
            target = None
            if 0 <= t_idx < len(self.enemy_party) and self.enemy_party[t_idx].is_alive:
                target = self.enemy_party[t_idx]
            else:
                target = next((e for e in self.enemy_party if e.is_alive), None)
            if not target:
                break
            dmg = max(1, actor.attack - target.defense)
            target.hp -= dmg
            self.log.append(f"{actor.name} attacks {target.name} for {dmg}")
            if target.hp <= 0:
                target.is_alive = False
                self.log.append(f"{target.name} was defeated")

        if not any(e.is_alive for e in self.enemy_party):
            self.finished = True
            self.outcome = "win"
            return

        # Enemy side
        for enemy in self.enemy_party:
            if not enemy.is_alive:
                continue
            target = next((m for m in self.player_party if m.is_alive), None)
            if not target:
                break
            dmg = max(1, enemy.attack - target.defense)
            target.hp -= dmg
            self.log.append(f"{enemy.name} attacks {target.name} for {dmg}")
            if target.hp <= 0:
                target.is_alive = False
                self.log.append(f"{target.name} fell")

        if not any(p.is_alive for p in self.player_party):
            self.finished = True
            self.outcome = "lose"
            return

        self.turn += 1



def run_simple_battle(player_party: list, enemy_party: list):
    """Auto resolve a battle using the stateful ``Battle`` class."""
    battle = Battle(player_party, enemy_party)
    # Always attack the first available enemy
    while not battle.finished:
        targets = []
        for _ in player_party:
            # choose first alive enemy index
            for j, enemy in enumerate(battle.enemy_party):
                if enemy.is_alive:
                    targets.append(j)
                    break
            else:
                targets.append(-1)
        battle.next_turn(targets)
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
    msgs.extend(battle_log)
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
    active_players[user_id] = player
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
    active_players[u_id] = player
    return redirect(url_for('play', user_id=u_id))

@app.route('/play/<int:user_id>')
def play(user_id):
    player = active_players.get(user_id)
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
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template("status.html", player=player, user_id=user_id)

@app.route('/party/<int:user_id>')
def party(user_id):
    """Show the player's party."""
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template("party.html", player=player, user_id=user_id)


@app.route('/monster_book/<int:user_id>')
def monster_book(user_id):
    """Show the player's monster encyclopedia."""
    player = active_players.get(user_id)
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
    player = active_players.get(user_id)
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
    return render_template('formation.html', player=player, user_id=user_id)


@app.route('/items/<int:user_id>', methods=['GET', 'POST'])
def items(user_id):
    player = active_players.get(user_id)
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
    return render_template('items.html', player=player, user_id=user_id, message=message)


@app.route('/shop/<int:user_id>', methods=['GET', 'POST'])
def shop(user_id):
    player = active_players.get(user_id)
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
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_inn', False):
        return redirect(url_for('play', user_id=user_id))
    cost = getattr(loc, 'inn_cost', 10)
    success = player.rest_at_inn(cost)
    msg = '宿屋で休んだ。' if success else 'お金が足りない。'
    return render_template('result.html', message=msg, user_id=user_id)


@app.route('/explore/<int:user_id>', methods=['POST'])
def explore(user_id):
    player = active_players.get(user_id)
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
    if loc.possible_enemies and random.random() < loc.encounter_rate:
        messages.extend(handle_battle(player, loc))
    else:
        messages.append('モンスターは現れなかった。')
    return render_template('explore.html', messages=messages, user_id=user_id)


@app.route('/battle/<int:user_id>', methods=['GET', 'POST'])
def battle(user_id):
    """Interactive battle view. State is kept on the server."""
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))

    battle_obj = active_battles.get(user_id)

    if request.method == 'GET':
        if not battle_obj:
            loc = LOCATIONS.get(player.current_location_id)
            if not loc:
                return redirect(url_for('play', user_id=user_id))
            enemies = generate_enemy_party(loc, player)
            if not enemies:
                msg = 'モンスターは現れなかった。'
                return render_template('result.html', message=msg, user_id=user_id)
            battle_obj = Battle(player.party_monsters, enemies)
            enemy_names = ", ".join(e.name for e in enemies)
            battle_obj.log.append(f"{enemy_names} が現れた！")
            active_battles[user_id] = battle_obj
        return render_template(
            'battle_turn.html',
            user_id=user_id,
            battle=battle_obj,
            player_party=battle_obj.player_party,
            enemy_party=battle_obj.enemy_party,
            log=battle_obj.log,
        )

    # POST -> perform next turn
    if not battle_obj:
        return redirect(url_for('battle', user_id=user_id))

    targets: list[int] = []
    for i in range(len(battle_obj.player_party)):
        val = request.form.get(f'target_{i}', '-1')
        try:
            targets.append(int(val))
        except ValueError:
            targets.append(-1)

    battle_obj.next_turn(targets)

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
            msgs.append(f"勝利した！ {gold_gain}G を得た。")
        else:
            msgs.append("敗北してしまった...")
        player.last_battle_log = msgs
        del active_battles[user_id]
        return render_template('battle.html', messages=msgs, user_id=user_id)

    return render_template(
        'battle_turn.html',
        user_id=user_id,
        battle=battle_obj,
        player_party=battle_obj.player_party,
        enemy_party=battle_obj.enemy_party,
        log=battle_obj.log,
    )


@app.route('/map/<int:user_id>')
def world_map(user_id):
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    overview = get_map_overview()
    return render_template('map.html', overview=overview, progress=player.exploration_progress, locations=LOCATIONS, user_id=user_id)


@app.route('/battle_log/<int:user_id>')
def battle_log(user_id):
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    log = getattr(player, 'last_battle_log', [])
    return render_template('battle_log.html', log=log, user_id=user_id)

@app.route('/move/<int:user_id>', methods=['POST'])
def move(user_id):
    """Move the player to another location."""
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    dest = request.form.get('dest')
    if dest in LOCATIONS:
        player.current_location_id = dest
    return redirect(url_for('play', user_id=user_id))

@app.route('/save/<int:user_id>', methods=['POST'])
def save(user_id):
    """Persist the current player state to the database."""
    player = active_players.get(user_id)
    if player:
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('play', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
