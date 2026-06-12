import math

import pygame


class LevelExit:
    def __init__(self, center, size=56):
        self.center = pygame.Vector2(center)
        self.size = size
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = center
        self.pulse_time = 0.0

    def update(self, delta_time):
        self.pulse_time += delta_time

    def can_interact(self, player_rect):
        interact_rect = self.rect.inflate(24, 24)
        return interact_rect.colliderect(player_rect)

    def render(self, display, camera=None):
        pulse = math.sin(self.pulse_time * 3.0)

        if camera is None:
            center_x, center_y = self.rect.center
            zoom = 1.0
        else:
            center_x, center_y = camera.apply(*self.rect.center)
            zoom = camera.zoom

        base_radius = (self.size / 2) * zoom
        outer_radius = int(base_radius + pulse * 5 * zoom)
        inner_radius = int(base_radius * 0.55)
        ring_width = max(2, int(4 * zoom))

        pygame.draw.circle(
            display,
            (110, 220, 255),
            (int(center_x), int(center_y)),
            max(1, outer_radius),
            ring_width,
        )
        pygame.draw.circle(
            display,
            (45, 140, 255),
            (int(center_x), int(center_y)),
            max(1, outer_radius // 2),
            max(1, ring_width - 1),
        )
        pygame.draw.circle(
            display,
            (220, 245, 255),
            (int(center_x), int(center_y)),
            max(1, inner_radius),
        )
