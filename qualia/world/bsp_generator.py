from collections import deque
import random
from dataclasses import dataclass

from constants import MIN_AREA_SIZE, MIN_CORRIDOR_WIDTH, MIN_ROOM_SIZE, TILE_SIZE, Tiles


@dataclass
class EnemySpawn:
    room_id: int
    position: tuple[int, int]


@dataclass
class GeneratedLevel:
    tiles: list[list[int]]
    rooms: list[tuple[int, int, int, int]]
    player_spawn: tuple[int, int]
    enemy_spawns: list[EnemySpawn]
    exit_spawn: tuple[int, int] | None
    exit_room_id: int | None
    boss_spawn: tuple[int, int] | None
    boss_room_id: int | None
    shop_spawn: tuple[int, int] | None
    shop_room_id: int | None


class BSPNode():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = None
        self.right = None
        self.room = None

    def is_leaf(self):
        return self.left is None and self.right is None
    
    def split(self):
        if not self.is_leaf():
            return False

        if self.width > self.height:
            split_vertical = True
        elif self.width < self.height:
            split_vertical = False
        else:
            split_vertical = random.choice([True, False])

        if split_vertical:
            max_split_pos = self.width - MIN_AREA_SIZE
        else:
            max_split_pos = self.height - MIN_AREA_SIZE

        if max_split_pos <= MIN_AREA_SIZE:
            return False

        split_pos = random.randrange(MIN_AREA_SIZE, max_split_pos + 1)

        if split_vertical:
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(
                self.x + split_pos,
                self.y,
                self.width - split_pos,
                self.height,
            )
        else:
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(
                self.x,
                self.y + split_pos,
                self.width,
                self.height - split_pos,
            )

        return True

    def create_rooms(self, grid, floor_value=Tiles.FLOOR.value, min_room=MIN_ROOM_SIZE, padding=1):
        if not self.is_leaf():
            if self.left:
                self.left.create_rooms(grid, floor_value, min_room, padding)
            if self.right:
                self.right.create_rooms(grid, floor_value, min_room, padding)
            return

        max_w = self.width - padding * 2
        max_h = self.height - padding * 2
        if max_w < min_room or max_h < min_room:
            return

        # Комнаты делаем ближе к размеру leaf-области, чтобы они не были
        # мелкими островками внутри большого прямоугольника.
        min_w = max(min_room, int(max_w * 0.72))
        min_h = max(min_room, int(max_h * 0.72))

        rw = random.randint(min_w, max_w)
        rh = random.randint(min_h, max_h)
        rx = self.x + random.randint(padding, self.width - rw - padding)
        ry = self.y + random.randint(padding, self.height - rh - padding)

        self.room = (rx, ry, rw, rh)
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                grid[y][x] = floor_value

    def get_room(self):
        if self.room is not None:
            return self.room

        left_room = self.left.get_room() if self.left else None
        right_room = self.right.get_room() if self.right else None

        if left_room and right_room:
            return random.choice([left_room, right_room])

        return left_room or right_room

    def get_room_center(self):
        room = self.get_room()
        if room:
            rx, ry, rw, rh = room
            return (rx + rw // 2, ry + rh // 2)
        return None

    def collect_rooms(self):
        rooms = []

        if self.room is not None:
            rooms.append(self.room)

        if self.left:
            rooms.extend(self.left.collect_rooms())
        if self.right:
            rooms.extend(self.right.collect_rooms())

        return rooms

    def connect_children(self, grid, floor_value):
        if self.left:
            self.left.connect_children(grid, floor_value)
        if self.right:
            self.right.connect_children(grid, floor_value)

        if not self.left or not self.right:
            return

        left_center = self.left.get_room_center()
        right_center = self.right.get_room_center()

        if left_center is None or right_center is None:
            return

        self.carve_corridor(grid, left_center, right_center, floor_value)
    
    def carve_corridor(self, grid, start, end, floor_value):
        x1, y1 = start
        x2, y2 = end

        if random.choice([True, False]):
            self.carve_h_corridor(grid, x1, x2, y1, floor_value)
            self.carve_v_corridor(grid, y1, y2, x2, floor_value)
        else:
            self.carve_v_corridor(grid, y1, y2, x1, floor_value)
            self.carve_h_corridor(grid, x1, x2, y2, floor_value)

    def carve_h_corridor(self, grid, x1, x2, y, floor_value):
        half = MIN_CORRIDOR_WIDTH // 2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for dy in range(-half, half + 1):
                cy = y + dy
                if 0 <= cy < len(grid) and 0 <= x < len(grid[0]):
                    grid[cy][x] = floor_value

    def carve_v_corridor(self, grid, y1, y2, x, floor_value):
        half = MIN_CORRIDOR_WIDTH // 2
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for dx in range(-half, half + 1):
                cx = x + dx
                if 0 <= y < len(grid) and 0 <= cx < len(grid[0]):
                    grid[y][cx] = floor_value


class BSPGenerator:
    def __init__(
        self,
        map_width,
        map_height,
        max_depth=4,
        enemy_count=1,
        has_shop=False,
        is_boss_floor=False,
        boss_min_room_width=0,
        boss_min_room_height=0,
        boss_min_room_area=0,
    ):
        self.map_width = map_width
        self.map_height = map_height
        self.max_depth = max_depth
        self.enemy_count = enemy_count
        self.has_shop = has_shop
        self.is_boss_floor = is_boss_floor
        self.boss_min_room_width = boss_min_room_width
        self.boss_min_room_height = boss_min_room_height
        self.boss_min_room_area = boss_min_room_area

    def split_tree(self, node, depth):
        if depth <= 0:
            return

        if node.split():
            self.split_tree(node.left, depth - 1)
            self.split_tree(node.right, depth - 1)

    def room_to_world_center(self, room):
        rx, ry, rw, rh = room
        center_x = rx + rw // 2
        center_y = ry + rh // 2
        return (
            center_x * TILE_SIZE + TILE_SIZE // 2,
            center_y * TILE_SIZE + TILE_SIZE // 2,
        )

    def room_to_tile_center(self, room):
        rx, ry, rw, rh = room
        return (rx + rw // 2, ry + rh // 2)

    def tile_to_world_center(self, tile_x, tile_y):
        return (
            tile_x * TILE_SIZE + TILE_SIZE // 2,
            tile_y * TILE_SIZE + TILE_SIZE // 2,
        )

    def world_to_tile(self, world_position):
        world_x, world_y = world_position
        return (world_x // TILE_SIZE, world_y // TILE_SIZE)

    def is_walkable_tile(self, grid, tile_x, tile_y):
        if tile_y < 0 or tile_y >= len(grid):
            return False
        if tile_x < 0 or tile_x >= len(grid[0]):
            return False

        return grid[tile_y][tile_x] == Tiles.FLOOR.value

    def collect_reachable_tiles(self, grid, start_tile):
        if not self.is_walkable_tile(grid, *start_tile):
            return set()

        reachable_tiles = {start_tile}
        queue = deque([start_tile])

        while queue:
            tile_x, tile_y = queue.popleft()
            for next_tile in (
                (tile_x + 1, tile_y),
                (tile_x - 1, tile_y),
                (tile_x, tile_y + 1),
                (tile_x, tile_y - 1),
            ):
                if next_tile in reachable_tiles:
                    continue
                if not self.is_walkable_tile(grid, *next_tile):
                    continue

                reachable_tiles.add(next_tile)
                queue.append(next_tile)

        return reachable_tiles

    def validate_reachability(
        self,
        grid,
        rooms,
        player_spawn,
        exit_spawn=None,
        boss_spawn=None,
        shop_spawn=None,
    ):
        if not rooms:
            return False

        reachable_tiles = self.collect_reachable_tiles(
            grid,
            self.world_to_tile(player_spawn),
        )
        if not reachable_tiles:
            return False

        required_tiles = [
            self.room_to_tile_center(room)
            for room in rooms
        ]
        for world_position in (exit_spawn, boss_spawn, shop_spawn):
            if world_position is not None:
                required_tiles.append(self.world_to_tile(world_position))

        return all(tile in reachable_tiles for tile in required_tiles)

    def choose_player_spawn(self, rooms):
        if not rooms:
            return (
                self.map_width * TILE_SIZE // 2,
                self.map_height * TILE_SIZE // 2,
            )

        return self.room_to_world_center(rooms[0])

    def choose_exit(self, rooms):
        if not rooms:
            return None, None

        if len(rooms) == 1:
            return 0, self.room_to_world_center(rooms[0])

        start_room = rooms[0]
        start_center_x = start_room[0] + start_room[2] // 2
        start_center_y = start_room[1] + start_room[3] // 2

        room_distances = [
            (
                room_id,
                room,
                (room[0] + room[2] // 2 - start_center_x) ** 2
                + (room[1] + room[3] // 2 - start_center_y) ** 2,
            )
            for room_id, room in enumerate(rooms[1:], start=1)
        ]
        max_distance = max(distance for _, _, distance in room_distances)
        min_candidate_distance = max_distance * 0.65
        candidate_rooms = [
            room_data
            for room_data in room_distances
            if room_data[2] >= min_candidate_distance
        ]

        chosen_room_id, chosen_room, _ = random.choices(
            candidate_rooms,
            weights=[max(1, distance) for _, _, distance in candidate_rooms],
            k=1,
        )[0]
        return chosen_room_id, self.room_to_world_center(chosen_room)

    def is_valid_boss_room(self, room):
        _, _, room_width, room_height = room
        room_area = room_width * room_height
        return (
            room_width >= self.boss_min_room_width
            and room_height >= self.boss_min_room_height
            and room_area >= self.boss_min_room_area
        )

    def choose_boss_room(self, rooms):
        if len(rooms) <= 1:
            return None, None

        start_room = rooms[0]
        start_center_x = start_room[0] + start_room[2] // 2
        start_center_y = start_room[1] + start_room[3] // 2
        room_score = lambda room: (
            room[1][2] * room[1][3],
            (room[1][0] + room[1][2] // 2 - start_center_x) ** 2
            + (room[1][1] + room[1][3] // 2 - start_center_y) ** 2,
        )

        candidate_rooms = [
            (room_id, room)
            for room_id, room in enumerate(rooms[1:], start=1)
            if self.is_valid_boss_room(room)
        ]

        if not candidate_rooms:
            return None, None

        boss_room_id, boss_room = max(candidate_rooms, key=room_score)
        return boss_room_id, self.room_to_world_center(boss_room)

    def choose_largest_room(self, rooms):
        if len(rooms) <= 1:
            return None, None

        start_room = rooms[0]
        start_center_x = start_room[0] + start_room[2] // 2
        start_center_y = start_room[1] + start_room[3] // 2

        largest_room_id, largest_room = max(
            enumerate(rooms[1:], start=1),
            key=lambda item: (
                item[1][2] * item[1][3],
                (item[1][0] + item[1][2] // 2 - start_center_x) ** 2
                + (item[1][1] + item[1][3] // 2 - start_center_y) ** 2,
            ),
        )
        return largest_room_id, self.room_to_world_center(largest_room)

    def choose_shop(self, rooms, exit_room_id=None):
        if not rooms:
            return None, None

        if self.is_boss_floor:
            return 0, self.get_shop_position_in_room(rooms[0])

        if len(rooms) <= 1:
            return None, None

        candidate_rooms = [
            (room_id, room)
            for room_id, room in enumerate(rooms)
            if room_id not in (0, exit_room_id)
        ]

        if not candidate_rooms:
            candidate_rooms = [
                (room_id, room)
                for room_id, room in enumerate(rooms)
                if room_id != exit_room_id
            ]

        if not candidate_rooms:
            candidate_rooms = list(enumerate(rooms))

        shop_room_id, shop_room = max(
            candidate_rooms,
            key=lambda item: item[1][2] * item[1][3],
        )
        return shop_room_id, self.get_shop_position_in_room(shop_room)

    def get_shop_position_in_room(self, room):
        rx, ry, rw, rh = room
        shop_tile_x = max(rx + 1, rx + rw - 2)
        shop_tile_y = max(ry + 1, ry + rh - 2)
        return self.tile_to_world_center(shop_tile_x, shop_tile_y)

    def choose_enemy_spawns(
        self,
        rooms,
        exit_room_id=None,
        shop_room_id=None,
        boss_room_id=None,
    ):
        if self.enemy_count <= 0:
            return []

        if len(rooms) <= 1:
            return []

        available_rooms = [
            (room_id, room)
            for room_id, room in enumerate(rooms[1:], start=1)
            if room_id != exit_room_id
            and room_id != shop_room_id
            and room_id != boss_room_id
        ]

        if not available_rooms:
            available_rooms = [
                (room_id, room)
                for room_id, room in enumerate(rooms[1:], start=1)
                if room_id != shop_room_id and room_id != boss_room_id
            ]

        if not available_rooms:
            available_rooms = list(enumerate(rooms[1:], start=1))

        selected_rooms = available_rooms
        enemy_count = max(self.enemy_count, len(selected_rooms) * 2)

        enemy_spawns = []
        for enemy_index in range(enemy_count):
            room_id, room = selected_rooms[enemy_index % len(selected_rooms)]
            room_slot_index = enemy_index // len(selected_rooms)
            enemy_spawns.append(
                EnemySpawn(
                    room_id=room_id,
                    position=self.get_enemy_position_in_room(room, room_slot_index),
                )
            )

        random.shuffle(enemy_spawns)
        return enemy_spawns

    def get_enemy_position_in_room(self, room, slot_index):
        center_x, center_y = self.room_to_world_center(room)
        rx, ry, rw, rh = room

        min_x = rx * TILE_SIZE + TILE_SIZE
        max_x = (rx + rw) * TILE_SIZE - TILE_SIZE
        min_y = ry * TILE_SIZE + TILE_SIZE
        max_y = (ry + rh) * TILE_SIZE - TILE_SIZE

        offset_step = TILE_SIZE * 2
        spawn_offsets = (
            (0, 0),
            (-offset_step, 0),
            (offset_step, 0),
            (0, -offset_step),
            (0, offset_step),
            (-offset_step, -offset_step),
            (offset_step, -offset_step),
            (-offset_step, offset_step),
            (offset_step, offset_step),
        )

        offset_x, offset_y = spawn_offsets[slot_index % len(spawn_offsets)]
        spawn_x = max(min_x, min(center_x + offset_x, max_x))
        spawn_y = max(min_y, min(center_y + offset_y, max_y))

        return (spawn_x, spawn_y)

    def generate(self):
        attempts = 24 if self.is_boss_floor else 12

        for attempt_index in range(attempts):
            grid = [
                [Tiles.WALL.value for _ in range(self.map_width)]
                for _ in range(self.map_height)
            ]

            root = BSPNode(0, 0, self.map_width, self.map_height)

            self.split_tree(root, self.max_depth)
            root.create_rooms(grid)
            root.connect_children(grid, Tiles.FLOOR.value)
            rooms = root.collect_rooms()
            player_spawn = self.choose_player_spawn(rooms)
            exit_room_id = None
            exit_spawn = None
            boss_room_id = None
            boss_spawn = None

            if self.is_boss_floor:
                boss_room_id, boss_spawn = self.choose_boss_room(rooms)
                if boss_room_id is None and attempt_index < attempts - 1:
                    continue
                if boss_room_id is None:
                    boss_room_id, boss_spawn = self.choose_largest_room(rooms)
            else:
                exit_room_id, exit_spawn = self.choose_exit(rooms)

            shop_room_id = None
            shop_spawn = None
            if self.has_shop:
                reserved_room_id = exit_room_id
                if reserved_room_id is None:
                    reserved_room_id = boss_room_id
                shop_room_id, shop_spawn = self.choose_shop(rooms, reserved_room_id)

            if not self.validate_reachability(
                grid,
                rooms,
                player_spawn,
                exit_spawn=exit_spawn,
                boss_spawn=boss_spawn,
                shop_spawn=shop_spawn,
            ):
                continue

            enemy_spawns = self.choose_enemy_spawns(
                rooms,
                exit_room_id,
                shop_room_id,
                boss_room_id,
            )

            return GeneratedLevel(
                tiles=grid,
                rooms=rooms,
                player_spawn=player_spawn,
                enemy_spawns=enemy_spawns,
                exit_spawn=exit_spawn,
                exit_room_id=exit_room_id,
                boss_spawn=boss_spawn,
                boss_room_id=boss_room_id,
                shop_spawn=shop_spawn,
                shop_room_id=shop_room_id,
            )

        raise RuntimeError("BSP generator could not build a fully connected level")
