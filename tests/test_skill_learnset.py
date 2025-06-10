import io
from contextlib import redirect_stdout
from monster_rpg.monsters.monster_data import SLIME


def test_monster_learns_skill_at_level():
    m = SLIME.copy()
    exp_needed = m.calculate_exp_to_next_level()
    buf = io.StringIO()
    with redirect_stdout(buf):
        m.gain_exp(exp_needed)
    output = buf.getvalue()
    skill_names = [s.name for s in m.skills]
    assert "ガードアップ を覚えた" in output
    assert "ガードアップ" in skill_names
