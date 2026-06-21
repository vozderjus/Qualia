from collections import deque
import random

from constants import MIN_CORRIDOR_WIDTH, TILE_SIZE, Tiles
from world.bsp_generator import EnemySpawn, GeneratedLevel


CARDINAL_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


class MazeGenerator:
    def __init__(
        self,
        map_width,
        map_height,
        enemy_count=1,
        min_passage_width=MIN_CORRIDOR_WIDTH,
        max_generation_attempts=8,
    ):
        self.map_width = map_width
        self.map_height = map_height
        self.enemy_count = enemy_count
        self.min_passage_width = max(2, min_passage_width)
        self.max_generation_attempts = max(1, max_generation_attempts)

        self.floor_value = Tiles.FLOOR.value
        self.wall_value = Tiles.WALL.value
        self.cell_step = self.min_passage_width + 1
        self.center_offset = self.min_passage_width // 2

        self.logical_width = self.logical_cell_count(self.map_width)
        self.logical_height = self.logical_cell_count(self.map_height)
        self.cells = [
            (cell_x, cell_y)
            for cell_y in range(self.logical_height)
            for cell_x in range(self.logical_width)
        ]
        if not self.cells:
            raise ValueError(
                "Maze map is too small for the minimum passage width"
            )

        self.cell_center_tiles = [
            self.cell_center_tile(cell)
            for cell in self.cells
        ]

    def logical_cell_count(self, map_size):
        available_span = map_size - self.min_passage_width - 2
        return 0 if available_span < 0 else 1 + available_span // self.cell_step

    def logical_cells(self):
        return self.cells

    def tile_to_world_center(self, tile_x, tile_y):
        return (
            tile_x * TILE_SIZE + TILE_SIZE // 2,
            tile_y * TILE_SIZE + TILE_SIZE // 2,
        )

    def is_walkable_tile(self, grid, tile_x, tile_y):
        return (
            0 <= tile_y < len(grid)
            and 0 <= tile_x < len(grid[0])
            and grid[tile_y][tile_x] == self.floor_value
        )

    def cell_origin(self, cell):
        cell_x, cell_y = cell
        return (
            1 + cell_x * self.cell_step,
            1 + cell_y * self.cell_step,
        )

    def cell_center_tile(self, cell):
        origin_x, origin_y = self.cell_origin(cell)
        return (
            origin_x + self.center_offset,
            origin_y + self.center_offset,
        )

    def carve_rect(self, grid, left, top, width, height):
        fill = [self.floor_value] * width
        for tile_y in range(top, top + height):
            grid[tile_y][left:left + width] = fill

    def carve_cell(self, grid, cell):
        self.carve_rect(
            grid,
            *self.cell_origin(cell),
            self.min_passage_width,
            self.min_passage_width,
        )

    def carve_connection(self, grid, from_cell, to_cell):
        from_x, from_y = self.cell_origin(from_cell)
        to_x, to_y = self.cell_origin(to_cell)

        if from_y == to_y:
            self.carve_rect(
                grid,
                min(from_x, to_x) + self.min_passage_width,
                from_y,
                1,
                self.min_passage_width,
            )
            return

        self.carve_rect(
            grid,
            from_x,
            min(from_y, to_y) + self.min_passage_width,
            self.min_passage_width,
            1,
        )

    def logical_neighbors(self, cell):
        cell_x, cell_y = cell
        for step_x, step_y in CARDINAL_STEPS:
            next_cell = (cell_x + step_x, cell_y + step_y)
            if 0 <= next_cell[0] < self.logical_width and 0 <= next_cell[1] < self.logical_height:
                yield next_cell

    def generate_maze_tiles(self):
        grid = [
            [self.wall_value for _ in range(self.map_width)]
            for _ in range(self.map_height)
        ]
        start_cell = random.choice(self.cells)
        stack = [start_cell]
        visited = {start_cell}
        self.carve_cell(grid, start_cell)

        while stack:
            current_cell = stack[-1]
            neighbors = [
                next_cell
                for next_cell in self.logical_neighbors(current_cell)
                if next_cell not in visited
            ]
            if not neighbors:
                stack.pop()
                continue

            next_cell = random.choice(neighbors)
            self.carve_connection(grid, current_cell, next_cell)
            self.carve_cell(grid, next_cell)
            visited.add(next_cell)
            stack.append(next_cell)

        return grid, self.cell_center_tile(start_cell)

    def collect_floor_distances(self, grid, start_tile):
        if not self.is_walkable_tile(grid, *start_tile):
            return {}

        distances = {start_tile: 0}
        queue = deque([start_tile])

        while queue:
            tile_x, tile_y = queue.popleft()
            current_distance = distances[(tile_x, tile_y)]

            for step_x, step_y in CARDINAL_STEPS:
                next_tile = (tile_x + step_x, tile_y + step_y)
                if next_tile in distances or not self.is_walkable_tile(grid, *next_tile):
                    continue

                distances[next_tile] = current_distance + 1
                queue.append(next_tile)

        return distances

    def reachable_cell_center_tiles(self, distances):
        return [
            tile
            for tile in self.cell_center_tiles
            if tile in distances
        ]

    def choose_exit_tile(self, distances):
        safe_tiles = self.reachable_cell_center_tiles(distances)
        if not safe_tiles:
            return None

        return max(safe_tiles, key=distances.get)

    def floor_run_length(self, grid, tile_x, tile_y, step_x, step_y):
        run_length = 1

        for direction in (1, -1):
            next_x = tile_x + step_x * direction
            next_y = tile_y + step_y * direction

            while self.is_walkable_tile(grid, next_x, next_y):
                run_length += 1
                next_x += step_x * direction
                next_y += step_y * direction

        return run_length

    def tile_has_min_wall_spacing(self, grid, tile_x, tile_y):
        return min(
            self.floor_run_length(grid, tile_x, tile_y, 1, 0),
            self.floor_run_length(grid, tile_x, tile_y, 0, 1),
        ) >= self.min_passage_width

    def validate_wall_spacing(self, grid):
        return all(
            tile != self.floor_value
            or self.tile_has_min_wall_spacing(grid, tile_x, tile_y)
            for tile_y, row in enumerate(grid)
            for tile_x, tile in enumerate(row)
        )

    def sample_enemy_tiles(self, distances, start_tile, exit_tile):
        if self.enemy_count <= 0 or not distances:
            return []

        safe_tiles = [
            tile
            for tile in self.reachable_cell_center_tiles(distances)
            if tile not in (start_tile, exit_tile)
        ]
        if not safe_tiles:
            return []

        min_distance_from_start = max(6, max(distances.values()) // 4)
        candidate_tiles = [
            tile
            for tile in safe_tiles
            if distances[tile] >= min_distance_from_start
        ] or safe_tiles

        random.shuffle(candidate_tiles)
        selected_tiles = []

        for tile in candidate_tiles:
            if all(
                abs(tile[0] - other[0]) + abs(tile[1] - other[1]) >= 4
                for other in selected_tiles
            ):
                selected_tiles.append(tile)
                if len(selected_tiles) == self.enemy_count:
                    return selected_tiles

        for tile in candidate_tiles:
            if tile in selected_tiles:
                continue

            selected_tiles.append(tile)
            if len(selected_tiles) == self.enemy_count:
                return selected_tiles

        while selected_tiles and len(selected_tiles) < self.enemy_count:
            selected_tiles.append(random.choice(selected_tiles))

        return selected_tiles

    def build_enemy_spawns(self, enemy_tiles):
        return [
            EnemySpawn(
                room_id=0,
                position=self.tile_to_world_center(tile_x, tile_y),
            )
            for tile_x, tile_y in enemy_tiles
        ]

    def generate(self):
        for _ in range(self.max_generation_attempts):
            grid, start_tile = self.generate_maze_tiles()
            if not self.validate_wall_spacing(grid):
                continue

            distances = self.collect_floor_distances(grid, start_tile)
            exit_tile = self.choose_exit_tile(distances)
            if not distances or exit_tile is None:
                continue

            enemy_tiles = self.sample_enemy_tiles(
                distances,
                start_tile,
                exit_tile,
            )
            return GeneratedLevel(
                tiles=grid,
                rooms=[(0, 0, self.map_width, self.map_height)],
                player_spawn=self.tile_to_world_center(*start_tile),
                enemy_spawns=self.build_enemy_spawns(enemy_tiles),
                exit_spawn=self.tile_to_world_center(*exit_tile),
                exit_room_id=0,
                boss_spawn=None,
                boss_room_id=None,
                shop_spawn=None,
                shop_room_id=None,
            )

        raise RuntimeError(
            "Maze generator could not create a labyrinth "
            f"with minimum passage width {self.min_passage_width}"
        )
