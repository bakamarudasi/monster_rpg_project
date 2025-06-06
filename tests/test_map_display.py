import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map_data import get_map_overview, LOCATIONS

class MapDisplayTests(unittest.TestCase):
    def test_overview_contains_start(self):
        overview = get_map_overview()
        loc = LOCATIONS["village_square"]
        self.assertIn(loc.name, overview)
        self.assertIn(f"({loc.x},{loc.y})", overview)

if __name__ == '__main__':
    unittest.main()
