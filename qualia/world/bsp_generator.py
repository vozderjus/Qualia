from dataclasses import dataclass

from constants import MIN_CORRIDOR_WIDTH, MIN_ROOM_SIZE, MIN_AREA_SIZE, TILE_SIZE, Tiles
import random


@dataclass
class GeneratedLevel:
    tiles: list[list[int]]
    rooms: list[tuple[int, int, int, int]]
    player_spawn: tuple[int, int]
    enemy_spawns: list[tuple[int, int]]


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

        rw = random.randint(min_room, max_w)
        rh = random.randint(min_room, max_h)
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
    def __init__(self, map_width, map_height, max_depth=4, enemy_count=1):
        self.map_width = map_width
        self.map_height = map_height
        self.max_depth = max_depth
        self.enemy_count = enemy_count

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

    def choose_enemy_spawns(self, rooms):
        if len(rooms) <= 1:
            return []

        available_rooms = rooms[1:]
        random.shuffle(available_rooms)
        selected_rooms = available_rooms[:self.enemy_count]
        return [self.room_to_world_center(room) for room in selected_rooms]

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
        enemy_spawns = self.choose_enemy_spawns(rooms)

        return GeneratedLevel(
            tiles=grid,
            rooms=rooms,
            player_spawn=player_spawn,
            enemy_spawns=enemy_spawns,
        )
