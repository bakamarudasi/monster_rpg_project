from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from ..items.item_data import ALL_ITEMS
from ..monsters.monster_data import ALL_MONSTERS, MONSTER_BOOK_DATA
from ..map_data import LOCATIONS
from .utils import load_player, save_player
from ..services.synthesis_service import perform_synthesis, preview_synthesis
from ..services import equipment_service, shop_service
from ..enhancement import ENHANCE_MAX

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/enhance/<int:user_id>', methods=['GET', 'POST'], endpoint='enhance')
def enhance(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        success, msg = equipment_service.enhance(player, request.form.get('instance_id', ''))
        save_player(player, user_id)
        flash(msg, 'success' if success else 'warn')
        return redirect(url_for('inventory.enhance', user_id=user_id))

    return render_template(
        'enhance.html', player=player, user_id=user_id,
        entries=equipment_service.enhance_entries(player), enhance_max=ENHANCE_MAX,
    )

@inventory_bp.route('/disassemble/<int:user_id>', methods=['POST'], endpoint='disassemble')
def disassemble(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    success, msg = equipment_service.disassemble(player, request.form.get('instance_id', ''))
    save_player(player, user_id)
    flash(msg, 'success' if success else 'warn')
    return redirect(url_for('inventory.enhance', user_id=user_id))

@inventory_bp.route('/limit_break/<int:user_id>', methods=['POST'], endpoint='limit_break')
def limit_break(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    success, msg = equipment_service.limit_break(player, request.form.get('instance_id', ''))
    save_player(player, user_id)
    flash(msg, 'success' if success else 'warn')
    return redirect(url_for('inventory.enhance', user_id=user_id))

@inventory_bp.route('/items/<int:user_id>', methods=['GET', 'POST'], endpoint='items')
def items(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
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
        save_player(player, user_id)
    return render_template('items.html', player=player, user_id=user_id, message=message)

@inventory_bp.route('/synthesize/<int:user_id>', methods=['GET', 'POST'], endpoint='synthesize')
def synthesize(user_id):
    """Display the synthesis page and handle legacy POST requests."""
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    message = None
    if request.method == 'POST':
        if request.is_json:
            outcome = perform_synthesis(player, request.get_json(silent=True) or {})
            if outcome.success:
                save_player(player, user_id)
            return jsonify(outcome.to_dict())
        # 旧来のフォーム送信（モンスター同士の配合のみ）
        outcome = perform_synthesis(player, {
            'base_type': 'monster', 'base_id': request.form.get('mon1', -1),
            'material_type': 'monster', 'material_id': request.form.get('mon2', -1),
        })
        if outcome.success:
            save_player(player, user_id)
        message = outcome.message
    return render_template('synthesize.html', player=player, user_id=user_id, message=message)

@inventory_bp.route('/synthesize_action/<int:user_id>', methods=['POST'], endpoint='synthesize_action')
def synthesize_action(user_id):
    """Handle monster synthesis via JSON payload."""
    player = load_player(user_id)
    if not player:
        return jsonify({'success': False, 'error': 'player not found'}), 404
    if not request.is_json:
        return jsonify({'success': False, 'error': 'json required'}), 400
    outcome = perform_synthesis(player, request.get_json(silent=True) or {})
    if outcome.is_validation_error:
        return jsonify({'success': False, 'error': outcome.message}), 400
    if outcome.success:
        save_player(player, user_id)
    return jsonify(outcome.to_dict())

@inventory_bp.route('/synthesize_preview/<int:user_id>', methods=['POST'], endpoint='synthesize_preview')
def synthesize_preview(user_id):
    """モンスター同士の配合結果を確定せず予測して返す。"""
    player = load_player(user_id)
    if not player:
        return jsonify({'ok': False, 'message': 'player not found'}), 404
    if not request.is_json:
        return jsonify({'ok': False, 'message': 'json required'}), 400
    preview, err = preview_synthesis(player, request.get_json(silent=True) or {})
    if err:
        return jsonify({'ok': False, 'message': err}), 400
    return jsonify(preview)

@inventory_bp.route('/shop/<int:user_id>', methods=['GET', 'POST'], endpoint='shop')
def shop(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_shop', False):
        return redirect(url_for('main.play', user_id=user_id))
    message = None
    if request.method == 'POST':
        if 'buy_item' in request.form:
            _, message = shop_service.buy_item(player, loc, request.form['buy_item'])
        elif 'buy_monster' in request.form:
            _, message = shop_service.buy_monster(player, loc, request.form['buy_monster'])
        save_player(player, user_id)
    entries = []
    for iid, pr in loc.shop_items.items():
        item = ALL_ITEMS.get(iid)
        name = item.name if item else iid
        desc = item.description if item else ""
        entries.append(("item", iid, name, pr, desc))
    for mid, pr in loc.shop_monsters.items():
        mon = ALL_MONSTERS.get(mid)
        mname = mon.name if mon else mid
        desc = MONSTER_BOOK_DATA.get(mid).description if mid in MONSTER_BOOK_DATA else ""
        entries.append(("monster", mid, mname, pr, desc))

    item_map = {iid: it.name for iid, it in ALL_ITEMS.items()}
    monster_map = {mid: mon.name for mid, mon in ALL_MONSTERS.items()}
    player_items = [{"idx": i, "name": it.name} for i, it in enumerate(player.items)]
    reserve_mons = [{"idx": i, "name": m.name} for i, m in enumerate(player.reserve_monsters)]

    buy_base = url_for("market.buy_route", user_id=user_id, listing_id=0)
    buy_base = buy_base.rsplit("/", 1)[0] + "/"

    market_data = {
        "listings_url": url_for("market.listings"),
        "list_item_url": url_for("market.list_item_route", user_id=user_id),
        "list_monster_url": url_for("market.list_monster_route", user_id=user_id),
        "buy_url": buy_base,
        "item_map": item_map,
        "monster_map": monster_map,
        "player_items": player_items,
        "reserve_monsters": reserve_mons,
    }

    return render_template(
        "shop.html",
        player=player,
        user_id=user_id,
        entries=entries,
        message=message,
        market_data=market_data,
    )

@inventory_bp.route('/inn/<int:user_id>', methods=['POST'], endpoint='inn')
def inn(user_id):
    player = load_player(user_id)
    if not player:
        return redirect(url_for('auth.index'))
    loc = LOCATIONS.get(player.current_location_id)
    if not loc or not getattr(loc, 'has_inn', False):
        return redirect(url_for('main.play', user_id=user_id))
    _, msg = shop_service.rest_at_inn(player, loc)
    save_player(player, user_id)
    return render_template('result.html', message=msg, user_id=user_id)
