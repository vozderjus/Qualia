import pygame


class ChaseMovement:
    def get_movement_vector(self, enemy, context):
        if context.distance_to_player == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_player

        if context.distance_to_player > enemy.preferred_max_range:
            return context.direction_to_player

        if context.distance_to_player < enemy.preferred_min_range:
            return -context.direction_to_player

        return pygame.Vector2()
