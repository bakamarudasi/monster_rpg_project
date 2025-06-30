"""Web entry point for the Monster RPG game."""

from .web import create_app
from .web.battle import active_battles
from .battle import Battle

app = create_app()

__all__ = ["app", "active_battles", "Battle"]
