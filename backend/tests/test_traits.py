"""固有特性（trait）の効果テスト。"""

import unittest
from unittest.mock import patch

from monster_rpg import battle
from monster_rpg.battle import calculate_damage, enemy_take_action, Battle, apply_skill_effect
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill
from monster_rpg.skills.skill_actions import calculate_skill_damage


def paralyze_skill(chance=0.5):
    return Skill('P', power=0, skill_type='status',
                 effects=[{'type': 'status', 'status': 'paralyze', 'chance': chance}])


def _has(mon, name):
    return any(e['name'] == name for e in mon.status_effects)


def mk(**kw):
    base = dict(hp=60, attack=10, defense=5)
    base.update(kw)
    return Monster('X', **base)


def magic_skill(power=20):
    return Skill('FB', power=power, category='魔法', skill_type='magic', target='enemy')


class NewStatTraitTests(unittest.TestCase):
    def test_critical_master_boosts_crit_rate(self):
        m = mk()
        before = m.critical_rate
        m.trait_id = 'critical_master'
        self.assertEqual(m.critical_rate - before, 15)

    def test_evasive_boosts_evasion_rate(self):
        m = mk()
        m.trait_id = 'evasive'
        self.assertEqual(m.evasion_rate, 15)

    def test_magic_ward_reduces_magic_damage(self):
        caster = mk(magic=40)
        plain = mk(defense=0)
        plain.magic_defense = 0
        warded = mk(defense=0)
        warded.magic_defense = 0
        warded.trait_id = 'magic_ward'
        self.assertLess(
            calculate_skill_damage(caster, warded, magic_skill()),
            calculate_skill_damage(caster, plain, magic_skill()),
        )

    def test_mana_leech_restores_mp_on_magic_hit(self):
        leecher = mk(magic=40)
        leecher.trait_id = 'mana_leech'
        leecher.max_mp = 50
        leecher.mp = 0
        target = mk(defense=0)
        target.magic_defense = 0
        calculate_skill_damage(leecher, target, magic_skill())
        self.assertGreater(leecher.mp, 0)

    def test_mana_leech_only_for_caster_not_physical(self):
        leecher = mk(attack=40)
        leecher.trait_id = 'mana_leech'
        leecher.max_mp = 50
        leecher.mp = 0
        target = mk(defense=0)
        phys = Skill('Slash', power=10, category='物理', skill_type='attack', target='enemy')
        calculate_skill_damage(leecher, target, phys)
        self.assertEqual(leecher.mp, 0)   # 物理ではMP回復しない


class ReactiveTraitTests(unittest.TestCase):
    def test_endure_survives_lethal_once_then_dies(self):
        hero = mk()
        hero.max_hp, hero.hp = 60, 5
        hero.trait_id = 'endure'
        foe = mk(attack=100)
        foe.ai_role = 'attacker'
        Battle([hero], [foe], Player('P'))   # 戦闘開始で不屈フラグをリセット
        enemy_take_action(foe, [hero], [foe], [])
        self.assertTrue(hero.is_alive)
        self.assertEqual(hero.hp, 1)
        hero.hp = 5
        enemy_take_action(foe, [hero], [foe], [])
        self.assertFalse(hero.is_alive)

    def test_lifesteal_heals_attacker(self):
        vamp = mk(attack=50)
        vamp.trait_id = 'lifesteal'
        vamp.hp = 10
        calculate_damage(vamp, mk(defense=0), [])
        self.assertGreater(vamp.hp, 10)

    def test_pinch_power_scales_with_missing_hp(self):
        full = mk(attack=30)
        full.trait_id = 'pinch_power'
        low = mk(attack=30)
        low.trait_id = 'pinch_power'
        low.hp = max(1, int(low.max_hp * 0.1))
        with patch('monster_rpg.battle.random.random', return_value=0.99):  # 会心を排除
            d_full = calculate_damage(full, mk(defense=0), [])
            d_low = calculate_damage(low, mk(defense=0), [])
        self.assertGreater(d_low, d_full)


class AilmentTraitTests(unittest.TestCase):
    def test_afflictor_raises_infliction_rate(self):
        master, plain = mk(), mk()
        master.trait_id = 'afflictor'
        t1, t2 = mk(defense=0), mk(defense=0)
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.7):
            apply_skill_effect(master, [t1], paralyze_skill())   # 0.5*1.5=0.75 > 0.7 → 成立
            apply_skill_effect(plain, [t2], paralyze_skill())    # 0.5 < 0.7 → 失敗
        self.assertTrue(_has(t1, 'paralyze'))
        self.assertFalse(_has(t2, 'paralyze'))

    def test_iron_will_lowers_infliction_rate(self):
        warded, normal = mk(defense=0), mk(defense=0)
        warded.trait_id = 'iron_will'
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.4):
            apply_skill_effect(mk(), [warded], paralyze_skill())   # 0.5*0.5=0.25 < 0.4 → 防ぐ
            apply_skill_effect(mk(), [normal], paralyze_skill())   # 0.5 > 0.4 → 受ける
        self.assertFalse(_has(warded, 'paralyze'))
        self.assertTrue(_has(normal, 'paralyze'))

    def test_venomous_poisons_on_physical_hit(self):
        attacker = mk(attack=30)
        attacker.trait_id = 'venomous'
        target = mk(defense=0)
        with patch('monster_rpg.battle.random.random', return_value=0.0):
            calculate_damage(attacker, target, [])
        self.assertTrue(_has(target, 'poison'))


class TempoTraitTests(unittest.TestCase):
    def test_haste_speeds_up_atb(self):
        fast, slow = mk(), mk()
        fast.atb_gauge = slow.atb_gauge = 0
        fast.trait_id = 'swift'
        fast.update_atb_gauge(20)
        slow.update_atb_gauge(20)
        self.assertGreater(fast.atb_gauge, slow.atb_gauge)

    def test_conserver_reduces_mp_cost(self):
        sk = Skill('S', power=10, cost=20)
        saver = mk()
        saver.trait_id = 'conserver'
        self.assertLess(saver.skill_mp_cost(sk), mk().skill_mp_cost(sk))

    def test_glass_cannon_deals_and_takes_more(self):
        with patch('monster_rpg.battle.random.random', return_value=0.99):  # 会心排除
            baseline = calculate_damage(mk(attack=20), mk(defense=0), [])
            atk = mk(attack=20)
            atk.trait_id = 'glass_cannon'
            deal = calculate_damage(atk, mk(defense=0), [])
            victim = mk(defense=0)
            victim.trait_id = 'glass_cannon'
            taken = calculate_damage(mk(attack=20), victim, [])
        self.assertGreater(deal, baseline)
        self.assertGreater(taken, baseline)

    def test_fortune_increases_gold(self):
        from monster_rpg.services.battle_service import apply_battle_rewards
        enemy = mk()
        enemy.level = 10
        lucky = mk()
        lucky.trait_id = 'fortune'
        p1 = Player('Rich')
        p1.gold = 0
        apply_battle_rewards(p1, 'win', [lucky], [enemy], [])
        p2 = Player('Poor')
        p2.gold = 0
        apply_battle_rewards(p2, 'win', [mk()], [enemy], [])
        self.assertGreater(p1.gold, p2.gold)


class ExtraActionTraitTests(unittest.TestCase):
    def _battle(self, actor):
        return Battle([actor], [mk(hp=999)], Player('P'))

    def test_refills_atb_on_proc(self):
        mon = mk(speed=20)
        mon.trait_id = 'dual_strike'
        b = self._battle(mon)
        mon.atb_gauge = 0
        with patch('monster_rpg.battle.random.random', return_value=0.0):
            b._maybe_extra_action(mon)
        self.assertEqual(mon.atb_gauge, 100)   # 満タン＝次に即行動

    def test_no_refill_on_fail(self):
        mon = mk(speed=20)
        mon.trait_id = 'dual_strike'
        b = self._battle(mon)
        mon.atb_gauge = 0
        with patch('monster_rpg.battle.random.random', return_value=0.99):
            b._maybe_extra_action(mon)
        self.assertEqual(mon.atb_gauge, 0)

    def test_requires_trait(self):
        mon = mk(speed=20)   # 特性なし
        b = self._battle(mon)
        mon.atb_gauge = 0
        with patch('monster_rpg.battle.random.random', return_value=0.0):
            b._maybe_extra_action(mon)
        self.assertEqual(mon.atb_gauge, 0)

    def test_dual_strike_increases_action_count(self):
        import random as _r
        from monster_rpg import arena

        def acts(trait):
            _r.seed(7)
            ace = Monster('Ace', hp=400, attack=20, defense=5, speed=20)
            if trait:
                ace.trait_id = trait
            dummy = Monster('Dummy', hp=10 ** 7, attack=0, defense=5, speed=20)
            _, log = arena.auto_resolve([ace], [dummy], Player('P'))
            return sum(1 for e in log if e.get('message') == "Ace の行動！")

        self.assertGreater(acts('dual_strike'), acts(None))


if __name__ == '__main__':
    unittest.main()
