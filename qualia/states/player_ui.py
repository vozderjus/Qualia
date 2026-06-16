import pygame

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

    def sync(self, curr_hp, max_hp, current_floor, total_floors, floor_name, currency):
        self.health_bar.update(curr_hp, max_hp)
        self.current_floor = current_floor
        self.total_floors = total_floors
        self.floor_name = floor_name
        self.currency = currency

    def render(self, surface):
        self.health_bar.render(surface)
        self.game.draw_text(
            surface,
            f"Этаж {self.current_floor}/{self.total_floors}: {self.floor_name}",
            (255, 255, 255),
            160,
            30,
            24,
        )
        self.game.draw_text(
            surface,
            f"Жар: {self.currency}",
            (255, 190, 80),
            self.game.GAME_W - 120,
            30,
            24,
        )
