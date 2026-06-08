from flask import Blueprint, render_template, redirect, url_for, request, flash
from .utils import save_player, with_player
from ..raid_data import RAID_BOSSES
from ..services import raid_service
from . import battle as battle_mod

raid_bp = Blueprint('raid', __name__)


@raid_bp.route('/raid/<int:user_id>', methods=['GET'], endpoint='raid')
@with_player
def raid(user_id, player):
    available = raid_service.collect_available(player)
    party_len = len(player.party_monsters)
    mons = [
        {
            'idx': i,
            'name': m.name,
            'level': m.level,
            'element': getattr(m, 'element', None),
            'image': getattr(m, 'image_filename', None),
            'hp': m.max_hp,
            'in_party': i < party_len,
        }
        for i, m in enumerate(available)
    ]
    bosses = []
    for b in RAID_BOSSES:
        entry = {**b, 'cleared': f"raid_cleared:{b['id']}" in player.story_flags}
        reqs = b.get('requires')
        if reqs:
            entry['reqs'] = raid_service.soul_status(player, reqs)
            entry['ready'] = all(r['have'] for r in entry['reqs'])
        bosses.append(entry)
    return render_template(
        'raid.html', user_id=user_id, bosses=bosses, mons=mons,
        max_party=raid_service.MAX_RAID_PARTY, title='レイド',
    )


@raid_bp.route('/raid/<int:user_id>', methods=['POST'], endpoint='raid_start')
@with_player
def raid_start(user_id, player):
    raid_id = request.form.get('raid_id')
    indices = [int(x) for x in request.form.getlist('mons') if x.lstrip('-').isdigit()]
    battle, error = raid_service.start_raid(player, raid_id, indices)
    if error:
        flash(error, 'warn')
        return redirect(url_for('raid.raid', user_id=user_id))

    battle_mod._assign_unit_ids(battle)
    # 素早い側の先制などを処理し、最初のプレイヤー手番まで進める
    battle.run_until_player_turn()
    battle_mod.active_battles[user_id] = battle
    save_player(player, user_id)
    return redirect(url_for('battle.battle', user_id=user_id))
