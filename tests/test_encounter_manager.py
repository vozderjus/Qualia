import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from constants import TILE_SIZE, Tiles
from world.encounter_manager import EncounterManager
from world.level import Level


class DummyEnemy:
    def __init__(self, game, level, player, position):
        self.game = game
        self.level = level
        self.player = player
        self.position = position
        self.room_id = None


class EncounterManagerTests(unittest.TestCase):
    def make_world(self):
        floor = Tiles.FLOOR.value
        level = Level(
            [
                [floor, floor, floor, floor, floor, floor],
                [floor, floor, floor, floor, floor, floor],
                [floor, floor, floor, floor, floor, floor],
                [floor, floor, floor, floor, floor, floor],
            ]
        )
        player = SimpleNamespace(rect=pygame.Rect(TILE_SIZE // 2, TILE_SIZE // 2, 20, 20))
        world = SimpleNamespace(
            level=level,
            rooms=[(0, 0, 2, 4), (3, 0, 3, 4)],
            player=player,
            alive_enemy_counts_by_room={},
            cleared_room_ids=set(),
            pending_lock_room_id=None,
            pending_room_doors=[],
            locked_room_id=None,
            active_room_doors=[],
            pending_enemy_spawns_by_room={},
            pending_enemy_spawn_count=0,
            pending_boss_spawn=None,
            boss=None,
            enemies=[],
            shop_room_id=None,
            game=SimpleNamespace(),
        )
        return world

    def test_get_room_id_for_point_uses_prepared_tile_lookup(self):
        world = self.make_world()
        manager = EncounterManager(world)

        manager.prepare_floor_layout()

        self.assertEqual(manager.get_room_id_for_point((TILE_SIZE, TILE_SIZE)), 0)
        self.assertIsNone(manager.get_room_id_for_point((TILE_SIZE * 2 + 1, TILE_SIZE)))
        self.assertEqual(manager.get_room_id_for_point((TILE_SIZE * 4, TILE_SIZE)), 1)

    def test_spawn_room_enemies_reads_only_room_bucket_and_tracks_counts(self):
        world = self.make_world()
        manager = EncounterManager(world)
        manager.prepare_floor_layout()
        world.pending_enemy_spawns_by_room = {
            1: [
                SimpleNamespace(room_id=1, position=(120, 60), enemy_class=DummyEnemy),
                SimpleNamespace(room_id=1, position=(160, 60), enemy_class=DummyEnemy),
            ]
        }
        world.pending_enemy_spawn_count = 2

        spawned_any = manager.spawn_room_enemies(1)

        self.assertTrue(spawned_any)
        self.assertEqual(len(world.enemies), 2)
        self.assertEqual(world.pending_enemy_spawn_count, 0)
        self.assertEqual(world.alive_enemy_counts_by_room, {1: 2})
        self.assertNotIn(1, world.pending_enemy_spawns_by_room)


if __name__ == "__main__":
    unittest.main()
