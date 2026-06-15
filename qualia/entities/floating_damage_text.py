import pygame


class FloatingDamageText:
    def __init__(
        self,
        game,
        value,
        position,
        color,
        duration=0.6,
        rise_speed=42,
        size=22,
    ):
        self.game = game
        self.value = str(value)
        self.pos = pygame.Vector2(position)
        self.color = color
        self.duration = duration
        self.timer = duration
        self.rise_speed = rise_speed
        self.size = size

    def update(self, delta_time):
        self.timer = max(0.0, self.timer - delta_time)
        self.pos.y -= self.rise_speed * delta_time
        return self.timer > 0

    def render(self, display, camera=None):
        if camera is None:
            screen_x, screen_y = self.pos.x, self.pos.y
        else:
            screen_x, screen_y = camera.apply(self.pos.x, self.pos.y)

        self.game.draw_text(
            display,
            self.value,
            self.color,
            int(screen_x),
            int(screen_y),
            self.size,
        )
