import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from constants import TILE_SIZE
from world.maze_generator import MazeGenerator


class MazeGeneratorTests(unittest.TestCase):
    def test_generate_returns_connected_maze_with_single_pseudo_room(self):
        random.seed(7)
        generator = MazeGenerator(map_width=15, map_height=13, enemy_count=4)

        generated_level = generator.generate()
        start_tile = (
            generated_level.player_spawn[0] // TILE_SIZE,
            generated_level.player_spawn[1] // TILE_SIZE,
        )
        exit_tile = (
            generated_level.exit_spawn[0] // TILE_SIZE,
            generated_level.exit_spawn[1] // TILE_SIZE,
        )
        distances = generator.collect_floor_distances(
            generated_level.tiles,
            start_tile,
        )
        safe_tiles = set(generator.reachable_cell_center_tiles(distances))

        self.assertEqual(generated_level.rooms, [(0, 0, 15, 13)])
        self.assertIn(exit_tile, distances)
        self.assertIn(exit_tile, safe_tiles)
        self.assertEqual(len(generated_level.enemy_spawns), 4)
        self.assertTrue(all(spawn.room_id == 0 for spawn in generated_level.enemy_spawns))
        self.assertTrue(
            all(
                (
                    spawn.position[0] // TILE_SIZE,
                    spawn.position[1] // TILE_SIZE,
                ) in safe_tiles
                for spawn in generated_level.enemy_spawns
            )
        )
        self.assertTrue(generator.validate_wall_spacing(generated_level.tiles))


if __name__ == "__main__":
    unittest.main()
