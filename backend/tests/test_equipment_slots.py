"""装備スロット拡張（兜 helmet・靴 boots）のテスト。"""

import unittest

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.items.equipment import ALL_EQUIPMENT
from monster_rpg.skills.skills import ALL_SKILLS


class EquipmentSlotTests(unittest.TestCase):
    def test_has_five_slots(self):
        m = Monster("Hero", hp=40, attack=10, defense=5)
        self.assertEqual(set(m.equipment_slots),
                         {"weapon", "armor", "helmet", "accessory", "boots"})

    def test_equip_helmet_and_boots_apply_stats(self):
        m = Monster("Hero", hp=40, attack=10, defense=5, speed=5)
        base_def, base_spd = m.defense, m.speed
        m.equip(ALL_EQUIPMENT["iron_helm"])    # defense +4
        m.equip(ALL_EQUIPMENT["swift_boots"])  # speed +8
        self.assertEqual(m.defense, base_def + 4)
        self.assertEqual(m.speed, base_spd + 8)
        self.assertIn("helmet", m.equipment)
        self.assertIn("boots", m.equipment)

    def test_full_loadout_five_pieces(self):
        m = Monster("Hero", hp=40, attack=10, defense=5, speed=5)
        for eid in ["bronze_sword", "iron_armor", "iron_helm", "power_ring", "traveler_boots"]:
            m.equip(ALL_EQUIPMENT[eid])
        self.assertEqual(len(m.equipment), 5)

    def test_helmet_and_boots_can_grant_skills(self):
        m = Monster("Hero", hp=40, attack=10, defense=5)
        m.equip(ALL_EQUIPMENT["dragon_helm"])   # grants stone_skin
        m.equip(ALL_EQUIPMENT["windwalkers"])   # grants teleport
        names = [s.name for s in m.total_skills]
        self.assertIn(ALL_SKILLS["stone_skin"].name, names)
        self.assertIn(ALL_SKILLS["teleport"].name, names)


if __name__ == "__main__":
    unittest.main()
