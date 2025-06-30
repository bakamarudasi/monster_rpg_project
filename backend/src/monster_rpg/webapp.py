from flask import Flask, request, jsonify
import os
import sqlite3
from . import database_setup
from .player import Player

app = Flask(__name__)

def get_or_create_user(username: str, password: str):
    """Return user id or an error tuple if the username already exists."""
    user_id = database_setup.get_user_id(username, password)
    if user_id is None:
        try:
            user_id = database_setup.create_user(username, password)
        except sqlite3.IntegrityError:
            return jsonify({'error': 'username already exists'}), 409
    return user_id

@app.route('/')
def index():
    return 'Monster RPG Web'

@app.route('/new_game', methods=['POST'])
def new_game():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password', 'pw')
    if not username:
        return jsonify({'error': 'username required'}), 400
    result = get_or_create_user(username, password)
    if isinstance(result, tuple):
        # Username conflict
        return result
    user_id = result
    player = Player(username, user_id=user_id, gold=100)
    player.save_game(database_setup.DATABASE_NAME)
    return jsonify({'user_id': user_id, 'message': 'created'})

@app.route('/load_game/<int:user_id>')
def load_game(user_id):
    player = Player.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'name': player.name, 'level': player.player_level, 'gold': player.gold})

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
