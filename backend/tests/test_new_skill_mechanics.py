"""新スキルメカニクスのテスト。

採用した4カテゴリ分の新規エフェクト/システムを検証する:
  1. 連撃 / 割合ダメージ / 状態異常シナジー / 背水 / 状態異常転移
  2. ATB操作（ディレイ・ヘイスト）
  3. 属性相性の拡張 / 属性変化 / フィールド（天候）
  4. バリア（シールド） / 変身 / みがわり
"""

import random
import unittest
from unittest import mock

from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import ALL_SKILLS, Skill
from monster_rpg.skills.skill_actions import apply_effects, deal_damage, calculate_skill_damage
from monster_rpg.battle import (
    apply_skill_effect,
    process_status_effects,
    enemy_take_action,
    _enemy_skill_targets,
)
from monster_rpg import elements


# ---------------------------------------------------------------------------
# 3. 属性相性表の拡張
# ---------------------------------------------------------------------------
class ElementalChartTests(unittest.TestCase):
    def test_existing_triangle_preserved(self):
        self.assertEqual(elements.elemental_multiplier("火", "風"), 1.5)
        self.assertEqual(elements.elemental_multiplier("風", "火"), 0.5)

    def test_new_relationships(self):
        # 雷 → 水 → 火 → 氷 → 雷 のサイクル
        self.assertEqual(elements.elemental_multiplier("雷", "水"), 1.5)
        self.assertEqual(elements.elemental_multiplier("水", "雷"), 0.5)
        self.assertEqual(elements.elemental_multiplier("火", "氷"), 1.5)
        self.assertEqual(elements.elemental_multiplier("氷", "火"), 0.5)

    def test_light_dark_mutual(self):
        # 光と闇は相互に弱点（両方向 1.5）
        self.assertEqual(elements.elemental_multiplier("光", "闇"), 1.5)
        self.assertEqual(elements.elemental_multiplier("闇", "光"), 1.5)

    def test_neutral_elements(self):
        self.assertEqual(elements.elemental_multiplier("無", "火"), 1.0)
        self.assertEqual(elements.elemental_multiplier("火", "無"), 1.0)
        self.assertEqual(elements.elemental_multiplier(None, "火"), 1.0)


# ---------------------------------------------------------------------------
# 1. 軽量エフェクト群
# ---------------------------------------------------------------------------
class MultiHitTests(unittest.TestCase):
    def test_multi_hit_lands_between_min_and_max(self):
        caster = Monster("Ninja", hp=40, attack=20, defense=5)
        target = Monster("Dummy", hp=500, attack=5, defense=0)
        skill = ALL_SKILLS["rapid_slash"]
        log = []
        apply_effects(caster, target, skill.effects, skill, log)
        hit_msgs = [e for e in log if "took" in e["message"] and "damage" in e["message"]]
        self.assertGreaterEqual(len(hit_msgs), 2)
        self.assertLessEqual(len(hit_msgs), 4)
        self.assertLess(target.hp, target.max_hp)
        self.assertTrue(any("連撃" in e["message"] for e in log))

    def test_multi_hit_stops_when_target_dies(self):
        caster = Monster("Ninja", hp=40, attack=100, defense=5)
        target = Monster("Glass", hp=5, attack=5, defense=0)
        skill = ALL_SKILLS["rapid_slash"]
        apply_effects(caster, target, skill.effects, skill, [])
        self.assertFalse(target.is_alive)


class PercentDamageTests(unittest.TestCase):
    def test_ignores_defense_and_scales_with_max_hp(self):
        caster = Monster("Mage", hp=30, attack=5, defense=5)
        target = Monster("Tank", hp=200, attack=5, defense=999)
        skill = ALL_SKILLS["gravity"]
        apply_effects(caster, target, skill.effects, skill, [])
        # 25% of 200 = 50, regardless of the huge defense
        self.assertEqual(target.hp, 150)


class StatusSynergyTests(unittest.TestCase):
    def test_bonus_if_status_increases_damage(self):
        caster = Monster("Hero", hp=30, attack=30, defense=5)
        skill = ALL_SKILLS["exploit_weakness"]

        healthy = Monster("A", hp=300, attack=5, defense=5)
        poisoned = Monster("B", hp=300, attack=5, defense=5)
        poisoned.apply_status("poison", [], 3)

        apply_effects(caster, healthy, skill.effects, skill, [])
        apply_effects(caster, poisoned, skill.effects, skill, [])

        dmg_healthy = healthy.max_hp - healthy.hp
        dmg_poisoned = poisoned.max_hp - poisoned.hp
        self.assertGreater(dmg_poisoned, dmg_healthy)


class DesperationTests(unittest.TestCase):
    def test_lower_hp_deals_more(self):
        skill = ALL_SKILLS["desperate_strike"]

        full = Monster("Full", hp=100, attack=30, defense=5)
        low = Monster("Low", hp=100, attack=30, defense=5)
        low.hp = 10  # 90% missing

        t1 = Monster("T1", hp=300, attack=5, defense=5)
        t2 = Monster("T2", hp=300, attack=5, defense=5)

        apply_effects(full, t1, skill.effects, skill, [])
        apply_effects(low, t2, skill.effects, skill, [])

        self.assertGreater(t1.max_hp - t1.hp, 0)
        self.assertGreater(t2.max_hp - t2.hp, t1.max_hp - t1.hp)


class TransferStatusTests(unittest.TestCase):
    def test_moves_debuff_to_target(self):
        caster = Monster("Hero", hp=40, attack=10, defense=5)
        target = Monster("Enemy", hp=40, attack=10, defense=5)
        caster.apply_status("poison", [], 3)
        self.assertTrue(any(e["name"] == "poison" for e in caster.status_effects))

        skill = ALL_SKILLS["affliction_swap"]
        apply_effects(caster, target, skill.effects, skill, [])

        self.assertFalse(any(e["name"] == "poison" for e in caster.status_effects))
        self.assertTrue(any(e["name"] == "poison" for e in target.status_effects))


# ---------------------------------------------------------------------------
# 2. ATB操作
# ---------------------------------------------------------------------------
class ATBChangeTests(unittest.TestCase):
    def test_delay_pushes_gauge_back(self):
        caster = Monster("Hero", hp=30, attack=10, defense=5)
        enemy = Monster("Enemy", hp=30, attack=10, defense=5)
        enemy.atb_gauge = 80
        apply_effects(caster, enemy, ALL_SKILLS["time_delay"].effects, ALL_SKILLS["time_delay"], [])
        self.assertEqual(enemy.atb_gauge, 30)

    def test_delay_clamped_at_zero(self):
        caster = Monster("Hero", hp=30, attack=10, defense=5)
        enemy = Monster("Enemy", hp=30, attack=10, defense=5)
        enemy.atb_gauge = 20
        apply_effects(caster, enemy, ALL_SKILLS["time_delay"].effects, ALL_SKILLS["time_delay"], [])
        self.assertEqual(enemy.atb_gauge, 0)

    def test_haste_fills_gauge(self):
        caster = Monster("Hero", hp=30, attack=10, defense=5)
        ally = Monster("Ally", hp=30, attack=10, defense=5)
        ally.atb_gauge = 10
        apply_effects(caster, ally, ALL_SKILLS["haste"].effects, ALL_SKILLS["haste"], [])
        self.assertEqual(ally.atb_gauge, 90)


# ---------------------------------------------------------------------------
# 3. 属性変化 / フィールド
# ---------------------------------------------------------------------------
class ChangeElementTests(unittest.TestCase):
    def test_element_changes_then_reverts(self):
        caster = Monster("Hero", hp=30, attack=10, defense=5, element="火")
        target = Monster("Enemy", hp=30, attack=10, defense=5, element="土")
        skill = ALL_SKILLS["frost_brand"]
        apply_effects(caster, target, skill.effects, skill, [])
        self.assertEqual(target.element, "氷")
        self.assertTrue(any(e["name"] == "element_shift" for e in target.status_effects))

        # duration=3 のので、3回ターン処理すると元に戻る
        for _ in range(3):
            process_status_effects(target)
        self.assertEqual(target.element, "土")
        self.assertFalse(any(e["name"] == "element_shift" for e in target.status_effects))


class FieldTests(unittest.TestCase):
    def tearDown(self):
        elements.clear_field()

    def test_field_amplifies_matching_element(self):
        caster = Monster("Pyro", hp=30, attack=20, defense=5, element="火")
        target = Monster("Dummy", hp=300, attack=5, defense=5, element="無")
        skill = Skill("Burn", power=10, skill_type="attack", effects=[{"type": "damage"}], category="物理")

        base = calculate_skill_damage(caster, target, skill)
        elements.set_field("火", 1.5, 5, "業火の地")
        boosted = calculate_skill_damage(caster, target, skill)
        self.assertEqual(boosted, int(base * 1.5))

    def test_field_does_not_affect_other_element(self):
        caster = Monster("Hydro", hp=30, attack=20, defense=5, element="水")
        target = Monster("Dummy", hp=300, attack=5, defense=5, element="無")
        skill = Skill("Splash", power=10, skill_type="attack", effects=[{"type": "damage"}], category="物理")

        base = calculate_skill_damage(caster, target, skill)
        elements.set_field("火", 1.5, 5, "業火の地")
        self.assertEqual(calculate_skill_damage(caster, target, skill), base)

    def test_field_expires_via_tick(self):
        elements.set_field("火", 1.5, 2, "業火の地")
        self.assertIsNotNone(elements.get_field())
        self.assertIsNone(elements.tick_field())   # 2 -> 1
        self.assertEqual(elements.tick_field(), "業火の地")  # 1 -> 0 (expired)
        self.assertIsNone(elements.get_field())


# ---------------------------------------------------------------------------
# 4. バリア / 変身 / みがわり
# ---------------------------------------------------------------------------
class ShieldTests(unittest.TestCase):
    def test_shield_absorbs_then_breaks(self):
        target = Monster("Guard", hp=100, attack=5, defense=0)
        target.shield = 40

        deal_damage(target, 30, [])
        self.assertEqual(target.shield, 10)
        self.assertEqual(target.hp, 100)  # 完全吸収

        deal_damage(target, 30, [])
        self.assertEqual(target.shield, 0)
        self.assertEqual(target.hp, 80)  # 10 吸収 + 20 がHPへ

    def test_barrier_skill_grants_shield(self):
        caster = Monster("Cleric", hp=40, attack=10, defense=5)
        ally = Monster("Ally", hp=60, attack=10, defense=5)
        skill = ALL_SKILLS["barrier"]
        apply_effects(caster, ally, skill.effects, skill, [])
        self.assertEqual(ally.shield, 40)

    def test_decoy_applies_shield_and_taunt(self):
        hero = Monster("Decoy", hp=100, attack=10, defense=5)
        skill = ALL_SKILLS["decoy"]
        apply_effects(hero, hero, skill.effects, skill, [])
        self.assertEqual(hero.shield, int(hero.max_hp * 0.2))
        self.assertTrue(any(e["name"] == "taunt" for e in hero.status_effects))

    def test_shield_survives_dict_round_trip(self):
        m = Monster("Guard", hp=100, attack=10, defense=5)
        m.shield = 25
        restored = Monster.from_dict(m.to_dict())
        self.assertEqual(restored.shield, 25)


class TransformTests(unittest.TestCase):
    def test_copies_stats_then_reverts(self):
        caster = Monster("Mimic", hp=40, attack=5, defense=5, speed=5, element="無")
        target = Monster("Boss", hp=200, attack=50, defense=40, speed=30, element="闇")
        skill = ALL_SKILLS["mimicry"]

        apply_effects(caster, target, skill.effects, skill, [])
        self.assertEqual(caster.attack, 50)
        self.assertEqual(caster.defense, 40)
        self.assertEqual(caster.speed, 30)
        self.assertEqual(caster.element, "闇")

        # duration=3 のので、3回処理で変身解除
        for _ in range(3):
            process_status_effects(caster)
        self.assertEqual(caster.attack, 5)
        self.assertEqual(caster.defense, 5)
        self.assertEqual(caster.element, "無")


# ---------------------------------------------------------------------------
# 敵AIが新スキルを賢く使う/狙う
# ---------------------------------------------------------------------------
class EnemyAITargetingTests(unittest.TestCase):
    """アーキタイプ別ターゲティング（純粋関数なので決定的）。"""

    def setUp(self):
        self.actor = Monster("Foe", hp=80, attack=20, defense=10, element="火")
        self.allies = [self.actor]
        self.weak = Monster("Weak", hp=40, attack=30, defense=5)
        self.weak.hp = 20
        self.tanky = Monster("Tanky", hp=300, attack=8, defense=5)
        self.players = [self.weak, self.tanky]

    def test_self_target_routes_to_self(self):
        # かつて self 対象スキルがランダムな味方へ飛ぶバグがあった箇所
        for sid in ("decoy", "inferno_field"):
            tgt = _enemy_skill_targets(self.actor, ALL_SKILLS[sid], self.players, self.allies)
            self.assertEqual(tgt, [self.actor])

    def test_percent_and_multihit_hit_high_hp(self):
        for sid in ("gravity", "rapid_slash"):
            tgt = _enemy_skill_targets(self.actor, ALL_SKILLS[sid], self.players, self.allies)
            self.assertEqual(tgt, [self.tanky])

    def test_transform_copies_strongest(self):
        tgt = _enemy_skill_targets(self.actor, ALL_SKILLS["mimicry"], self.players, self.allies)
        self.assertEqual(tgt, [self.weak])  # weak が最高attack(30)

    def test_delay_hits_highest_atb(self):
        self.weak.atb_gauge = 90
        self.tanky.atb_gauge = 10
        tgt = _enemy_skill_targets(self.actor, ALL_SKILLS["time_delay"], self.players, self.allies)
        self.assertEqual(tgt, [self.weak])

    def test_exploit_prefers_statused_target(self):
        self.tanky.apply_status("poison", [], 3)
        tgt = _enemy_skill_targets(self.actor, ALL_SKILLS["exploit_weakness"], self.players, self.allies)
        self.assertEqual(tgt, [self.tanky])


class EnemyAIBehaviorTests(unittest.TestCase):
    def tearDown(self):
        elements.clear_field()

    def test_fire_enemy_sets_matching_field(self):
        enemy = Monster("Wyrm", hp=120, attack=20, defense=10, element="火",
                        skills=[ALL_SKILLS["inferno_field"], ALL_SKILLS["fireball"]])
        enemy.mp = 999
        hero = Monster("Hero", hp=200, attack=10, defense=10, speed=5)
        elements.clear_field()
        with mock.patch("random.random", return_value=0.0):  # フィールド設営ゲートを通す
            enemy_take_action(enemy, [hero], [enemy], [])
        field = elements.get_field()
        self.assertIsNotNone(field)
        self.assertEqual(field["element"], "火")

    def test_enemy_reactively_heals_critical_ally(self):
        healer = Monster("Support", hp=60, attack=10, defense=5,
                         skills=[ALL_SKILLS["heal"]])
        healer.mp = 999
        ally = Monster("Ally", hp=100, attack=10, defense=5)
        ally.hp = 25  # 25% < 40% → 危機
        hero = Monster("Hero", hp=80, attack=10, defense=5)
        # 確率ゲートに関係なく回復する（random=1.0でも発動）
        with mock.patch("random.random", return_value=1.0):
            enemy_take_action(healer, [hero], [healer, ally], [])
        self.assertGreater(ally.hp, 25)


if __name__ == "__main__":
    unittest.main()
