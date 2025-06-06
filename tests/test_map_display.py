import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map_data import get_map_overview, LOCATIONS, load_locations

class MapDisplayTests(unittest.TestCase):
    def test_overview_contains_start(self):
        load_locations()
        overview = get_map_overview()
        start = LOCATIONS["village_square"]
        self.assertIn(start.name, overview)
        coord_text = f"({start.x},{start.y})"
        self.assertIn(coord_text, overview)

if __name__ == '__main__':
    unittest.main()
