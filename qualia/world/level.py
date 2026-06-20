import pygame
from constants import TILE_SIZE, Tiles


class Level:
    FLOOR = Tiles.FLOOR
    WALL = Tiles.WALL
    
    def __init__(
        self,
        tiles,
    ):
        self.tile_size = TILE_SIZE
        self.tiles = tiles
        self.dynamic_blockers = []
        self.pixel_width = len(self.tiles[0]) * self.tile_size
        self.pixel_height = len(self.tiles) * self.tile_size

    def collides_with_wall(self, rect):
        for blocker in self.dynamic_blockers:
            if blocker.colliderect(rect):
                return True

        left_tile, right_tile = rect.left // self.tile_size, (rect.right - 1) // self.tile_size
        top_tile, bottom_tile = rect.top // self.tile_size, (rect.bottom - 1) // self.tile_size

        for row in range(top_tile, bottom_tile + 1):
            for col in range(left_tile, right_tile + 1):
                if row < 0 or row >= len(self.tiles):
                    return True
                if col < 0 or col >= len(self.tiles[0]):
                    return True
                if self.tiles[row][col] == self.WALL.value:
                    return True

        return False

    def set_dynamic_blockers(self, blockers):
        self.dynamic_blockers = [pygame.Rect(blocker) for blocker in blockers]

    def clear_dynamic_blockers(self):
        self.dynamic_blockers = []

    def world_point_to_tile(self, x, y):
        return int(x // self.tile_size), int(y // self.tile_size)

    def has_line_of_sight(self, start, end):
        start_vec = pygame.Vector2(start)
        end_vec = pygame.Vector2(end)
        ray = end_vec - start_vec
        distance = ray.length()

        if distance == 0:
            return True

        direction = ray.normalize()
        step_size = max(1, self.tile_size // 4)
        steps = int(distance // step_size)

        for step in range(steps + 1):
            sample_point = start_vec + direction * (step * step_size)
            tile_x, tile_y = self.world_point_to_tile(sample_point.x, sample_point.y)

            if tile_y < 0 or tile_y >= len(self.tiles):
                return False
            if tile_x < 0 or tile_x >= len(self.tiles[0]):
                return False
            if self.tiles[tile_y][tile_x] == self.WALL.value:
                return False

        end_tile_x, end_tile_y = self.world_point_to_tile(end_vec.x, end_vec.y)
        if end_tile_y < 0 or end_tile_y >= len(self.tiles):
            return False
        if end_tile_x < 0 or end_tile_x >= len(self.tiles[0]):
            return False

        return self.tiles[end_tile_y][end_tile_x] != self.WALL.value
