import os
from flask import Flask
from .. import database_setup
from ..map_data import load_locations


def create_app():
    base_dir = os.path.dirname(__file__)
    templates = os.path.join(base_dir, '..', 'templates')
    static = os.path.join(base_dir, '..', 'static')
    app = Flask(__name__, template_folder=templates, static_folder=static)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    database_setup.initialize_database()
    load_locations()

    from .auth import auth_bp
    from .main import main_bp
    from .party import party_bp
    from .inventory import inventory_bp
    from .explore import explore_bp
    from .battle import battle_bp
    from .market import market_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(party_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(explore_bp)
    app.register_blueprint(battle_bp)
    app.register_blueprint(market_bp)

    # Backwards compatible endpoint aliases
    alias_map = {
        'play': 'main.play',
        'status': 'main.status',
        'monster_book': 'main.monster_book',
        'world_map': 'main.world_map',
        'battle_log': 'main.battle_log',
        'move': 'main.move',
        'save': 'main.save',
        'party': 'party.party',
        'equip': 'party.equip',
        'formation': 'party.formation',
        'party_manage': 'party.manage',
        'items': 'inventory.items',
        'synthesize': 'inventory.synthesize',
        'synthesize_action': 'inventory.synthesize_action',
        'shop': 'inventory.shop',
        'inn': 'inventory.inn',
        'explore': 'explore.explore',
        'battle': 'battle.battle',
    }
    for alias, target in alias_map.items():
        if target in app.view_functions:
            view = app.view_functions[target]
            # Reuse the same URL rule
            for rule in app.url_map.iter_rules(target):
                app.add_url_rule(rule.rule, endpoint=alias, view_func=view, methods=rule.methods)

    return app
