import unittest

from monster_rpg.map_data import get_map_overview, get_map_grid, LOCATIONS, load_locations

class MapDisplayTests(unittest.TestCase):
    def test_overview_contains_start(self):
        load_locations()
        overview = get_map_overview()
        start = LOCATIONS["village_square"]
        self.assertIn(start.name, overview)
        coord_text = f"({start.x},{start.y})"
        self.assertIn(coord_text, overview)

    def test_grid_includes_start(self):
        load_locations()
        grid = get_map_grid()
        ids = [cell.location_id for row in grid for cell in row if cell]
        self.assertIn("village_square", ids)

if __name__ == '__main__':
    unittest.main()
