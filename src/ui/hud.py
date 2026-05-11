import pygame
from src.logic.inventory import Inventory
from src.grid.rules import get_rule_meta

class HUD:
    """Минимальный интерфейс для Фазы 2.1: инвентарь + подсветка сетки."""

    def __init__(self, screen: pygame.Surface, inventory: Inventory, 
                 cell_size: int = 40, rule_images: dict = None):
        self.screen = screen
        self.inventory = inventory
        self.cell_size = cell_size
        self.rule_images = rule_images or {}  # Словарь картинок
        self.font = pygame.font.SysFont("consolas", 20)

        # Геометрия панели (внизу экрана)
        self.panel_h = 80
        self.panel_y = screen.get_height() - self.panel_h
        self.slot_size = 60
        self.gap = 10
        
        # Формируем слоты один раз
        self.slots = []
        x = 20
        y = self.panel_y + 10
        for tile_type in inventory.slots.keys():
            rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            self.slots.append((tile_type, rect))
            x += self.slot_size + self.gap

    def get_slot_at(self, mouse_pos: tuple[int, int]):
        """Возвращает тип плитки, если клик попал в слот инвентаря."""
        for tile_type, rect in self.slots:
            if rect.collidepoint(mouse_pos):
                return tile_type
        return None

    def draw(self, mouse_pos: tuple[int, int], grid_pos: tuple[int, int] | None, is_valid: bool):
        """Отрисовка панели и подсветки. Вызывается после отрисовки сетки."""
        # 1. Фон панели
        pygame.draw.rect(self.screen, (35, 35, 45), (0, self.panel_y, self.screen.get_width(), self.panel_h))

        # 2. Слоты инвентаря
        selected = self.inventory.get_selected()
        for tile_type, rect in self.slots:
            meta = get_rule_meta(tile_type)
            if not meta: continue
            
            count = self.inventory.get_count(tile_type)
            # Цвет слота: зелёный если выбран, серый иначе
            bg = (80, 150, 80) if tile_type == selected else (55, 55, 70)
            pygame.draw.rect(self.screen, bg, rect)
            
            # Символ правила или картинка
            if count > 0:
                # Пробуем нарисовать картинку, если есть
                img = self.rule_images.get(tile_type)
                if img:
                    self.screen.blit(img, (rect.x + 6, rect.y + 6))
                else:
                    # Фолбэк на текст
                    sym = self.font.render(meta.symbol, True, meta.color)
                    self.screen.blit(sym, (rect.centerx - sym.get_width()//2, rect.centery - sym.get_height()//2))
                
                # Счётчик
                cnt = self.font.render(str(count), True, (255, 255, 255))
                self.screen.blit(cnt, (rect.right - 18, rect.bottom - 18))

        # 3. Подсветка ячейки под курсором
        if grid_pos:
            row, col = grid_pos
            x, y = col * self.cell_size, row * self.cell_size
            color = (60, 220, 60) if is_valid else (220, 60, 60)
            # Рамка + лёгкая заливка
            pygame.draw.rect(self.screen, (*color, 50), (x, y, self.cell_size, self.cell_size))
            pygame.draw.rect(self.screen, color, (x, y, self.cell_size, self.cell_size), width=2)