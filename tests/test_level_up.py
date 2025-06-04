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
        self.assertIn("素早さが", output)
        self.assertGreater(monster.speed, start_speed)

if __name__ == '__main__':
    unittest.main()
