"""Simple web interface for the Monster RPG game."""

from flask import Flask, request, redirect, url_for, render_template

import database_setup
from player import Player
from monsters.monster_data import ALL_MONSTERS
from map_data import LOCATIONS

app = Flask(__name__)

database_setup.initialize_database()

# In-memory store of active players keyed by user_id
active_players: dict[int, Player] = {}

@app.route('/')
def index():
    """Show the landing page for starting or loading a game."""
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start_game():
    """Create a new player and start the game."""
    name = request.form.get('username', 'Hero')
    user_id = database_setup.create_user(name, 'pw')
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
