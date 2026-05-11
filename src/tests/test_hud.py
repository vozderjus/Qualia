"""
Изолированный стенд для отладки HUD.
Запускается независимо от main.py. Позволяет проверить отрисовку, 
выбор слотов и реакцию на валидацию без игрового цикла.
"""

import pygame
import sys
import os
from src.ui.hud import HUD
from src.logic.inventory import Inventory
from src.grid.tiles import TileType

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Локальные константы для теста (не зависят от core/constants)
SCREEN_W, SCREEN_H = 800, 600
CELL_SIZE = 40

def run_hud_sandbox():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("HUD Sandbox | Phase 2.1")
    clock = pygame.time.Clock()

    # 1. Создаём тестовый инвентарь с разными состояниями
    test_inventory = Inventory({
        TileType.RULE_RIGHT: 4,   # Есть в наличии
        TileType.RULE_LEFT: 0,    # Пустой слот (должен показать "0")
        TileType.RULE_ROTATE: 2,
        TileType.RULE_JUMP: 1
    })
    # Предварительно выбираем первую плитку, чтобы увидеть подсветку слота
    test_inventory.select_tile(TileType.RULE_RIGHT)

    hud = HUD(screen, test_inventory, CELL_SIZE)
    
    running = True
    # Флаги для ручной проверки состояний
    force_valid = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Тестируем выбор слота
                slot = hud.get_slot_at(event.pos)
                if slot:
                    test_inventory.select_tile(slot)
                    print(f"[SANDBOX] Выбран слот: {slot.name}")
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    # Переключаем валидность подсветки (имитация клика по занятой/пустой ячейке)
                    force_valid = not force_valid
                    print(f"[SANDBOX] Valid toggle: {force_valid}")

        # 2. Имитируем данные, которые normally приходят из Grid/Game
        mouse_pos = pygame.mouse.get_pos()
        # Фиксируем позицию на сетке для наглядности (строка 3, колонка 5)
        grid_pos = (3, 5) 
        
        # 3. Отрисовка
        screen.fill((25, 25, 35))  # Тёмный фон вместо сетки
        hud.draw(mouse_pos, grid_pos, force_valid)
        
        # Подсказка для тестировщика
        font = pygame.font.SysFont("consolas", 16)
        hint = font.render(f"VALID={force_valid} | Press [V] to toggle | Click slots to select", True, (200, 200, 200))
        screen.blit(hint, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

run_hud_sandbox()