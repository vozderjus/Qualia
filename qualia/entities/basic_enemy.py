import pygame


class Enemy():
    def __init__(self, game, level, player, pos, image, hp, speed, fire_cooldown):
        # базовые импорты
        self.game = game
        self.level = level
        self.player = player

        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.hp = hp
        self.speed = speed

        self.fire_cooldown = fire_cooldown
        self.time_since_shot = fire_cooldown

    def update_fire_timer(self, delta_time):
        self.time_since_shot += delta_time

    def can_shoot(self):
        return self.time_since_shot >= self.fire_cooldown

    def reset_shot_timer(self):
        self.time_since_shot = 0

    def take_damage(self, amount):
        self.hp -= amount

    def is_dead(self):
        return self.hp <= 0

    def get_shot_origin(self):
        return self.rect.center

    def render(self, display):
        display.blit(self.image, self.rect)
