from ..player import Player
from ..items.equipment import Equipment


def process_synthesis_payload(player: Player, data: dict):
    """Common logic for synthesis routes using the unified JSON format."""
    base_type = data.get("base_type")
    base_id = data.get("base_id")
    material_type = data.get("material_type")
    material_id = data.get("material_id")

    if base_type == "monster":
        try:
            base_idx = int(base_id)
        except (TypeError, ValueError):
            return False, "invalid base index", None
    else:
        if not isinstance(base_id, str):
            return False, "invalid base id", None

    if material_type == "monster":
        try:
            mat_idx = int(material_id)
        except (TypeError, ValueError):
            return False, "invalid material index", None
    else:
        if not isinstance(material_id, str):
            return False, "invalid material id", None

    if base_type == "monster" and material_type == "monster":
        return player.synthesize_monster(base_idx, mat_idx)
    if base_type == "monster" and material_type == "item":
        return player.synthesize_monster_with_item(base_idx, material_id)
    if base_type == "item" and material_type == "monster":
        return player.synthesize_monster_with_item(mat_idx, base_id)
    if base_type == "item" and material_type == "item":
        return player.synthesize_items(base_id, material_id)
    return False, "invalid types", None
