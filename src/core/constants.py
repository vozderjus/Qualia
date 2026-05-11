import pygame

TILE_SIZE = 32
GRID_W = 16
GRID_H = 16

WIDTH = GRID_W * TILE_SIZE
HEIGHT = GRID_H * TILE_SIZE
FPS = 60

# src/core/constants.py
COLORS = {
    "BG": (25, 25, 35),
    "EMPTY": (40, 40, 55),
    "WALL": (100, 100, 120),
    "START": (50, 100, 255),
    "EXIT": (50, 200, 50),
    "TRAP": (200, 50, 50),
    "RULE_BG": (70, 70, 90),
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