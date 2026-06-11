import pygame

from constants import ENEMY_BULLET_VELOCITY, SNIPER_BULLET_VELOCITY


class ChaseMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player:
            return pygame.Vector2()

        if context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        if context.distance_to_target > enemy.preferred_max_range:
            return context.direction_to_target

        if context.distance_to_target < enemy.preferred_min_range:
            return -context.direction_to_target

        return pygame.Vector2()


class KeepDistanceMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player:
            return pygame.Vector2()

        if context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        if context.distance_to_target < enemy.preferred_min_range:
            return -context.direction_to_target

        if context.distance_to_target > enemy.preferred_max_range:
            return context.direction_to_target

        strafe_vector = pygame.Vector2(
            -context.direction_to_target.y,
            context.direction_to_target.x,
        )
        return strafe_vector


class SingleShotAttack:
    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and
            context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            return {
                'origin': enemy.get_shot_origin(),
                'directions': [context.direction_to_target],
                'speed': ENEMY_BULLET_VELOCITY,
            }

        return None


class ConeShotAttack:
    def __init__(self, spread_angles=None):
        self.spread_angles = spread_angles or (-12, 0, 12)

    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and
            context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            directions = [
                context.direction_to_target.rotate(angle)
                for angle in self.spread_angles
            ]
            return {
                'origin': enemy.get_shot_origin(),
                'directions': directions,
                'speed': ENEMY_BULLET_VELOCITY,
            }

        return None


class SniperAttack:
    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and
            context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            return {
                'origin': enemy.get_shot_origin(),
                'directions': [context.direction_to_target],
                'speed': SNIPER_BULLET_VELOCITY,
            }

        return None
