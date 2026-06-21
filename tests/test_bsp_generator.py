import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from constants import TILE_SIZE, Tiles
from world.bsp_generator import BSPGenerator


class BSPGeneratorValidationTests(unittest.TestCase):
    def setUp(self):
        self.generator = BSPGenerator(map_width=6, map_height=4)
        self.floor = Tiles.FLOOR.value
        self.wall = Tiles.WALL.value

    def test_validate_reachability_returns_true_for_connected_layout(self):
        grid = [
            [self.floor, self.floor, self.floor, self.floor, self.floor, self.floor],
            [self.floor, self.floor, self.floor, self.floor, self.floor, self.floor],
            [self.floor, self.floor, self.floor, self.floor, self.floor, self.floor],
            [self.floor, self.floor, self.floor, self.floor, self.floor, self.floor],
        ]
        rooms = [(0, 0, 2, 4), (3, 0, 3, 4)]
        player_spawn = self.generator.room_to_world_center(rooms[0])
        exit_spawn = self.generator.room_to_world_center(rooms[1])

        self.assertTrue(
            self.generator.validate_reachability(
                grid,
                rooms,
                player_spawn,
                exit_spawn=exit_spawn,
            )
        )

    def test_validate_reachability_returns_false_for_disconnected_layout(self):
        grid = [
            [self.floor, self.floor, self.wall, self.wall, self.floor, self.floor],
            [self.floor, self.floor, self.wall, self.wall, self.floor, self.floor],
            [self.floor, self.floor, self.wall, self.wall, self.floor, self.floor],
            [self.floor, self.floor, self.wall, self.wall, self.floor, self.floor],
        ]
        rooms = [(0, 0, 2, 4), (4, 0, 2, 4)]
        player_spawn = self.generator.room_to_world_center(rooms[0])
        exit_spawn = self.generator.room_to_world_center(rooms[1])

        self.assertFalse(
            self.generator.validate_reachability(
                grid,
                rooms,
                player_spawn,
                exit_spawn=exit_spawn,
            )
        )

    def test_choose_shop_uses_start_room_on_boss_floor(self):
        boss_generator = BSPGenerator(
            map_width=20,
            map_height=20,
            has_shop=True,
            is_boss_floor=True,
        )
        rooms = [
            (1, 1, 10, 10),
            (12, 1, 6, 6),
        ]

        shop_room_id, shop_spawn = boss_generator.choose_shop(rooms)

        self.assertEqual(shop_room_id, 0)
        self.assertNotEqual(
            shop_spawn,
            boss_generator.room_to_world_center(rooms[0]),
        )


if __name__ == "__main__":
    unittest.main()
