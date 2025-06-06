"""Compatibility wrapper for the deprecated CLI version."""
from old_cli import main as _old_main

start_battle = _old_main.start_battle
handle_battle_loss = _old_main.handle_battle_loss
random = _old_main.random

_old_main.start_battle = start_battle
_old_main.handle_battle_loss = handle_battle_loss
_old_main.random = random

def game_loop(hero):
    _old_main.start_battle = start_battle
    _old_main.handle_battle_loss = handle_battle_loss
    _old_main.random = random
    return _old_main.game_loop(hero)
