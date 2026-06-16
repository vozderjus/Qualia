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
    def __init__(self, map_width, map_height, max_depth=4, enemy_count=1, has_shop=False):
        self.map_width = map_width
        self.map_height = map_height
        self.max_depth = max_depth
        self.enemy_count = enemy_count
        self.has_shop = has_shop

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

        farthest_room_id, farthest_room = max(
            enumerate(rooms[1:], start=1),
            key=lambda item: (
                (item[1][0] + item[1][2] // 2 - start_center_x) ** 2
                + (item[1][1] + item[1][3] // 2 - start_center_y) ** 2
            ),
        )

        return farthest_room_id, self.room_to_world_center(farthest_room)

    def choose_shop(self, rooms, exit_room_id=None):
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
        return shop_room_id, self.room_to_world_center(shop_room)

    def choose_enemy_spawns(self, rooms, exit_room_id=None, shop_room_id=None):
        if len(rooms) <= 1:
            return []

        available_rooms = [
            (room_id, room)
            for room_id, room in enumerate(rooms[1:], start=1)
            if room_id != exit_room_id and room_id != shop_room_id
        ]

        if not available_rooms:
            available_rooms = [
                (room_id, room)
                for room_id, room in enumerate(rooms[1:], start=1)
                if room_id != shop_room_id
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
        exit_room_id, exit_spawn = self.choose_exit(rooms)
        shop_room_id = None
        shop_spawn = None
        if self.has_shop:
            shop_room_id, shop_spawn = self.choose_shop(rooms, exit_room_id)
        enemy_spawns = self.choose_enemy_spawns(rooms, exit_room_id, shop_room_id)

        return GeneratedLevel(
            tiles=grid,
            rooms=rooms,
            player_spawn=player_spawn,
            enemy_spawns=enemy_spawns,
            exit_spawn=exit_spawn,
            exit_room_id=exit_room_id,
            shop_spawn=shop_spawn,
            shop_room_id=shop_room_id,
        )
