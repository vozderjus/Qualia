import pygame

from constants import SNIPER_EYE_COOLDOWN, SNIPER_EYE_HP, SNIPER_EYE_SPEED
from entities.basic_enemy import Enemy
from entities.enemies_behavior import KeepDistanceMovement, SniperAttack


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
