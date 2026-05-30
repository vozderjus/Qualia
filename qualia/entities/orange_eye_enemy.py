import pygame
from entities.basic_enemy import Enemy
from constants import ORANGE_EYE_HP, ORANGE_EYE_SPEED, ORANGE_EYE_COOLDOWN
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
    
    def update(self, delta_time):
        self.update_fire_timer(delta_time)
        
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