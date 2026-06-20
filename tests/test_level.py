import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from constants import TILE_SIZE, Tiles
from world.level import Level


class LevelLineOfSightTests(unittest.TestCase):
    def make_level(self, tiles):
        level = Level.__new__(Level)
        level.tile_size = TILE_SIZE
        level.tiles = tiles
        level.dynamic_blockers = []
        return level

    def test_has_line_of_sight_returns_true_for_open_space(self):
        floor = Tiles.FLOOR.value
        level = self.make_level(
            [
                [floor, floor, floor],
                [floor, floor, floor],
                [floor, floor, floor],
            ]
        )

        self.assertTrue(level.has_line_of_sight((16, 16), (80, 16)))

    def test_has_line_of_sight_returns_false_when_wall_blocks_path(self):
        floor = Tiles.FLOOR.value
        wall = Tiles.WALL.value
        level = self.make_level(
            [
                [floor, wall, floor],
                [floor, wall, floor],
                [floor, wall, floor],
            ]
        )

        self.assertFalse(level.has_line_of_sight((16, 16), (80, 16)))

    def test_has_line_of_sight_returns_false_for_out_of_bounds_target(self):
        floor = Tiles.FLOOR.value
        level = self.make_level(
            [
                [floor, floor, floor],
                [floor, floor, floor],
                [floor, floor, floor],
            ]
        )

        self.assertFalse(level.has_line_of_sight((16, 16), (160, 16)))


if __name__ == "__main__":
    unittest.main()
