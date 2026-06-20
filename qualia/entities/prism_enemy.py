import pygame
from constants import SNIPER_EYE_COOLDOWN, SNIPER_EYE_HP, SNIPER_EYE_SPEED
from entities.attack_behaviors import SniperAttack
from entities.basic_enemy import Enemy
from entities.movement_behaviors import KeepDistanceMovement


class SniperEnemy(Enemy):
    def __init__(self, game, level, player, pos):
        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=pygame.image.load("images/prism_enemy.png").convert_alpha(),
            hp=SNIPER_EYE_HP,
            speed=SNIPER_EYE_SPEED,
            fire_cooldown=SNIPER_EYE_COOLDOWN,
            role='sniper'
        )
        self.movement_behavior = KeepDistanceMovement()
        self.attack_behavior = SniperAttack()
        self.preferred_min_range = 260
        self.preferred_max_range = 420
        self.phase = 'idle'
