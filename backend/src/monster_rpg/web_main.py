"""Web entry point for the Monster RPG game."""

from .web import create_app
from .web.battle import Battle, active_battles

app = create_app()

__all__ = ["app", "Battle", "active_battles"]
