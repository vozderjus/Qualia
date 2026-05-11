"""
main.py — Главный координатор игры RuleGrid.
Отвечает за:
1. Инициализацию окна Pygame и подсистем (Сетка, Инвентарь, HUD).
2. Игровой цикл (Game Loop) с разделением логики и рендера.
3. Обработку ввода (Мышь -> HUD -> Grid).
"""

import pygame
import sys
import os

# Импорт наших модулей
from src.core.constants import WIDTH, HEIGHT, TILE_SIZE, COLORS
from src.grid.grid import Grid
from src.grid.tiles import TileType
from src.logic.inventory import Inventory
from src.ui.hud import HUD


class Game:
    def __init__(self):
        # 1. Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RuleGrid | Phase 2.1")
        self.clock = pygame.time.Clock()
        
        # 2. Загрузка ассетов (Картинки правил)
        # Мы загружаем их один раз здесь и передаем в HUD
        self.rule_images = self._load_assets()

        # 3. Инициализация игровых подсистем
        self.grid = Grid(16, 16)  # Поле 16x16
        
        # Создаем тестовое состояние: Стартовая позиция героя (0,0) и Выход (15,15)
        # (В будущем это будет читаться из файла уровня)
        self.grid.set_tile(0, 0, TileType.START)
        self.grid.set_tile(15, 15, TileType.EXIT)

        self.inventory = Inventory.create_default()
        
        # Передаем картинки в HUD, чтобы он мог их рисовать
        self.hud = HUD(self.screen, self.inventory, self.rule_images)

        # 4. Состояния игры
        self.debug_mode = False
        self.running = True

    def _load_assets(self) -> dict:
        """
        Простая загрузка картинок.
        Возвращает словарь {TileType: Surface}
        """
        assets = {}
        asset_dir = os.path.join("assets", "rules")
        
        # Карта соответствия типов и имен файлов
        # Если файла нет, вернем None (HUD отрисует заглушку)
        file_map = {
            TileType.RULE_RIGHT: "right.png",
            TileType.RULE_UP:    "up.png",
            TileType.RULE_LEFT:  "left.png",
            TileType.RULE_DOWN:  "down.png",
            TileType.RULE_ROTATE: "rotate.png",
            TileType.RULE_JUMP:  "jump.png",
        }

        for tile_type, filename in file_map.items():
            path = os.path.join(asset_dir, filename)
            try:
                # convert_alpha() важен для прозрачности PNG
                raw = pygame.image.load(path).convert_alpha()
                # Масштабируем ПОД размер слота (48x48) один раз при старте
                assets[tile_type] = pygame.transform.scale(raw, (48, 48))
            except pygame.error:
                assets[tile_type] = None
                print(f"⚠️ Не найдена картинка: {path}")
        
        return assets

    def run(self):
        """Главный цикл (Game Loop)."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Ограничиваем FPS до 60
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Обработка ввода."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # F1 — включение режима отладки
                if event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                
                # R — сброс уровня (возврат правил в инвентарь)
                elif event.key == pygame.K_r:
                    self.grid.reset_rules()
                    self.inventory.restore_all()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши (ЛКМ)
                    # 1. Сначала проверяем клик по UI (инвентарю)
                    slot_type = self.hud.get_slot_at(mouse_pos)
                    if slot_type:
                        self.inventory.select_tile(slot_type)
                        continue # Если кликнули по UI, не ставим плитку на сетку!

                    # 2. Если клик не по UI, проверяем сетку
                    grid_pos = self.grid.screen_to_grid(mouse_pos)
                    if grid_pos:
                        row, col = grid_pos
                        selected = self.inventory.get_selected()
                        
                        # Логика установки правила
                        if selected and self.inventory.can_place(selected):
                            if self.grid.is_cell_free(row, col):
                                self.grid.place_tile(row, col, selected)
                                self.inventory.consume(selected)
                                
                elif event.button == 3:  # Правая кнопка мыши (ПКМ)
                    # Удаление правила (опционально)
                    grid_pos = self.grid.screen_to_grid(mouse_pos)
                    if grid_pos:
                        row, col = grid_pos
                        removed_type = self.grid.remove_tile(row, col)
                        if removed_type:
                            self.inventory.refund(removed_type)

    def update(self):
        """Логика обновления (Phase 2.1 пуста, так как симуляция еще не работает)."""
        pass

    def draw(self):
        """Отрисовка всего на экране."""
        # 1. Очистка экрана
        self.screen.fill(COLORS["BG"])

        # 2. Отрисовка сетки
        self.grid.draw(self.screen)

        # 3. Подготовка данных для HUD
        mouse_pos = pygame.mouse.get_pos()
        grid_hover = self.grid.screen_to_grid(mouse_pos)
        selected = self.inventory.get_selected()
        
        # Проверяем, валидно ли размещение в этой ячейке
        is_valid = (
            grid_hover is not None and
            selected is not None and
            self.grid.is_cell_free(*grid_hover) and
            self.inventory.can_place(selected)
        )

        # 4. Отрисовка HUD (Инвентарь + Подсветка)
        # HUD рисует поверх сетки
        self.hud = HUD(self.screen, self.inventory, TILE_SIZE, self.rule_images)

        # 5. Дебаг-оверлей
        if self.debug_mode:
            self._draw_debug(mouse_pos, grid_hover)

        pygame.display.flip()

    def _draw_debug(self, mouse, grid_pos):
        font = pygame.font.SysFont("consolas", 14)
        lines = [
            f"Debug Mode (F1)",
            f"Mouse: {mouse}",
            f"Grid Hover: {grid_pos}",
            f"Selected: {self.inventory.get_selected()}",
            f"Inventory: {self.inventory.to_dict()}"
        ]
        
        y = 10
        for line in lines:
            surf = font.render(line, True, (255, 255, 0)) # Желтый текст
            self.screen.blit(surf, (10, y))
            y += 20


if __name__ == "__main__":
    game = Game()
    game.run()