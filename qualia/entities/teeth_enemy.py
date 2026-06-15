import pygame

from constants import ORANGE_EYE_COOLDOWN, ORANGE_EYE_SPEED, SHOTGUN_ENEMY_HP
from entities.basic_enemy import Enemy
from entities.enemies_behavior import ConeShotAttack, KeepDistanceMovement


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

    def update(self, delta_time):
        if self.update_spawn_state(delta_time):
            return None

        self.update_fire_timer(delta_time)
        self.update_detection_telegraph(delta_time)

        context = self.build_context()
        move_vector = self.movement_behavior.get_movement_vector(self, context)
        self.move_with_collision(move_vector, delta_time)
        context = self.build_context()

        return self.request_attack(context)
