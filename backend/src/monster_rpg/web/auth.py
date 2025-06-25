from flask import Blueprint, request, redirect, url_for, render_template, session
import sqlite3
from .. import database_setup
from ..player import Player
from ..monsters.monster_data import ALL_MONSTERS
from .. import save_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Show the landing page for starting or loading a game."""
    return render_template('index.html')

@auth_bp.route('/start', methods=['POST'])
def start_game():
    """Create a new player and start the game."""
    name = request.form.get('username', 'Hero')
    password = request.form.get('password', 'pw')
    try:
        user_id = database_setup.create_user(name, password)
    except sqlite3.IntegrityError:
        msg = '既に同じ名前の人が存在しています'
        return render_template('result.html', message=msg, user_id=None)
    player = Player(name=name, user_id=user_id, gold=100)
    for mid in ('slime', 'goblin', 'wolf'):
        if mid in ALL_MONSTERS:
            player.add_monster_to_party(mid)
    save_manager.save_game(player, database_setup.DATABASE_NAME, user_id=user_id)
    session['user_id'] = user_id
    return redirect(url_for('main.play', user_id=user_id))

@auth_bp.route('/load', methods=['POST'])
def load_existing():
    """Load an existing player by user id."""
    user_id = request.form.get('user_id')
    try:
        u_id = int(user_id)
    except (ValueError, TypeError):
        return 'invalid user id', 400
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=u_id)
    if not player:
        return 'save not found', 404
    session['user_id'] = u_id
    return redirect(url_for('main.play', user_id=u_id))

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate an existing user by username/password."""
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template(
            'result.html',
            message='ユーザー名またはパスワードが不正です',
            user_id=None,
        )
    user_id = database_setup.get_user_id(username, password)
    if not user_id:
        return render_template(
            'result.html',
            message='ユーザー名またはパスワードが違います',
            user_id=None,
        )
    player = save_manager.load_game(database_setup.DATABASE_NAME, user_id=user_id)
    if not player:
        return render_template(
            'result.html',
            message='セーブデータが見つかりません',
            user_id=None,
        )
    session['user_id'] = user_id
    return redirect(url_for('main.play', user_id=user_id))
