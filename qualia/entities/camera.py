import pygame


class Camera:
    def __init__(self, screen_width, screen_height, zoom=1.0):
        self.x = 0.0
        self.y = 0.0
        self.width = screen_width
        self.height = screen_height
        self.zoom = zoom

    def visible_width(self):
        return self.width / self.zoom

    def visible_height(self):
        return self.height / self.zoom
    
    def smooth_follow(self, target_x, target_y, speed, delta_time):
        target_cx = target_x - self.visible_width() / 2
        target_cy = target_y - self.visible_height() / 2
        
        self.x += (target_cx - self.x) * speed * delta_time
        self.y += (target_cy - self.y) * speed * delta_time
    
    def apply(self, world_x, world_y):
        return (
            (world_x - self.x) * self.zoom,
            (world_y - self.y) * self.zoom,
        )

    def apply_rect(self, rect):
        screen_x, screen_y = self.apply(rect.x, rect.y)
        return pygame.Rect(
            int(screen_x),
            int(screen_y),
            max(1, int(rect.width * self.zoom)),
            max(1, int(rect.height * self.zoom)),
        )

    def screen_to_world(self, screen_x, screen_y, scale_x=1.0, scale_y=1.0):
        return (
            screen_x * scale_x / self.zoom + self.x,
            screen_y * scale_y / self.zoom + self.y,
        )
    
    def clamp(self, level_width, level_height):
        max_x = max(0, level_width - self.visible_width())
        max_y = max(0, level_height - self.visible_height())

        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))
    
    def get_visible_range(self, tile_size, cols, rows):
        start_col = max(0, int(self.x // tile_size))
        start_row = max(0, int(self.y // tile_size))

        end_col = min(cols, int((self.x + self.visible_width()) // tile_size) + 2)
        end_row = min(rows, int((self.y + self.visible_height()) // tile_size) + 2)
        
        return start_col, end_col, start_row, end_row
    
    def is_visible(self, obj_x, obj_y, obj_width, obj_height):
        return (obj_x + obj_width > self.x
                and obj_x < self.x + self.visible_width()
                and obj_y + obj_height > self.y
                and obj_y < self.y + self.visible_height())
