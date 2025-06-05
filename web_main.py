"""Simple web interface for the Monster RPG game."""

try:
    from flask import Flask, request, redirect, url_for, render_template
except ImportError as e:  # pragma: no cover - dependency check
    raise SystemExit(
        "Flask is required to run this web interface. "
        "Install dependencies with 'pip install -r requirements.txt'."
    ) from e
import random
from dataclasses import dataclass, field

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


@dataclass
class Battle:
    """Simple in-memory battle state for the web UI."""
    player: Player
    enemies: list
    log: list[str] = field(default_factory=list)
    turn: int = 1
    finished: bool = False
    outcome: str | None = None

    @property
    def player_party(self) -> list:
        return [m for m in self.player.party_monsters if m.is_alive]


# Active battles per user
active_battles: dict[int, Battle] = {}



def run_simple_battle(player_party: list, enemy_party: list):
    """Very simplified auto battle returning outcome and log messages."""
    log = []
    while any(m.is_alive for m in player_party) and any(e.is_alive for e in enemy_party):
        for p in player_party:
            if not p.is_alive:
                continue
            target = next((e for e in enemy_party if e.is_alive), None)
            if not target:
                break
            dmg = max(1, p.attack - target.defense)
            target.hp -= dmg
            log.append(f"{p.name} attacks {target.name} for {dmg}")
            if target.hp <= 0:
                target.is_alive = False
                log.append(f"{target.name} was defeated")
        for e in enemy_party:
            if not e.is_alive:
                continue
            target = next((m for m in player_party if m.is_alive), None)
            if not target:
                break
            dmg = max(1, e.attack - target.defense)
            target.hp -= dmg
            log.append(f"{e.name} attacks {target.name} for {dmg}")
            if target.hp <= 0:
                target.is_alive = False
                log.append(f"{target.name} fell")
    outcome = "win" if any(m.is_alive for m in player_party) else "lose"
    return outcome, log


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
        entries.append((entry, status))
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
    """Interactive battle page with simple command selection."""
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
                msgs = ['モンスターは現れなかった。']
                return render_template(
                    'battle.html',
                    player_party=player.party_monsters,
                    enemy_party=[],
                    messages=msgs,
                    finished=True,
                    user_id=user_id,
                )
            battle_obj = Battle(player=player, enemies=enemies)
            first_names = ', '.join(e.name for e in enemies)
            battle_obj.log.append(f"{first_names} が現れた！")
            active_battles[user_id] = battle_obj
        return render_template(
            'battle.html',
            player_party=battle_obj.player_party,
            enemy_party=battle_obj.enemies,
            messages=battle_obj.log,
            finished=battle_obj.finished,
            user_id=user_id,
        )

    # POST: player action
    if not battle_obj:
        return redirect(url_for('battle', user_id=user_id))

    action = request.form.get('action')
    actor = next((m for m in battle_obj.player_party if m.is_alive), None)
    target = next((e for e in battle_obj.enemies if e.is_alive), None)

    if not battle_obj.finished and actor and target:
        if action == 'attack':
            dmg = max(1, actor.attack - target.defense)
            target.hp -= dmg
            battle_obj.log.append(f"{actor.name} の攻撃！ {target.name} に {dmg} ダメージ")
            if target.hp <= 0:
                target.is_alive = False
                battle_obj.log.append(f"{target.name} を倒した！")
        elif action == 'run':
            if random.random() < 0.5:
                battle_obj.log.append('うまく逃げ切れた。')
                battle_obj.finished = True
                battle_obj.outcome = 'fled'
            else:
                battle_obj.log.append('しかし逃げられなかった。')
        else:
            battle_obj.log.append('その行動はまだ使えない。')

        # Enemy actions if battle still ongoing
        if not battle_obj.finished:
            alive_enemies = [e for e in battle_obj.enemies if e.is_alive]
            alive_players = [m for m in battle_obj.player_party if m.is_alive]
            if not alive_enemies:
                battle_obj.finished = True
                battle_obj.outcome = 'win'
            elif not alive_players:
                battle_obj.finished = True
                battle_obj.outcome = 'lose'
            else:
                for ene in alive_enemies:
                    ptarget = next((m for m in battle_obj.player_party if m.is_alive), None)
                    if not ptarget:
                        break
                    dmg = max(1, ene.attack - ptarget.defense)
                    ptarget.hp -= dmg
                    battle_obj.log.append(f"{ene.name} の攻撃！ {ptarget.name} に {dmg} ダメージ")
                    if ptarget.hp <= 0:
                        ptarget.is_alive = False
                        battle_obj.log.append(f"{ptarget.name} は倒れた！")

                alive_enemies = [e for e in battle_obj.enemies if e.is_alive]
                alive_players = [m for m in battle_obj.player_party if m.is_alive]
                if not alive_enemies:
                    battle_obj.finished = True
                    battle_obj.outcome = 'win'
                elif not alive_players:
                    battle_obj.finished = True
                    battle_obj.outcome = 'lose'

    if battle_obj.finished:
        if battle_obj.outcome == 'win':
            total_exp = sum(e.level * 10 for e in battle_obj.enemies)
            gold_gain = sum(e.level * 5 for e in battle_obj.enemies)
            alive_members = [m for m in player.party_monsters if m.is_alive]
            if alive_members and total_exp:
                share = total_exp // len(alive_members)
                for m in alive_members:
                    m.gain_exp(share)
            player.gold += gold_gain
            battle_obj.log.append(f"勝利した！ {gold_gain}G を得た。")
        elif battle_obj.outcome == 'lose':
            battle_obj.log.append('敗北してしまった...')
        active_battles.pop(user_id, None)
        player.last_battle_log = list(battle_obj.log)

    return render_template(
        'battle.html',
        player_party=battle_obj.player_party,
        enemy_party=battle_obj.enemies,
        messages=battle_obj.log,
        finished=battle_obj.finished,
        user_id=user_id,
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
