import os
import sys
import unittest
import io
from contextlib import redirect_stdout

# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from monsters.monster_data import SLIME

class LevelUpSpeedTests(unittest.TestCase):
    def test_speed_increase_and_message(self):
        monster = SLIME.copy()
        start_speed = monster.speed
        buf = io.StringIO()
        with redirect_stdout(buf):
            monster.level_up()
        output = buf.getvalue()
        end_speed = monster.speed
        speed_gain = end_speed - start_speed
        self.assertIn(f"素早さが {speed_gain}", output)
        self.assertGreater(end_speed, start_speed)

if __name__ == '__main__':
    unittest.main()
