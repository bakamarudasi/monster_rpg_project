"""Web entry point for the Monster RPG game."""

import random

from .web import create_app
from .web.battle import Battle, active_battles

app = create_app()

__all__ = ["app", "Battle", "active_battles", "random"]
