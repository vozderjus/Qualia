import os
from enum import Enum


# === разрешение основной игры ===
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720


# === все что связано с игроком ===
PLAYER_SIZE = 64
PLAYER_SPEED = 200


# === ВРАГИ ===
# оранжевый глаз (первый враг!!!)
ORANGE_EYE_HP = 3
ORANGE_EYE_SPEED = 200
ORANGE_EYE_COOLDOWN = 1.0

# === все что связано с тайлингом ===
TILE_SIZE = 32
MIN_CORRIDOR_WIDTH = 3
MIN_ROOM_WIDTH = 8
MIN_ROOM_HEIGHT = 8

class Tiles(Enum):
    FLOOR = 1
    WALL = 2


# === все что связано с пулями ===
PLAYER_BULLET_SIZE = 10
PLAYER_BULLET_VELOCITY = 400
PLAYER_FIRE_COOLDOWN = 0.15
ENEMY_BULLET_VELOCITY = 600