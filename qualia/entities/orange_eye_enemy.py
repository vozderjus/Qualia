import math

import pygame
from constants import ORANGE_EYE_COOLDOWN, ORANGE_EYE_HP, ORANGE_EYE_SPEED
from entities.basic_enemy import Enemy


class OrangeEye(Enemy):
    def __init__(self, game, level, player, pos):
        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=pygame.image.load("images/orange_eye_enemy.png").convert_alpha(),
            hp=ORANGE_EYE_HP,
            speed=ORANGE_EYE_SPEED,
            fire_cooldown=ORANGE_EYE_COOLDOWN,
        )
        
        self.orbit_radius = 80
        self.orbit_center = pygame.Vector2(self.rect.centerx - self.orbit_radius, self.rect.centery)
        self.orbit_angle = 0.0
    
    def update(self, delta_time):
        self.update_fire_timer(delta_time)
        
        angular_speed = self.speed / self.orbit_radius
        self.orbit_angle += angular_speed * delta_time
        
        new_centerx = self.orbit_center.x + math.cos(self.orbit_angle) * self.orbit_radius
        new_centery = self.orbit_center.y + math.sin(self.orbit_angle) * self.orbit_radius
        
        self.rect.center = (round(new_centerx), round(new_centery))

        direction = pygame.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery,
        )
        
        if direction.length_squared() > 0:
            direction = direction.normalize()
        
        if self.can_shoot() and direction.length_squared() > 0:
            self.reset_shot_timer()
            return {
                'origin': self.get_shot_origin(),
                'direction': direction,
            }

        return None