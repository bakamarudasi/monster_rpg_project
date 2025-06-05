from flask import Flask, request, redirect, url_for, render_template_string

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
    return render_template_string(
        '''<h1>Monster RPG Web Test</h1>
<form action="{{ url_for('start_game') }}" method="post">
    <input name="username" placeholder="名前">
    <button type="submit">新規ゲーム</button>
</form>
<form action="{{ url_for('load_existing') }}" method="post">
    <input name="user_id" placeholder="User ID">
    <button type="submit">ロード</button>
</form>''')

@app.route('/start', methods=['POST'])
def start_game():
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
    return render_template_string('''
<h2>{{ loc.name }}</h2>
<p>{{ loc.description }}</p>
<p>Player: {{ player.name }} Lv.{{ player.player_level }} Gold {{ player.gold }}</p>
<h3>移動</h3>
{% for cmd, dest, name in connections %}
<form action="{{ url_for('move', user_id=user_id) }}" method="post">
    <input type="hidden" name="dest" value="{{ dest }}">
    <button type="submit">{{ cmd }} -> {{ name }}</button>
</form>
{% endfor %}
<form action="{{ url_for('status', user_id=user_id) }}" method="get"><button>ステータス</button></form>
<form action="{{ url_for('party', user_id=user_id) }}" method="get"><button>パーティ</button></form>
<form action="{{ url_for('save', user_id=user_id) }}" method="post"><button>セーブ</button></form>
''', player=player, loc=loc, connections=connections, user_id=user_id)

@app.route('/status/<int:user_id>')
def status(user_id):
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template_string('''
<h2>{{ player.name }} のステータス</h2>
<p>Lv {{ player.player_level }} EXP {{ player.exp }} Gold {{ player.gold }}</p>
<a href="{{ url_for('play', user_id=user_id) }}">戻る</a>
''', player=player, user_id=user_id)

@app.route('/party/<int:user_id>')
def party(user_id):
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    return render_template_string('''
<h2>パーティ</h2>
<ul>
{% for m in player.party_monsters %}
<li>{{ m.name }} Lv.{{ m.level }} HP {{ m.hp }}/{{ m.max_hp }}</li>
{% endfor %}
</ul>
<a href="{{ url_for('play', user_id=user_id) }}">戻る</a>
''', player=player, user_id=user_id)

@app.route('/move/<int:user_id>', methods=['POST'])
def move(user_id):
    player = active_players.get(user_id)
    if not player:
        return redirect(url_for('index'))
    dest = request.form.get('dest')
    if dest in LOCATIONS:
        player.current_location_id = dest
    return redirect(url_for('play', user_id=user_id))

@app.route('/save/<int:user_id>', methods=['POST'])
def save(user_id):
    player = active_players.get(user_id)
    if player:
        player.save_game(database_setup.DATABASE_NAME, user_id=user_id)
    return redirect(url_for('play', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
