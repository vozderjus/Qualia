import pygame
from constants import TILE_SIZE, Tiles


class Level:
    FLOOR = Tiles.FLOOR
    WALL = Tiles.WALL
    
    def __init__(self, tiles):
        self.tile_size = TILE_SIZE
        
        # Создание уровня, то есть тут мы подключаем BSP
        self.tiles = tiles
        
        # картиночки для пола и стен (TODO - bitmap с полом)
        self.floor_tile = pygame.image.load("images/floor_tile1.png").convert_alpha()
        self.wall_tile = pygame.image.load("images/wall_tile.png").convert_alpha()
        # зум, увеличение тайлов под зум
        self._cached_zoom = None
        self._scaled_floor_tile = self.floor_tile
        self._scaled_wall_tile = self.wall_tile

        # ширина и высота уровня в пикселях
        self.pixel_width = len(self.tiles[0]) * self.tile_size
        self.pixel_height = len(self.tiles) * self.tile_size
    
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
        x0, y0 = self.world_point_to_tile(*start)
        x1, y1 = self.world_point_to_tile(*end)
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if y0 < 0 or y0 >= len(self.tiles):
                return False
            if x0 < 0 or x0 >= len(self.tiles[0]):
                return False
            if self.tiles[y0][x0] == self.WALL.value:
                return False
            
            if x0 == x1 and y0 == y1:
                return True
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

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
