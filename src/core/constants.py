import pygame

TILE_SIZE = 32
GRID_W = 16
GRID_H = 16

WIDTH = GRID_W * TILE_SIZE
HEIGHT = GRID_H * TILE_SIZE
FPS = 60

COLORS = {
    "bg": (18, 18, 24),
    "grid_line": (40, 40, 50),
    "hero_idle": (180, 180, 180),
    "hero_moving": (76, 175, 80),
    "hero_lose": (220, 60, 60),
    "hero_win": (0, 230, 100),
    "text": (230, 230, 230),
    "debug_overlay": (0, 0, 0, 180),
    "wall": (100, 100, 110),
    "start": (76, 175, 80),
    "exit": (255, 193, 7),
    "rule": (100, 150, 255),
    "trap": (220, 60, 60)
}

class GameState:
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    EXITING = "EXITING"

STEP_INTERVAL = 0.3
MAX_STEPS = 64

class HeroState:
    IDLE = "IDLE"
    MOVING = "MOVING"
    WIN = "WIN"
    LOSE = "LOSE"