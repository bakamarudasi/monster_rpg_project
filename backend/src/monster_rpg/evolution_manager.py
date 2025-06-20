"""Utilities for monster evolution handling."""

from __future__ import annotations

from .monsters.monster_class import Monster


def try_evolution(monster: Monster, verbose: bool = True) -> None:
    """Trigger the monster's internal evolution check."""
    monster._try_evolution(verbose=verbose)
