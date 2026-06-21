import pygame
from constants import ORANGE_EYE_COOLDOWN, ORANGE_EYE_SPEED, SHOTGUN_ENEMY_HP
from entities.attack_behaviors import ConeShotAttack
from entities.basic_enemy import Enemy
from entities.movement_behaviors import KeepDistanceMovement


class ShotgunEnemy(Enemy):
    def __init__(self, game, level, player, pos):
        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=pygame.image.load("images/teeth_enemy.png").convert_alpha(),
            hp=SHOTGUN_ENEMY_HP,
            speed=ORANGE_EYE_SPEED - 30,
            fire_cooldown=ORANGE_EYE_COOLDOWN + 0.35,
            role='burst'
        )
        self.movement_behavior = KeepDistanceMovement()
        self.attack_behavior = ConeShotAttack()
        self.preferred_min_range = 160
        self.preferred_max_range = 300
        self.phase = 'idle'
        self.shot_sound_key = "shotgun_enemy_shot"
