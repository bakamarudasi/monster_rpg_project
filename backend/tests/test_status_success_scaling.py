"""状態異常の成功率が術者の魔力／相手の魔法防御に依存することのテスト。"""

import unittest
from unittest.mock import patch

from monster_rpg.battle import apply_skill_effect
from monster_rpg.monsters.monster_class import Monster
from monster_rpg.skills.skills import Skill


def _paralyze_skill():
    return Skill('Z', power=0, skill_type='status',
                 effects=[{'type': 'status', 'status': 'paralyze', 'chance': 0.5}])


def _has(mon, name):
    return any(e['name'] == name for e in mon.status_effects)


class StatusSuccessScalingTests(unittest.TestCase):
    def test_high_magic_caster_lands_ailment_more_often(self):
        skill = _paralyze_skill()
        mage = Monster('Mage', hp=20, attack=5, defense=2, magic=100)  # 魔力100
        weak = Monster('Weak', hp=20, attack=5, defense=2)             # 魔力0
        # 同じ乱数(0.7)で、魔力が高い術者だけが状態異常を決める（基礎0.5×1.5=0.75 > 0.7）
        t1 = Monster('A', hp=20, attack=5, defense=0)                  # 魔防0
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.7):
            apply_skill_effect(mage, [t1], skill)
        self.assertTrue(_has(t1, 'paralyze'))

        t2 = Monster('B', hp=20, attack=5, defense=0)
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.7):
            apply_skill_effect(weak, [t2], skill)                      # 0.5 < 0.7 → 失敗
        self.assertFalse(_has(t2, 'paralyze'))

    def test_high_magic_defense_target_resists_better(self):
        skill = _paralyze_skill()
        mage = Monster('Mage', hp=20, attack=5, defense=2, magic=100)
        tough = Monster('Tough', hp=20, attack=5, defense=0)
        tough.magic_defense = 100   # 魔力と拮抗 → ボーナス消滅 → 基礎0.5のまま
        with patch('monster_rpg.skills.skill_actions.random.random', return_value=0.7):
            apply_skill_effect(mage, [tough], skill)
        self.assertFalse(_has(tough, 'paralyze'))


if __name__ == '__main__':
    unittest.main()
