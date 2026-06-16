import math

import pygame


class ShopKeeper:
    def __init__(self, game, center, room_id, trigger_radius=96):
        self.game = game
        self.center = pygame.Vector2(center)
        self.room_id = room_id
        self.trigger_radius = trigger_radius
        self.pulse_time = 0.0
        self.rect = pygame.Rect(0, 0, 52, 72)
        self.rect.center = center

    def update(self, delta_time):
        self.pulse_time += delta_time

    def can_trigger(self, player_rect):
        player_center = pygame.Vector2(player_rect.center)
        return player_center.distance_to(self.center) <= self.trigger_radius

    def render(self, display, camera=None):
        pulse = math.sin(self.pulse_time * 3.0)

        if camera is None:
            center_x, center_y = self.rect.center
            zoom = 1.0
        else:
            center_x, center_y = camera.apply(*self.rect.center)
            zoom = camera.zoom

        center_x = int(center_x)
        center_y = int(center_y)

        aura_radius = max(18, int((30 + pulse * 3) * zoom))
        body_width = max(16, int(28 * zoom))
        body_height = max(18, int(24 * zoom))
        stall_width = max(30, int(44 * zoom))
        stall_height = max(10, int(14 * zoom))
        canopy_width = max(34, int(54 * zoom))
        canopy_height = max(12, int(18 * zoom))
        head_radius = max(6, int(10 * zoom))

        stall_rect = pygame.Rect(0, 0, stall_width, stall_height)
        stall_rect.center = (center_x, center_y + max(10, int(14 * zoom)))

        body_rect = pygame.Rect(0, 0, body_width, body_height)
        body_rect.midbottom = (center_x, stall_rect.top + max(4, int(6 * zoom)))

        canopy_rect = pygame.Rect(0, 0, canopy_width, canopy_height)
        canopy_rect.midbottom = (center_x, body_rect.top - max(4, int(4 * zoom)))

        head_center = (center_x, body_rect.top + head_radius)
        sign_y = canopy_rect.top - max(18, int(24 * zoom))

        pygame.draw.circle(display, (255, 160, 70), (center_x, center_y), aura_radius, max(2, int(3 * zoom)))
        pygame.draw.rect(display, (105, 58, 30), stall_rect, border_radius=max(4, int(5 * zoom)))
        pygame.draw.rect(display, (168, 92, 52), body_rect, border_radius=max(4, int(5 * zoom)))
        pygame.draw.rect(display, (216, 126, 62), canopy_rect, border_radius=max(4, int(5 * zoom)))
        pygame.draw.circle(display, (255, 220, 170), head_center, head_radius)
        pygame.draw.circle(
            display,
            (255, 220, 110),
            (center_x, canopy_rect.top - max(6, int(10 * zoom))),
            max(4, int(6 * zoom)),
        )
        self.game.draw_text(
            display,
            "Лавка",
            (255, 225, 170),
            center_x,
            sign_y,
            18,
        )
