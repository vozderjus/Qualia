import os
from enum import Enum

# === разрешение основной игры ===
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CAMERA_ZOOM = 1.5


# === все что связано с игроком ===
PLAYER_SIZE = 64
PLAYER_HITBOX_WIDTH = 36
PLAYER_HITBOX_HEIGHT = 38
PLAYER_RENDER_OFFSET_Y = 4
PLAYER_SPEED = 200
PLAYER_MAX_HP = 120
PLAYER_DODGE_SPEED = 560
PLAYER_DODGE_DURATION = 0.16
PLAYER_DODGE_COOLDOWN = 0.7
HEAT_DROP_RANGE = (8, 12)
HEAT_PICKUP_SIZE = 18

# === ВРАГИ ===

# оранжевый глаз (первый враг!!!)
ORANGE_EYE_HP = 90
ORANGE_EYE_SPEED = 200
ORANGE_EYE_COOLDOWN = 1.0

# шотганер
SHOTGUN_ENEMY_HP = 105

# снайпер
SNIPER_EYE_HP = 80
SNIPER_EYE_SPEED = 130
SNIPER_EYE_COOLDOWN = 1.8

# сердце
HEART_HP = 200
HEART_SPEED = 0
HEART_COOLDOWN = 1

# голубой глаз (усложненный оранжевый)
BLUE_EYE_HP = 150
BLUE_EYE_SPEED = 250
BLUE_EYE_COOLDOWN = 0.8

# босс
BOSS_SIZE = 128
BOSS_HP = 1750

# === все что связано с тайлингом ===
TILE_SIZE = 32
MIN_CORRIDOR_WIDTH = 3
MIN_ROOM_SIZE = 10
MIN_AREA_SIZE = 12

class Tiles(Enum):
    FLOOR = 1
    WALL = 2


# === все что связано с пулями ===

# игрок
PLAYER_BULLET_SIZE = 10
PLAYER_BULLET_VELOCITY = 400
PLAYER_FIRE_COOLDOWN = 0.15
PLAYER_BULLET_DAMAGE_RANGE = (22, 34)
PLAYER_BULLET_COLOR = (255, 255, 0)

# общий враг
ENEMY_BULLET_VELOCITY = 400
ENEMY_BULLET_DAMAGE_RANGE = (8, 12)
ENEMY_BULLET_COLOR = (200, 24, 40)

# снайпер
SNIPER_BULLET_VELOCITY = 600
SNIPER_BULLET_DAMAGE_RANGE = (10, 14)

# сердце
HEART_BULLET_VELOCITY = 100
HEART_BULLET_DAMAGE_RANGE = (8, 15)

# голубой глаз
BLUE_BULLET_VELOCITY = 400
BLUE_BULLET_DAMAGE_RANGE = (12, 15)
BLUE_BULLET_BOUNCE_RANGE = (1, 3)
BLUE_BULLET_SPEED_LOSS_PER_BOUNCE = 80


# Описание настроек
SETTINGS_LORE_PARAGRAPHS = (
    "Солнце уснуло в лучах серого мира, окунувшись в собственное ощущение мира. Ему пришлось взглянуть на внутренний мир. Это лишь сон, из которого можно пробудиться в любую секунду, или минуту, или год. Вы никогда не сможете почувствовать то же, что чувствовали прошлой ночью. Вы никогда не окажетесь там же, где были тогда. Но каждый раз вы будете встречать того, с кем приходится бороться изо дня в день. С самим собой."
)


SETTINGS_CREDITS_LINES = (
    "Игра от Vozderjus",
    "",
    "Основная идея и сюжет: Vozderjus",
    "Логика игры и программирование: Vozderjus",
    "Боевая система и поведение врагов: Vozderjus",
    "Генерация уровней: Vozderjus",
    "Музыка: Vozderjus",
    "Ассеты и визуальное наполнение: Vozderjus",
)
