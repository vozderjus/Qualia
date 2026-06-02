import pygame
from constants import PLAYER_SIZE, PLAYER_SPEED


class Player():
    def __init__(self, game, level, spawn_center=None):
        # ==== TODO ====
        self.current_frame, self.last_frame_update = 0, 0
        # ==== TODO ====

        # получаем изображение игрока
        self.curr_image = pygame.image.load("images/main_character.png").convert_alpha()
        self.curr_image = pygame.transform.scale(self.curr_image, (PLAYER_SIZE, PLAYER_SIZE))

        # работаем с rect
        self.rect = self.curr_image.get_rect(topleft=(PLAYER_SIZE, PLAYER_SIZE))
        if spawn_center is not None:
            self.rect.center = spawn_center

        # доп импорты
        self.level = level
        self.game = game
        self.hp = 100

    def update(self, delta_time, actions):
        direction_x = actions['right'] - actions['left']
        direction_y = actions['down'] - actions['up']

        # смотрим следующий шаг
        speed = PLAYER_SPEED
        move_x = speed * delta_time * direction_x
        move_y = speed * delta_time * direction_y

        # коллизии по x
        next_rect_x = self.rect.copy()
        next_rect_x.x += int(move_x)

        if not self.level.collides_with_wall(next_rect_x):
            self.rect.x = next_rect_x.x

        # коллизии по y
        next_rect_y = self.rect.copy()
        next_rect_y.y += int(move_y)
        
        if not self.level.collides_with_wall(next_rect_y):
            self.rect.y = next_rect_y.y

    def get_shot_origin(self):
        return self.rect.center

    def take_damage(self, damage):
        self.hp -= damage

    def is_dead(self):
        return self.hp <= 0

    def render(self, display, camera=None):
        if camera is None:
            display.blit(self.curr_image, self.rect)
            return

        screen_rect = camera.apply_rect(self.rect)
        scaled_image = pygame.transform.scale(self.curr_image, screen_rect.size)
        display.blit(scaled_image, screen_rect)
