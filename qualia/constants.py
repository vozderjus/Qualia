import os
from enum import Enum

import pygame
from uis import Button

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# все что связано с игроком
PLAYER_SIZE = 64
PLAYER_SPEED = 200
# все что связано с тайлингом
TILE_SIZE = 32
MIN_CORRIDOR_WIDTH = 3
MIN_ROOM_WIDTH = 8
MIN_ROOM_HEIGHT = 8

class Tiles(Enum):
    FLOOR = 1
    WALL = 2
