import pygame
from constants import HEART_COOLDOWN, HEART_HP, HEART_SPEED
from entities.attack_behaviors import HeartAttack
from entities.basic_enemy import Enemy
from entities.movement_behaviors import IdleMovement


class HeartEnemy(Enemy):
    def __init__(self, game, level, player, pos):
        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=pygame.image.load("images/heart_enemy.png").convert_alpha(),
            hp=HEART_HP,
            speed=HEART_SPEED,
            fire_cooldown=HEART_COOLDOWN,
            role='burst',
        )
        self.movement_behavior = IdleMovement()
        self.attack_behavior = HeartAttack()
        self.preferred_min_range = 0
        self.preferred_max_range = 300
        self.phase = 'idle'
