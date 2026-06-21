import pygame
from constants import (PLAYER_DODGE_COOLDOWN, PLAYER_DODGE_DURATION,
                       PLAYER_DODGE_SPEED, PLAYER_HITBOX_HEIGHT,
                       PLAYER_HITBOX_WIDTH, PLAYER_MAX_HP,
                       PLAYER_RENDER_OFFSET_Y, PLAYER_SIZE, PLAYER_SPEED)


class Player():
    def __init__(self, game, level, spawn_center=None):
        self.current_frame, self.last_frame_update = 0, 0

        # получаем изображение игрока
        self.curr_image = pygame.image.load("images/main_character.png").convert_alpha()
        self.curr_image = pygame.transform.scale(self.curr_image, (PLAYER_SIZE, PLAYER_SIZE))

        # работаем с rect
        self.rect = pygame.Rect(0, 0, PLAYER_HITBOX_WIDTH, PLAYER_HITBOX_HEIGHT)
        self.render_offset_y = PLAYER_RENDER_OFFSET_Y
        if spawn_center is not None:
            self.rect.center = spawn_center
        else:
            self.rect.center = (PLAYER_SIZE, PLAYER_SIZE)

        # доп импорты
        self.level = level
        self.game = game
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.last_move_direction = pygame.Vector2()
        self.dodge_direction = pygame.Vector2()
        self.dodge_duration = PLAYER_DODGE_DURATION
        self.dodge_duration_left = 0.0
        self.dodge_cooldown = PLAYER_DODGE_COOLDOWN
        self.dodge_cooldown_left = 0.0
        self.dodge_was_pressed = False

    def update(self, delta_time, actions):
        input_vector = self.get_input_vector(actions)
        if input_vector.length_squared() > 0:
            self.last_move_direction = input_vector.normalize()

        self.update_dodge_timers(delta_time)
        self.try_start_dodge(actions, input_vector)
        if self.is_dodging():
            self.move_with_collision(
                self.dodge_direction,
                PLAYER_DODGE_SPEED,
                delta_time,
            )
            self.dodge_duration_left = max(0.0, self.dodge_duration_left - delta_time)
            return

        self.move_with_collision(input_vector, PLAYER_SPEED, delta_time)

    def get_input_vector(self, actions):
        direction_x = actions['right'] - actions['left']
        direction_y = actions['down'] - actions['up']
        return pygame.Vector2(direction_x, direction_y)

    def update_dodge_timers(self, delta_time):
        self.dodge_cooldown_left = max(0.0, self.dodge_cooldown_left - delta_time)

    def try_start_dodge(self, actions, input_vector):
        is_pressed = actions['dodge']
        if is_pressed and not self.dodge_was_pressed and self.can_start_dodge(input_vector):
            if input_vector.length_squared() > 0:
                self.dodge_direction = input_vector.normalize()
            else:
                self.dodge_direction = self.last_move_direction.normalize()

            self.dodge_duration_left = self.dodge_duration
            self.dodge_cooldown_left = self.dodge_cooldown

        self.dodge_was_pressed = is_pressed

    def can_start_dodge(self, input_vector):
        if self.is_dodging() or self.dodge_cooldown_left > 0:
            return False

        if input_vector.length_squared() > 0:
            return True

        return self.last_move_direction.length_squared() > 0

    def is_dodging(self):
        return self.dodge_duration_left > 0

    def can_fire(self):
        return not self.is_dodging()

    def move_with_collision(self, move_vector, speed, delta_time):
        if move_vector.length_squared() > 1:
            move_vector = move_vector.normalize()

        move_x = move_vector.x * speed * delta_time
        move_y = move_vector.y * speed * delta_time

        next_rect_x = self.rect.copy()
        next_rect_x.x += int(move_x)
        if not self.level.collides_with_wall(next_rect_x):
            self.rect.x = next_rect_x.x

        next_rect_y = self.rect.copy()
        next_rect_y.y += int(move_y)
        if not self.level.collides_with_wall(next_rect_y):
            self.rect.y = next_rect_y.y

    def get_shot_origin(self):
        return self.rect.center

    def get_render_rect(self):
        return self.curr_image.get_rect(
            center=(self.rect.centerx, self.rect.centery - self.render_offset_y)
        )

    def take_damage(self, damage):
        if self.is_dodging():
            return False

        self.hp = max(0, self.hp - damage)
        return True

    def is_dead(self):
        return self.hp <= 0

    def dodge_cooldown_ratio(self):
        if self.dodge_cooldown <= 0:
            return 1.0

        if self.is_dodging():
            return 0.0

        return 1.0 - min(1.0, self.dodge_cooldown_left / self.dodge_cooldown)

    def render(self, display, camera=None):
        render_rect = self.get_render_rect()
        image = self.curr_image.copy()
        if self.is_dodging():
            image.set_alpha(180)

        if camera is None:
            display.blit(image, render_rect)
            return

        screen_rect = camera.apply_rect(render_rect)
        scaled_image = pygame.transform.scale(image, screen_rect.size)
        display.blit(scaled_image, screen_rect)
