import pygame
from constants import TILE_SIZE, Tiles

class Level:
    FLOOR = Tiles.FLOOR
    WALL = Tiles.WALL
    
    def __init__(self):
        self.tile_size = TILE_SIZE
        
        # Базовая тестовая арена с широкими проходами под игрока 64x64.
        self.tiles = [
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2],
            [2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2],
            [2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
            [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        ]
        
        self.floor_color = (40, 40, 40)
        self.wall_color = (110, 110, 110)
    
    def render(self, display):
        for row_index, row in enumerate(self.tiles):
            for col_index, tile in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                # отрисовка пола
                if tile == self.FLOOR.value:
                    pygame.draw.rect(
                        display,
                        self.floor_color,
                        (x, y, self.tile_size, self.tile_size)
                    )
                # отрисовка стен
                elif tile == self.WALL.value:
                    pygame.draw.rect(
                        display,
                        self.wall_color,
                        (x, y, self.tile_size, self.tile_size)
                    )
    
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
