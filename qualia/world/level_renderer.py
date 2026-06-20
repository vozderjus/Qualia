import pygame


class LevelRenderer:
    def __init__(
        self,
        level,
        floor_tile_path="images/floor_tile1.png",
        wall_tile_path="images/wall_tile.png",
        floor_tint=None,
        wall_tint=None,
    ):
        self.level = level
        self.floor_tile = self.load_tinted_tile(floor_tile_path, floor_tint)
        self.wall_tile = self.load_tinted_tile(wall_tile_path, wall_tint)
        self._cached_zoom = None
        self._scaled_floor_tile = self.floor_tile
        self._scaled_wall_tile = self.wall_tile

    def load_tinted_tile(self, path, tint):
        tile = pygame.image.load(path).convert_alpha()

        if tint is None:
            return tile

        tinted_tile = tile.copy()
        tint_surface = pygame.Surface(tinted_tile.get_size(), pygame.SRCALPHA)
        tint_surface.fill((*tint, 255))
        tinted_tile.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_tile

    def update_scaled_tiles(self, zoom):
        if self._cached_zoom == zoom:
            return

        scaled_size = max(1, int(self.level.tile_size * zoom))
        self._scaled_floor_tile = pygame.transform.scale(
            self.floor_tile,
            (scaled_size, scaled_size),
        )
        self._scaled_wall_tile = pygame.transform.scale(
            self.wall_tile,
            (scaled_size, scaled_size),
        )
        self._cached_zoom = zoom

    def render(self, display, camera):
        self.update_scaled_tiles(camera.zoom)

        rows = len(self.level.tiles)
        cols = len(self.level.tiles[0])
        start_col, end_col, start_row, end_row = camera.get_visible_range(
            self.level.tile_size,
            cols,
            rows,
        )

        for row_index in range(start_row, end_row):
            for col_index in range(start_col, end_col):
                tile = self.level.tiles[row_index][col_index]
                world_x = col_index * self.level.tile_size
                world_y = row_index * self.level.tile_size
                screen_x, screen_y = camera.apply(world_x, world_y)

                if tile == self.level.FLOOR.value:
                    display.blit(
                        self._scaled_floor_tile,
                        (int(screen_x), int(screen_y)),
                    )
                elif tile == self.level.WALL.value:
                    display.blit(
                        self._scaled_wall_tile,
                        (int(screen_x), int(screen_y)),
                    )
