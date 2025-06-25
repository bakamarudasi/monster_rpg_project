# monsters package initialization

from .monster_class import (
    Monster,
    GROWTH_TYPE_AVERAGE,
    GROWTH_TYPE_EARLY,
    GROWTH_TYPE_LATE,
    GROWTH_TYPE_POWER,
    GROWTH_TYPE_MAGIC,
    GROWTH_TYPE_DEFENSE,
    GROWTH_TYPE_SPEED,
)
from .monster_data import ALL_MONSTERS, load_monsters
from .synthesis_rules import (
    SYNTHESIS_RECIPES,
    SYNTHESIS_ITEMS_REQUIRED,
    MONSTER_ITEM_RECIPES,
    find_family_synthesis_result,
)
from .evolution_rules import EVOLUTION_RULES

