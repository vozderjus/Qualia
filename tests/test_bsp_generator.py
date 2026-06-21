import sys
import unittest
from pathlib import Path
from collections import Counter

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

    def test_sample_enemy_positions_stay_inside_room(self):
        random_generator = BSPGenerator(map_width=20, map_height=20, enemy_count=4)
        room = (4, 5, 8, 7)

        positions = random_generator.sample_enemy_positions_in_room(room, 4)

        self.assertEqual(len(positions), 4)
        min_x, max_x, min_y, max_y = random_generator.room_spawn_tile_bounds(room)
        valid_tiles = {
            (tile_x, tile_y)
            for tile_y in range(min_y, max_y + 1)
            for tile_x in range(min_x, max_x + 1)
        }

        for position in positions:
            self.assertIn(
                random_generator.world_to_tile(position),
                valid_tiles,
            )

    def test_choose_enemy_spawns_keeps_minimum_two_enemies_per_room(self):
        spawn_generator = BSPGenerator(map_width=30, map_height=30, enemy_count=3)
        rooms = [
            (1, 1, 7, 7),
            (10, 1, 7, 7),
            (1, 10, 7, 7),
        ]

        enemy_spawns = spawn_generator.choose_enemy_spawns(rooms)

        counts_by_room = Counter(enemy_spawn.room_id for enemy_spawn in enemy_spawns)
        self.assertEqual(set(counts_by_room), {1, 2})
        self.assertTrue(all(count >= 2 for count in counts_by_room.values()))


if __name__ == "__main__":
    unittest.main()
