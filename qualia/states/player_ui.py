import math

import pygame
from ui_helpers import PanelStyle, draw_panel, draw_text, load_font

MINIMAP_PANEL_SIZE = (220, 220)
MINIMAP_MARGIN = 18
MINIMAP_TOP = 18
MINIMAP_INNER_MARGIN = 10
MINIMAP_PANEL_STYLE = PanelStyle(
    fill_color=(14, 18, 24),
    border_color=(150, 132, 102),
    border_radius=14,
    border_width=3,
)


class HealthBar():
    def __init__(self, curr_hp, max_hp):
        self.x = 25
        self.y = 65
        self.w = 256
        self.h = 32
        self.hp = curr_hp
        self.max_hp = max_hp

    def update(self, curr_hp, max_hp):
        self.hp = curr_hp
        self.max_hp = max_hp

    def render(self, surface):
        if self.max_hp <= 0:
            ratio = 0
        else:
            ratio = max(0, min(1, self.hp / self.max_hp))

        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))


class PlayerUI():
    def __init__(self, game, curr_hp, max_hp):
        self.game = game
        self.health_bar = HealthBar(curr_hp, max_hp)
        self.current_floor = 1
        self.total_floors = 1
        self.floor_name = ""
        self.currency = 0
        self.dodge_ratio = 1.0
        self.body_font = load_font(24)
        self.small_font = load_font(18)
        self.minimap_panel_rect = pygame.Rect(0, 0, *MINIMAP_PANEL_SIZE)

    def sync(
        self,
        curr_hp,
        max_hp,
        current_floor,
        total_floors,
        floor_name,
        currency,
        dodge_ratio,
    ):
        self.health_bar.update(curr_hp, max_hp)
        self.current_floor = current_floor
        self.total_floors = total_floors
        self.floor_name = floor_name
        self.currency = currency
        self.dodge_ratio = dodge_ratio

    def get_minimap_panel_rect(self):
        self.minimap_panel_rect.topright = (
            self.game.GAME_W - MINIMAP_MARGIN,
            MINIMAP_TOP,
        )
        return self.minimap_panel_rect

    def get_minimap_map_rect(self):
        panel_rect = self.get_minimap_panel_rect()
        return pygame.Rect(
            panel_rect.left + MINIMAP_INNER_MARGIN,
            panel_rect.top + MINIMAP_INNER_MARGIN,
            panel_rect.width - MINIMAP_INNER_MARGIN * 2,
            panel_rect.height - MINIMAP_INNER_MARGIN * 2,
        )

    def get_minimap_transform(self, world, map_rect):
        rows = len(world.level.tiles)
        cols = len(world.level.tiles[0])
        scale = min(map_rect.width / cols, map_rect.height / rows)
        scaled_width = cols * scale
        scaled_height = rows * scale
        origin_x = map_rect.left + (map_rect.width - scaled_width) / 2
        origin_y = map_rect.top + (map_rect.height - scaled_height) / 2
        return scale, origin_x, origin_y

    def tile_to_map_rect(self, tile_x, tile_y, scale, origin_x, origin_y):
        left = origin_x + tile_x * scale
        top = origin_y + tile_y * scale
        right = origin_x + (tile_x + 1) * scale
        bottom = origin_y + (tile_y + 1) * scale
        return pygame.Rect(
            round(left),
            round(top),
            max(1, math.ceil(right - left)),
            max(1, math.ceil(bottom - top)),
        )

    def world_to_map_point(self, world_point, world, scale, origin_x, origin_y):
        world_x, world_y = world_point
        tile_size = world.level.tile_size
        return (
            round(origin_x + (world_x / tile_size) * scale),
            round(origin_y + (world_y / tile_size) * scale),
        )

    def draw_minimap_tiles(self, surface, world, scale, origin_x, origin_y):
        discovered_tiles = world.discovered_minimap_tiles
        visible_tiles = world.visible_minimap_tiles
        floor_value = world.level.FLOOR.value
        wall_value = world.level.WALL.value

        for tile_y, row in enumerate(world.level.tiles):
            for tile_x, tile in enumerate(row):
                tile_key = (tile_x, tile_y)
                if tile_key not in discovered_tiles:
                    continue

                is_visible = tile_key in visible_tiles
                if tile == floor_value:
                    color = (138, 148, 164) if is_visible else (74, 84, 98)
                elif tile == wall_value:
                    color = (86, 92, 104) if is_visible else (36, 40, 48)
                else:
                    continue

                pygame.draw.rect(
                    surface,
                    color,
                    self.tile_to_map_rect(tile_x, tile_y, scale, origin_x, origin_y),
                )

    def draw_minimap_rooms(self, surface, world, scale, origin_x, origin_y):
        if world.current_floor_definition.generator_type != "bsp":
            return

        overlay_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        for room_id, room in enumerate(world.rooms):
            if room_id not in world.discovered_room_ids:
                continue

            room_rect = pygame.Rect(
                round(origin_x + room[0] * scale),
                round(origin_y + room[1] * scale),
                max(1, round(room[2] * scale)),
                max(1, round(room[3] * scale)),
            )

            fill_color = None
            border_color = (88, 92, 104, 180)

            if room_id in world.cleared_room_ids:
                fill_color = (62, 116, 82, 95)
                border_color = (118, 200, 140, 220)
            elif room_id == world.current_room_id:
                fill_color = (164, 130, 72, 92)
                border_color = (246, 210, 144, 230)
            elif room_id == world.shop_room_id:
                border_color = (255, 182, 92, 210)
            elif room_id == world.floor_exit_room_id:
                border_color = (126, 210, 255, 210)
            elif room_id == world.boss_room_id:
                border_color = (255, 118, 138, 210)

            if fill_color is not None:
                pygame.draw.rect(
                    overlay_surface,
                    fill_color,
                    room_rect,
                    border_radius=3,
                )

            pygame.draw.rect(
                overlay_surface,
                border_color,
                room_rect,
                2,
                border_radius=3,
            )

        surface.blit(overlay_surface, (0, 0))

    def draw_minimap_marker(
        self,
        surface,
        world,
        world_point,
        color,
        scale,
        origin_x,
        origin_y,
        radius=None,
        require_discovery=True,
    ):
        if world_point is None:
            return
        if require_discovery and not world.is_minimap_point_discovered(world_point):
            return

        marker_radius = radius or max(3, int(scale * 0.55))
        pygame.draw.circle(
            surface,
            color,
            self.world_to_map_point(world_point, world, scale, origin_x, origin_y),
            marker_radius,
        )

    def render_minimap(self, surface, world):
        panel_rect = self.get_minimap_panel_rect()
        map_rect = self.get_minimap_map_rect()
        scale, origin_x, origin_y = self.get_minimap_transform(world, map_rect)

        draw_panel(surface, panel_rect, MINIMAP_PANEL_STYLE)
        pygame.draw.rect(surface, (8, 10, 14), map_rect, border_radius=9)
        self.draw_minimap_tiles(surface, world, scale, origin_x, origin_y)
        self.draw_minimap_rooms(surface, world, scale, origin_x, origin_y)

        if world.floor_exit is not None:
            self.draw_minimap_marker(
                surface,
                world,
                world.floor_exit.rect.center,
                (120, 214, 255),
                scale,
                origin_x,
                origin_y,
            )

        if world.shop_keeper is not None:
            self.draw_minimap_marker(
                surface,
                world,
                world.shop_keeper.rect.center,
                (255, 186, 92),
                scale,
                origin_x,
                origin_y,
            )

        boss_point = None
        if world.boss is not None:
            boss_point = world.boss.rect.center
        elif world.pending_boss_spawn is not None:
            boss_point = world.pending_boss_spawn.position

        if boss_point is not None:
            self.draw_minimap_marker(
                surface,
                world,
                boss_point,
                (255, 104, 132),
                scale,
                origin_x,
                origin_y,
            )

        self.draw_minimap_marker(
            surface,
            world,
            world.player.rect.center,
            (255, 248, 230),
            scale,
            origin_x,
            origin_y,
            radius=max(4, int(scale * 0.7)),
            require_discovery=False,
        )

    def render(self, surface, world=None):
        self.health_bar.render(surface)
        dodge_bar_rect = pygame.Rect(25, 105, 256, 12)
        dodge_fill_rect = dodge_bar_rect.copy()
        dodge_fill_rect.width = int(dodge_bar_rect.width * self.dodge_ratio)

        pygame.draw.rect(surface, (35, 35, 42), dodge_bar_rect, border_radius=6)
        if dodge_fill_rect.width > 0:
            pygame.draw.rect(surface, (120, 210, 255), dodge_fill_rect, border_radius=6)

        draw_text(
            surface,
            f"Этаж {self.current_floor}/{self.total_floors}: {self.floor_name}",
            (255, 255, 255),
            160,
            30,
            self.body_font,
            center=True,
        )
        draw_text(
            surface,
            "Shift - уворот",
            (180, 220, 255),
            150,
            135,
            self.small_font,
            center=True,
        )

        if world is not None:
            self.render_minimap(surface, world)

        minimap_panel_rect = self.get_minimap_panel_rect()
        draw_text(
            surface,
            f"Жар: {self.currency}",
            (255, 190, 80),
            minimap_panel_rect.centerx,
            minimap_panel_rect.bottom + 22,
            self.body_font,
            center=True,
        )
