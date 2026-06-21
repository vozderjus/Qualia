import pygame
from entities.room_door import RoomDoor


class RoomLayoutCache:
    def __init__(self):
        self.level = None
        self.rooms = []
        self.room_rects = []
        self.room_lookup = []
        self.door_specs_by_room_id = {}

    def prepare(self, level, rooms):
        self.level = level
        self.rooms = list(rooms)
        self.room_rects = [
            pygame.Rect(
                room_x * level.tile_size,
                room_y * level.tile_size,
                room_w * level.tile_size,
                room_h * level.tile_size,
            )
            for room_x, room_y, room_w, room_h in self.rooms
        ]

        self.room_lookup = self._build_room_lookup()
        self.door_specs_by_room_id = {
            room_id: self._build_room_door_specs(room_id)
            for room_id in range(len(self.rooms))
        }

    def get_room_id_for_point(self, point):
        if self.level is None or not self.room_lookup:
            return None

        tile_x, tile_y = self.level.world_point_to_tile(*point)
        if tile_y < 0 or tile_y >= len(self.room_lookup):
            return None
        if tile_x < 0 or tile_x >= len(self.room_lookup[tile_y]):
            return None

        return self.room_lookup[tile_y][tile_x]

    def get_room_rect(self, room_id):
        return self.room_rects[room_id]

    def build_room_doors(self, room_id):
        return [
            RoomDoor(rect, orientation)
            for rect, orientation in self.door_specs_by_room_id.get(room_id, [])
        ]

    def _build_room_lookup(self):
        if self.level is None:
            return []

        lookup = [
            [None for _ in range(len(self.level.tiles[0]))]
            for _ in range(len(self.level.tiles))
        ]
        for room_id, (room_x, room_y, room_w, room_h) in enumerate(self.rooms):
            for tile_y in range(room_y, room_y + room_h):
                row = lookup[tile_y]
                for tile_x in range(room_x, room_x + room_w):
                    row[tile_x] = room_id

        return lookup

    def _is_floor_tile(self, tile_x, tile_y):
        if tile_y < 0 or tile_y >= len(self.level.tiles):
            return False
        if tile_x < 0 or tile_x >= len(self.level.tiles[0]):
            return False

        return self.level.tiles[tile_y][tile_x] == self.level.FLOOR.value

    def _group_contiguous_positions(self, positions):
        if not positions:
            return []

        sorted_positions = sorted(positions)
        groups = []
        group_start = sorted_positions[0]
        previous = sorted_positions[0]

        for position in sorted_positions[1:]:
            if position == previous + 1:
                previous = position
                continue

            groups.append((group_start, previous))
            group_start = position
            previous = position

        groups.append((group_start, previous))
        return groups

    def _build_room_door_specs(self, room_id):
        room_x, room_y, room_w, room_h = self.rooms[room_id]
        tile_size = self.level.tile_size
        door_specs = []

        top_openings = [
            tile_x
            for tile_x in range(room_x, room_x + room_w)
            if self._is_floor_tile(tile_x, room_y)
            and self._is_floor_tile(tile_x, room_y - 1)
        ]
        for start_x, end_x in self._group_contiguous_positions(top_openings):
            door_specs.append(
                (
                    pygame.Rect(
                        start_x * tile_size,
                        room_y * tile_size - tile_size // 2,
                        (end_x - start_x + 1) * tile_size,
                        tile_size,
                    ),
                    "top",
                )
            )

        bottom_openings = [
            tile_x
            for tile_x in range(room_x, room_x + room_w)
            if self._is_floor_tile(tile_x, room_y + room_h - 1)
            and self._is_floor_tile(tile_x, room_y + room_h)
        ]
        for start_x, end_x in self._group_contiguous_positions(bottom_openings):
            door_specs.append(
                (
                    pygame.Rect(
                        start_x * tile_size,
                        (room_y + room_h) * tile_size - tile_size // 2,
                        (end_x - start_x + 1) * tile_size,
                        tile_size,
                    ),
                    "bottom",
                )
            )

        left_openings = [
            tile_y
            for tile_y in range(room_y, room_y + room_h)
            if self._is_floor_tile(room_x, tile_y)
            and self._is_floor_tile(room_x - 1, tile_y)
        ]
        for start_y, end_y in self._group_contiguous_positions(left_openings):
            door_specs.append(
                (
                    pygame.Rect(
                        room_x * tile_size - tile_size // 2,
                        start_y * tile_size,
                        tile_size,
                        (end_y - start_y + 1) * tile_size,
                    ),
                    "left",
                )
            )

        right_openings = [
            tile_y
            for tile_y in range(room_y, room_y + room_h)
            if self._is_floor_tile(room_x + room_w - 1, tile_y)
            and self._is_floor_tile(room_x + room_w, tile_y)
        ]
        for start_y, end_y in self._group_contiguous_positions(right_openings):
            door_specs.append(
                (
                    pygame.Rect(
                        (room_x + room_w) * tile_size - tile_size // 2,
                        start_y * tile_size,
                        tile_size,
                        (end_y - start_y + 1) * tile_size,
                    ),
                    "right",
                )
            )

        return door_specs
