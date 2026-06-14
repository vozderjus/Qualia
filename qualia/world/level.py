import pygame
from constants import TILE_SIZE, Tiles


class Level:
    FLOOR = Tiles.FLOOR
    WALL = Tiles.WALL
    
    def __init__(
        self,
        tiles,
        floor_tile_path="images/floor_tile1.png",
        wall_tile_path="images/wall_tile.png",
        floor_tint=None,
        wall_tint=None,
    ):
        self.tile_size = TILE_SIZE
        
        # Создание уровня, то есть тут мы подключаем BSP
        self.tiles = tiles
        
        # картиночки для пола и стен (TODO - bitmap с полом)
        self.floor_tile = self.load_tinted_tile(floor_tile_path, floor_tint)
        self.wall_tile = self.load_tinted_tile(wall_tile_path, wall_tint)
        # зум, увеличение тайлов под зум
        self._cached_zoom = None
        self._scaled_floor_tile = self.floor_tile
        self._scaled_wall_tile = self.wall_tile

        # ширина и высота уровня в пикселях
        self.pixel_width = len(self.tiles[0]) * self.tile_size
        self.pixel_height = len(self.tiles) * self.tile_size

    def load_tinted_tile(self, path, tint):
        tile = pygame.image.load(path).convert_alpha()

        if tint is None:
            return tile

        tinted_tile = tile.copy()
        tint_surface = pygame.Surface(tinted_tile.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*tint, 255))
        tinted_tile.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_tile
    
    # функция для проверки коллизий
    def collides_with_wall(self, rect):
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

    # вспомогательный метод для расчета линии взгляда
    def world_point_to_tile(self, x, y):
        return int(x // self.tile_size), int(y // self.tile_size)

    # линия взгляда врагов
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

    # применение зума
    def update_scaled_tiles(self, zoom):
        # если зум уже применен - не делаем ничего
        if self._cached_zoom == zoom:
            return

        scaled_size = max(1, int(self.tile_size * zoom))
        self._scaled_floor_tile = pygame.transform.scale(
            self.floor_tile,
            (scaled_size, scaled_size),
        )
        self._scaled_wall_tile = pygame.transform.scale(
            self.wall_tile,
            (scaled_size, scaled_size),
        )
        self._cached_zoom = zoom

    def render(self, display, camera):
        self.update_scaled_tiles(camera.zoom)

        rows = len(self.tiles)
        cols = len(self.tiles[0])
        start_col, end_col, start_row, end_row = camera.get_visible_range(
            self.tile_size,
            cols,
            rows,
        )

        for row_index in range(start_row, end_row):
            for col_index in range(start_col, end_col):
                tile = self.tiles[row_index][col_index]
                
                world_x = col_index * self.tile_size
                world_y = row_index * self.tile_size
                
                screen_x, screen_y = camera.apply(world_x, world_y)

                # отрисовка пола
                if tile == self.FLOOR.value:
                    display.blit(self._scaled_floor_tile, (int(screen_x), int(screen_y)))
                # отрисовка стен
                elif tile == self.WALL.value:
                    display.blit(self._scaled_wall_tile, (int(screen_x), int(screen_y)))
