import math

import pygame
from constants import HEAT_PICKUP_SIZE


class HeatPickup:
    def __init__(self, center, amount, size=HEAT_PICKUP_SIZE):
        self.center = pygame.Vector2(center)
        self.amount = amount
        self.size = size
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = center
        self.pulse_time = 0.0

    def update(self, delta_time):
        self.pulse_time += delta_time

    def can_collect(self, player_rect):
        return self.rect.inflate(20, 20).colliderect(player_rect)

    def render(self, display, camera=None):
        pulse = math.sin(self.pulse_time * 4.0)

        if camera is None:
            center_x, center_y = self.rect.center
            zoom = 1.0
        else:
            center_x, center_y = camera.apply(*self.rect.center)
            zoom = camera.zoom

        outer_radius = max(4, int((self.size * 0.5 + pulse * 1.5) * zoom))
        inner_radius = max(2, int(self.size * 0.28 * zoom))
        glow_radius = max(outer_radius + 2, int(outer_radius * 1.45))
        ring_width = max(2, int(3 * zoom))
        center = (int(center_x), int(center_y))

        pygame.draw.circle(
            display,
            (255, 155, 55),
            center,
            glow_radius,
            max(1, ring_width - 1),
        )
        pygame.draw.circle(
            display,
            (255, 190, 80),
            center,
            outer_radius,
        )
        pygame.draw.circle(
            display,
            (255, 235, 155),
            center,
            inner_radius,
        )
