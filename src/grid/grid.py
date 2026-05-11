"""
Модуль сетки уровня.
Отвечает за хранение состояния ячеек, базовую валидацию и отрисовку.
"""

from typing import Tuple, Optional
import pygame
from src.core.constants import TILE_SIZE, COLORS
from src.grid.tiles import TileType, get_tile_props, TILE_PROPERTIES


class Grid:
    """Двумерная сетка уровня."""
    
    def __init__(self, width: int = 16, height: int = 16):
        self.width = width      # Количество колонок (ось X)
        self.height = height    # Количество строк (ось Y)
        self.tile_size = TILE_SIZE
        
        # Сетка: tiles[row][col] → tiles[y][x]
        self.tiles: list[list[TileType]] = [
            [TileType.EMPTY for _ in range(width)] 
            for _ in range(height)
        ]
        
        # Кэшированные поверхности для отрисовки (чтобы не создавать каждый кадр)
        self._tile_surfaces: dict[TileType, pygame.Surface] = {}
        self._prepare_tile_surfaces()

    def _prepare_tile_surfaces(self):
        """Создаёт поверхности для отрисовки типов плиток один раз."""
        for tile_type in TileType:
            surf = pygame.Surface((self.tile_size, self.tile_size))
            props = get_tile_props(tile_type)
            
            # Базовая заливка по типу
            if props.is_solid:
                surf.fill(COLORS.get("WALL", (100, 100, 120)))
            elif props.is_goal:
                surf.fill(COLORS.get("EXIT", (50, 200, 50)))
            elif props.is_start:
                surf.fill(COLORS.get("START", (50, 100, 255)))
            elif props.is_hazardous:
                surf.fill(COLORS.get("TRAP", (200, 50, 50)))
            elif props.is_rule:
                surf.fill(COLORS.get("RULE_BG", (70, 70, 90)))
            else:
                surf.fill(COLORS.get("EMPTY", (40, 40, 55)))
            
            # Рамка для визуального разделения
            pygame.draw.rect(surf, (80, 80, 100), surf.get_rect(), width=1)
            
            # Символ для правил (если есть)
            if props.is_rule and tile_type in TILE_PROPERTIES:
                # Простая отрисовка текста для правил
                symbol = self._get_rule_symbol(tile_type)
                if symbol:
                    font = pygame.font.SysFont("consolas", 24, bold=True)
                    text = font.render(symbol, True, (255, 255, 255))
                    surf.blit(text, text.get_rect(center=(self.tile_size//2, self.tile_size//2)))
            
            self._tile_surfaces[tile_type] = surf

    def _get_rule_symbol(self, tile_type: TileType) -> str:
        """Возвращает символ для правила (заглушка, пока нет rules.py)."""
        symbols = {
            TileType.RULE_RIGHT: "→",
            TileType.RULE_LEFT: "←",
            TileType.RULE_UP: "↑",
            TileType.RULE_DOWN: "↓",
            TileType.RULE_ROTATE: "↺",
            TileType.RULE_JUMP: "⚡",
        }
        return symbols.get(tile_type, "")

    # === БАЗОВЫЕ МЕТОДЫ ДОСТУПА ===
    
    def is_valid(self, col: int, row: int) -> bool:
        """Проверка: находится ли ячейка в границах сетки."""
        return 0 <= col < self.width and 0 <= row < self.height

    def get_tile(self, col: int, row: int) -> TileType:
        """Получить тип плитки по координатам (col, row)."""
        if not self.is_valid(col, row):
            return TileType.EMPTY  # Безопасный возврат вместо исключения
        return self.tiles[row][col]

    def set_tile(self, col: int, row: int, tile: TileType) -> None:
        """Установить тип плитки по координатам (col, row)."""
        if self.is_valid(col, row):
            self.tiles[row][col] = tile

    # === ФИЗИЧЕСКИЕ ПРОВЕРКИ ===
    
    def is_solid(self, col: int, row: int) -> bool:
        """Можно ли пройти через ячейку?"""
        if not self.is_valid(col, row):
            return True  # За пределами — стена
        return get_tile_props(self.get_tile(col, row)).is_solid

    def is_hazardous(self, col: int, row: int) -> bool:
        """Наносит ли ячейка урон?"""
        if not self.is_valid(col, row):
            return False
        return get_tile_props(self.get_tile(col, row)).is_hazardous

    # === КОНВЕРТАЦИЯ КООРДИНАТ ===
    
    def to_pixel_rect(self, col: int, row: int) -> pygame.Rect:
        """Преобразует координаты сетки в прямоугольник экрана."""
        return pygame.Rect(
            col * self.tile_size,
            row * self.tile_size,
            self.tile_size,
            self.tile_size
        )

    def from_pixel(self, px: int, py: int) -> Tuple[int, int]:
        """Экранные координаты → индексы сетки (col, row)."""
        return px // self.tile_size, py // self.tile_size

    def screen_to_grid(self, mouse_pos: tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Координаты мыши → (row, col) для совместимости с main.py.
        Возвращает None, если клик вне сетки.
        """
        col, row = self.from_pixel(*mouse_pos)
        if self.is_valid(col, row):
            return (row, col)  # Возвращаем (row, col) как ожидает main.py
        return None

    # === МЕХАНИКА РАЗМЕЩЕНИЯ ПРАВИЛ ===
    
    def is_free(self, row: int, col: int) -> bool:
        """Можно ли разместить правило в этой ячейке?"""
        if not self.is_valid(col, row):
            return False
        tile = self.tiles[row][col]
        # Разрешаем ставить только на пустые клетки
        return tile == TileType.EMPTY

    # Алиас для совместимости с main.py
    is_cell_free = is_free

    def place_tile(self, row: int, col: int, tile_type: TileType) -> bool:
        """Разместить правило. Возвращает True при успехе."""
        if not self.is_free(row, col):
            return False
        self.tiles[row][col] = tile_type
        return True

    def remove_tile(self, row: int, col: int) -> Optional[TileType]:
        """
        Удалить правило из ячейки.
        Возвращает тип удалённой плитки или None, если удалить нельзя.
        """
        if not self.is_valid(col, row):
            return None
        
        tile = self.tiles[row][col]
        
        # Нельзя удалять статические элементы уровня
        if tile in [TileType.EMPTY, TileType.WALL, TileType.START, TileType.EXIT, TileType.TRAP]:
            return None
        
        self.tiles[row][col] = TileType.EMPTY
        return tile

    def reset_rules(self) -> None:
        """Удалить все правила с поля, сохранив стены/старт/выход."""
        for row in range(self.height):
            for col in range(self.width):
                tile = self.tiles[row][col]
                if get_tile_props(tile).is_rule:
                    self.tiles[row][ col] = TileType.EMPTY

    # === ОТРИСОВКА (ИСПРАВЛЯЕТ ОШИБКУ) ===
    
    def draw(self, screen: pygame.Surface):
        """Отрисовка всей сетки на экране."""
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.tiles[row][col]
                
                # Берём готовую поверхность из кэша
                surf = self._tile_surfaces.get(tile_type)
                if surf:
                    # Вычисляем позицию на экране
                    x = col * self.tile_size
                    y = row * self.tile_size
                    screen.blit(surf, (x, y))