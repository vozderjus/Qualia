from dataclasses import dataclass

from entities.level_exit import LevelExit
from world.bsp_generator import BSPGenerator
from world.level import Level
from world.level_renderer import LevelRenderer


@dataclass(frozen=True, slots=True)
class EnemySpawnRequest:
    room_id: int
    position: tuple[int, int]
    enemy_class: type


@dataclass(frozen=True, slots=True)
class BossSpawnRequest:
    room_id: int
    position: tuple[int, int]
    boss_class: type


@dataclass(frozen=True, slots=True)
class FloorBuildResult:
    level: Level
    level_renderer: LevelRenderer
    rooms: list[tuple[int, int, int, int]]
    player_spawn: tuple[int, int]
    enemy_spawns: list[EnemySpawnRequest]
    boss_spawn: BossSpawnRequest | None
    boss_room_id: int | None
    floor_exit: LevelExit | None
    floor_exit_room_id: int | None
    shop_spawn: tuple[int, int] | None
    shop_room_id: int | None


class FloorBuilder:
    def build(self, floor_definition):
        generated_level = BSPGenerator(
            floor_definition.map_width,
            floor_definition.map_height,
            max_depth=floor_definition.max_depth,
            enemy_count=floor_definition.enemy_count,
            has_shop=floor_definition.has_shop,
            is_boss_floor=floor_definition.is_boss_floor,
            boss_min_room_width=floor_definition.boss_min_room_width,
            boss_min_room_height=floor_definition.boss_min_room_height,
            boss_min_room_area=floor_definition.boss_min_room_area,
        ).generate()

        level = Level(generated_level.tiles)
        level_renderer = LevelRenderer(
            level,
            floor_tile_path=floor_definition.floor_tile_path,
            wall_tile_path=floor_definition.wall_tile_path,
            floor_tint=floor_definition.floor_tint,
            wall_tint=floor_definition.wall_tint,
        )

        enemy_spawns = []
        if floor_definition.enemy_pool:
            for index, enemy_spawn in enumerate(generated_level.enemy_spawns):
                enemy_class = floor_definition.enemy_pool[
                    index % len(floor_definition.enemy_pool)
                ]
                enemy_spawns.append(
                    EnemySpawnRequest(
                        room_id=enemy_spawn.room_id,
                        position=enemy_spawn.position,
                        enemy_class=enemy_class,
                    )
                )

        boss_spawn = None
        if (
            floor_definition.boss_class is not None
            and generated_level.boss_spawn is not None
            and generated_level.boss_room_id is not None
        ):
            boss_spawn = BossSpawnRequest(
                room_id=generated_level.boss_room_id,
                position=generated_level.boss_spawn,
                boss_class=floor_definition.boss_class,
            )

        floor_exit = None
        if floor_definition.has_exit and generated_level.exit_spawn is not None:
            floor_exit = LevelExit(generated_level.exit_spawn)

        return FloorBuildResult(
            level=level,
            level_renderer=level_renderer,
            rooms=generated_level.rooms,
            player_spawn=generated_level.player_spawn,
            enemy_spawns=enemy_spawns,
            boss_spawn=boss_spawn,
            boss_room_id=generated_level.boss_room_id,
            floor_exit=floor_exit,
            floor_exit_room_id=generated_level.exit_room_id,
            shop_spawn=generated_level.shop_spawn,
            shop_room_id=generated_level.shop_room_id,
        )
