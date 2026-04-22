from typing import Tuple
import pygame
from src.core.constants import TILE_SIZE
from src.grid.tiles import TileType, get_tile_props

class Grid:
    def __init__(self, width: int = 16, height: int = 16):
        self.width = width
        self.height = height
        self.tile_size = TILE_SIZE
        self.tiles: list[list[TileType]] = [
            [TileType.EMPTY for _ in range(width)] for _ in range(height)
        ]

    def is_valid(self, x: int, y: int) -> bool:
        """Проверка границ"""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> TileType:
        if not self.is_valid(x, y):
            raise ValueError(f"Запрос клетки вне границ: ({x}, {y}). Сетка: {self.width}x{self.height}")
        return self.tiles[y][x]

    def set_tile(self, x: int, y: int, tile: TileType) -> None:
        if not self.is_valid(x, y):
            raise ValueError(f"Попытка записать клетку вне границ: ({x}, {y})")
        self.tiles[y][x] = tile

    def is_solid(self, x: int, y: int) -> bool:
        if not self.is_valid(x, y):
            return True  # За пределами сетки всегда "твердо"
        return get_tile_props(self.get_tile(x, y)).is_solid

    def is_hazardous(self, x: int, y: int) -> bool:
        if not self.is_valid(x, y):
            return False
        return get_tile_props(self.get_tile(x, y)).is_hazardous

    def to_pixel_rect(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)

    def from_pixel(self, px: int, py: int) -> Tuple[int, int]:
        """Перевод координат мыши/касания в индексы сетки"""
        return px // self.tile_size, py // self.tile_size

    def clear(self) -> None:
        """Сброс поля"""
        self.tiles = [[TileType.EMPTY for _ in range(self.width)] for _ in range(self.height)]

    def debug_info(self, highlight_x: int | None = None, highlight_y: int | None = None) -> str:
        """
        Генерирует читаемый снимок состояния для оверлея.
        """
        char_map = {
            TileType.EMPTY: "·", TileType.WALL: "█", TileType.START: "S",
            TileType.EXIT: "E", TileType.TRAP: "⚠", TileType.RULE_RIGHT: "→",
            TileType.RULE_UP: "↑", TileType.RULE_LEFT: "←", TileType.RULE_DOWN: "↓"
        }
        lines = []
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                char = char_map.get(self.tiles[y][x], "?")
                if x == highlight_x and y == highlight_y:
                    char = f"[{char}]"
                row_str += f"{char:2} "
            lines.append(row_str)
        return "\n".join(lines)