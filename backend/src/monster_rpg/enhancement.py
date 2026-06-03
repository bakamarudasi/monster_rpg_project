"""装備強化（+N）システム。

死蔵されがちな強化素材（武器の核・防具の欠片・力の破片など）とゴールドを
消費して、装備の能力を恒久的に底上げする。スロット種別ごとに必要素材が異なる。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from .items.item_data import ALL_ITEMS

if TYPE_CHECKING:
    from .player import Player
    from .items.equipment import EquipmentInstance

# 強化の上限
ENHANCE_MAX = 10

# スロットごとの必要素材（候補。先に見つかったものを1個消費する）
ENHANCE_MATERIALS_BY_SLOT = {
    "weapon": ["weapon_core_common", "steel_ingot"],
    "armor": ["armor_fragment_common", "tough_leather"],
    "accessory": ["power_fragment", "magic_stone"],
}


def enhance_cost(level: int) -> int:
    """現在の強化レベルから次のレベルへ上げる際に必要なゴールド。"""
    return 50 * (level + 1)


def _find_equipment(player: "Player", instance_id: str) -> Optional["EquipmentInstance"]:
    for e in player.equipment_inventory:
        if getattr(e, "instance_id", None) == instance_id:
            return e
    return None


def _find_material_index(player: "Player", slot: str) -> Tuple[Optional[int], Optional[str]]:
    """スロットに対応する素材のうち、所持している最初のものの (index, item_id) を返す。"""
    candidates = ENHANCE_MATERIALS_BY_SLOT.get(slot, [])
    for mat_id in candidates:
        idx = next(
            (i for i, it in enumerate(player.items) if getattr(it, "item_id", None) == mat_id),
            None,
        )
        if idx is not None:
            return idx, mat_id
    return None, None


def required_material_names(slot: str) -> str:
    names = []
    for mat_id in ENHANCE_MATERIALS_BY_SLOT.get(slot, []):
        item = ALL_ITEMS.get(mat_id)
        names.append(item.name if item else mat_id)
    return " または ".join(names) if names else "素材"


def enhance_equipment(player: "Player", instance_id: str) -> Tuple[bool, str]:
    """インベントリの装備1点を1段階強化する。"""
    equip = _find_equipment(player, instance_id)
    if equip is None:
        return False, "対象の装備が見つかりません。（装備中の物は外してください）"

    level = getattr(equip, "enhance_level", 0)
    if level >= ENHANCE_MAX:
        return False, f"これ以上は強化できない（最大 +{ENHANCE_MAX}）。"

    slot = equip.slot
    mat_idx, mat_id = _find_material_index(player, slot)
    if mat_idx is None:
        return False, f"強化には {required_material_names(slot)} が必要だ。"

    cost = enhance_cost(level)
    if player.gold < cost:
        return False, f"強化には {cost}G 必要だ（所持 {player.gold}G）。"

    # 消費して強化
    player.gold -= cost
    mat_name = ALL_ITEMS[mat_id].name if mat_id in ALL_ITEMS else mat_id
    player.items.pop(mat_idx)
    equip.enhance_level = level + 1
    return True, f"{mat_name} と {cost}G を使い、{equip.name} の強化に成功した！"
