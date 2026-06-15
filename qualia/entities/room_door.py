import math

import pygame


class RoomDoor:
    def __init__(self, rect, orientation):
        self.rect = pygame.Rect(rect)
        self.orientation = orientation
        self.pulse_time = 0.0
        self.deploy_duration = 0.22
        self.deploy_timer = self.deploy_duration
        self.is_deploying = False

    def update(self, delta_time):
        self.pulse_time += delta_time
        if self.is_deploying:
            self.deploy_timer = max(0.0, self.deploy_timer - delta_time)
            if self.deploy_timer == 0.0:
                self.is_deploying = False

    def start_deploy(self):
        self.is_deploying = True
        self.deploy_timer = self.deploy_duration

    def get_deploy_progress(self):
        if self.deploy_duration <= 0:
            return 1.0

        if not self.is_deploying:
            return 1.0

        return 1.0 - (self.deploy_timer / self.deploy_duration)

    def get_visible_rect(self, target_rect):
        progress = self.get_deploy_progress()

        if progress >= 1.0:
            return target_rect

        if self.orientation == "top":
            visible_height = max(1, int(target_rect.height * progress))
            return pygame.Rect(
                target_rect.x,
                target_rect.bottom - visible_height,
                target_rect.width,
                visible_height,
            )

        if self.orientation == "bottom":
            visible_height = max(1, int(target_rect.height * progress))
            return pygame.Rect(
                target_rect.x,
                target_rect.y,
                target_rect.width,
                visible_height,
            )

        if self.orientation == "left":
            visible_width = max(1, int(target_rect.width * progress))
            return pygame.Rect(
                target_rect.right - visible_width,
                target_rect.y,
                visible_width,
                target_rect.height,
            )

        if self.orientation == "right":
            visible_width = max(1, int(target_rect.width * progress))
            return pygame.Rect(
                target_rect.x,
                target_rect.y,
                visible_width,
                target_rect.height,
            )

        return target_rect

    def render(self, display, camera=None):
        target_rect = self.rect if camera is None else camera.apply_rect(self.rect)
        target_rect = self.get_visible_rect(target_rect)
        pulse = (math.sin(self.pulse_time * 4.0) + 1.0) * 0.5

        outer_color = (115, 70, 30)
        inner_color = (
            210,
            int(140 + 70 * pulse),
            65,
        )

        pygame.draw.rect(display, outer_color, target_rect, border_radius=max(2, max(target_rect.width, target_rect.height) // 10))
        inner_rect = target_rect.inflate(
            -max(2, target_rect.width // 5),
            -max(2, target_rect.height // 5),
        )
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(
                display,
                inner_color,
                inner_rect,
                border_radius=max(2, min(inner_rect.width, inner_rect.height) // 6),
            )
