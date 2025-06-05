from flask import Flask, request, jsonify
import database_setup
from player import Player

app = Flask(__name__)

db_name = database_setup.DATABASE_NAME

def get_or_create_user(username: str, password: str) -> int:
    user_id = database_setup.get_user_id(username, password)
    if user_id is None:
        user_id = database_setup.create_user(username, password)
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
    user_id = get_or_create_user(username, password)
    player = Player(username, user_id=user_id, gold=100)
    player.save_game(db_name)
    return jsonify({'user_id': user_id, 'message': 'created'})

@app.route('/load_game/<int:user_id>')
def load_game(user_id):
    player = Player.load_game(db_name, user_id=user_id)
    if not player:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'name': player.name, 'level': player.player_level, 'gold': player.gold})

if __name__ == '__main__':
    app.run(debug=True)
