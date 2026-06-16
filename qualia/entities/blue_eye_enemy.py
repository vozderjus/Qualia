import pygame
from constants import BLUE_EYE_COOLDOWN, BLUE_EYE_HP, BLUE_EYE_SPEED
from entities.basic_enemy import Enemy
from entities.enemies_behavior import ChaseMovement, RicochetShotAttack


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

    def update(self, delta_time):
        if self.update_spawn_state(delta_time):
            return None

        self.update_fire_timer(delta_time)

        context = self.build_context()
        move_vector = self.movement_behavior.get_movement_vector(self, context)
        self.move_with_collision(move_vector, delta_time)
        context = self.build_context()

        return self.request_attack(context)
