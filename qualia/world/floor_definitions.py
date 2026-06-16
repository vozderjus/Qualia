from dataclasses import dataclass

from entities.blue_eye_enemy import BlueEyeEnemy
from entities.heart_enemy import HeartEnemy
from entities.orange_eye_enemy import OrangeEye
from entities.prism_enemy import SniperEnemy
from entities.teeth_enemy import ShotgunEnemy


@dataclass(frozen=True)
class FloorDefinition:
    floor_number: int
    name: str
    map_width: int
    map_height: int
    max_depth: int
    enemy_count: int
    enemy_pool: tuple[type, ...]
    floor_tile_path: str = "images/floor_tile1.png"
    wall_tile_path: str = "images/wall_tile.png"
    floor_tint: tuple[int, int, int] | None = None
    wall_tint: tuple[int, int, int] | None = None
    has_exit: bool = True
    has_shop: bool = False
    is_boss_floor: bool = False


FLOOR_DEFINITIONS = (
    FloorDefinition(
        floor_number=1,
        name="Подземелье",
        map_width=50,
        map_height=40,
        max_depth=3,
        enemy_count=5,
        enemy_pool=(OrangeEye, ShotgunEnemy),
        floor_tint=(255, 255, 255),
        wall_tint=(245, 245, 255),
    ),
    FloorDefinition(
        floor_number=2,
        name="Холодные Залы",
        map_width=52,
        map_height=42,
        max_depth=3,
        enemy_count=6,
        enemy_pool=(OrangeEye, ShotgunEnemy, SniperEnemy, HeartEnemy),
        floor_tint=(220, 240, 255),
        wall_tint=(210, 225, 255),
    ),
    FloorDefinition(
        floor_number=3,
        name="Медные Коридоры",
        map_width=55,
        map_height=44,
        max_depth=4,
        enemy_count=7,
        enemy_pool=(BlueEyeEnemy, HeartEnemy, SniperEnemy, ShotgunEnemy),
        floor_tint=(255, 230, 205),
        wall_tint=(240, 210, 185),
        has_shop=True,
    ),
    FloorDefinition(
        floor_number=4,
        name="Пепельный Лабиринт",
        map_width=58,
        map_height=46,
        max_depth=4,
        enemy_count=8,
        enemy_pool=(BlueEyeEnemy, ShotgunEnemy, HeartEnemy, SniperEnemy),
        floor_tint=(230, 225, 220),
        wall_tint=(205, 195, 190),
    ),
    FloorDefinition(
        floor_number=5,
        name="Преддверие Босса",
        map_width=60,
        map_height=48,
        max_depth=4,
        enemy_count=9,
        enemy_pool=(ShotgunEnemy, HeartEnemy, BlueEyeEnemy, SniperEnemy),
        floor_tint=(235, 220, 210),
        wall_tint=(220, 195, 180),
        has_exit=False,
        is_boss_floor=True,
    ),
)
