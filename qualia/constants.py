import os
from enum import Enum

# === разрешение основной игры ===
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CAMERA_ZOOM = 1.5


# === все что связано с игроком ===
PLAYER_SIZE = 64
PLAYER_SPEED = 200


# === ВРАГИ ===
# оранжевый глаз (первый враг!!!)
ORANGE_EYE_HP = 3
ORANGE_EYE_SPEED = 200
ORANGE_EYE_COOLDOWN = 1.0
SNIPER_EYE_HP = 2
SNIPER_EYE_SPEED = 130
SNIPER_EYE_COOLDOWN = 1.8

# === все что связано с тайлингом ===
TILE_SIZE = 32
MIN_CORRIDOR_WIDTH = 3
MIN_ROOM_SIZE = 8
MIN_AREA_SIZE = 10

class Tiles(Enum):
    FLOOR = 1
    WALL = 2


# === все что связано с пулями ===
PLAYER_BULLET_SIZE = 10
PLAYER_BULLET_VELOCITY = 400
PLAYER_FIRE_COOLDOWN = 0.15
ENEMY_BULLET_VELOCITY = 600
SNIPER_BULLET_VELOCITY = 900

# === Этажи ===
FLOOR_CONFIGS = (
    {"map_width": 50, "map_height": 40, "max_depth": 3, "enemy_count": 5},
    {"map_width": 52, "map_height": 42, "max_depth": 3, "enemy_count": 6},
    {"map_width": 55, "map_height": 44, "max_depth": 4, "enemy_count": 7},
    {"map_width": 58, "map_height": 46, "max_depth": 4, "enemy_count": 8},
    {"map_width": 60, "map_height": 48, "max_depth": 4, "enemy_count": 9},
)
