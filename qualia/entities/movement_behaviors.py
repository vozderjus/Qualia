import pygame


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


class IdleMovement:
    def get_movement_vector(self, enemy, context):
        return pygame.Vector2()
