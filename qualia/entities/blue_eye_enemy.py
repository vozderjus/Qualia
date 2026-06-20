import pygame
from constants import BLUE_EYE_COOLDOWN, BLUE_EYE_HP, BLUE_EYE_SPEED
from entities.attack_behaviors import RicochetShotAttack
from entities.basic_enemy import Enemy
from entities.movement_behaviors import ChaseMovement


class BlueEyeEnemy(Enemy):
    def __init__(self, game, level, player, pos):
        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=pygame.image.load("images/blue_eye_enemy.png").convert_alpha(),
            hp=BLUE_EYE_HP,
            speed=BLUE_EYE_SPEED,
            fire_cooldown=BLUE_EYE_COOLDOWN,
            role='burst',
        )
        self.movement_behavior = ChaseMovement()
        self.attack_behavior = RicochetShotAttack()
        self.preferred_min_range = 150
        self.preferred_max_range = 300
        self.phase = 'idle'
