"""戦闘ログが日本語で、ダメージ/回復が色分け用の type を持つことのテスト。"""

import unittest
from unittest.mock import patch

from monster_rpg.battle import Battle, calculate_damage
from monster_rpg.player import Player
from monster_rpg.monsters.monster_class import Monster

ENGLISH_WORDS = ['took', 'damage!', 'fainted', 'attacks', "'s action", 'counters', 'Invalid']


class BattleLogJapaneseTests(unittest.TestCase):
    def test_player_attack_log_is_japanese_and_typed(self):
        hero = Monster('勇者', hp=80, attack=30, defense=5, speed=10)
        foe = Monster('魔物', hp=200, attack=5, defense=5, speed=1)
        battle = Battle([hero], [foe], Player('P'))
        battle.current_actor = hero
        with patch('monster_rpg.battle.random.random', return_value=0.99):  # 会心排除
            battle.process_player_action({'type': 'attack', 'target_enemy': 0})

        joined = ' '.join(e['message'] for e in battle.log)
        for w in ENGLISH_WORDS:
            self.assertNotIn(w, joined, f'英語が残っている: {w}')
        dmg = [e for e in battle.log if 'のダメージ' in e['message']]
        self.assertTrue(dmg)
        self.assertEqual(dmg[0]['type'], 'damage')   # 赤色スタイル用

    def test_dodge_log_uses_resist_type(self):
        atk = Monster('A', hp=30, attack=20, defense=1)
        dodger = Monster('B', hp=30, attack=1, defense=1)
        dodger._stat_bonuses['evasion_rate'] = 50
        log = []
        with patch('monster_rpg.battle.random.random', return_value=0.0):  # 必ず回避
            calculate_damage(atk, dodger, log)
        self.assertTrue(any('かわした' in e['message'] and e['type'] == 'resist' for e in log))

    def test_enemy_turn_not_double_announced(self):
        from monster_rpg.battle import enemy_take_action
        foe = Monster('ゴブリン', hp=40, attack=10, defense=2, ai_role='attacker')
        log = []
        enemy_take_action(foe, [Monster('勇者', hp=50, attack=5, defense=5)], [foe], log)
        announces = [e for e in log if 'の行動！' in e['message'] or 'のターン！' in e['message']]
        self.assertEqual(len(announces), 1)   # 「の行動！」のみ（二重宣言なし）


if __name__ == '__main__':
    unittest.main()
