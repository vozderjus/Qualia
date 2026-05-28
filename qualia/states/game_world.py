import os

import pygame
from states.state import State
from states.pause_menu import PauseMenu
from world.level import Level
from constants import PLAYER_SIZE, PLAYER_SPEED

class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.level = Level()
        self.player = Player(self.game, self.level)

    def update(self, delta_time, actions):
        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.player.update(delta_time, actions)

    
    def render(self, display):
        display.fill((0, 0, 0))
        self.level.render(display)
        self.player.render(display)

class Player():
    def __init__(self, game, level):
        self.game = game
        self.position_x, self.position_y = 64, 64
        
        self.current_frame, self.last_frame_update = 0, 0
        self.curr_image = pygame.image.load("images/main_character.png").convert_alpha()
        self.curr_image = pygame.transform.scale(self.curr_image, (PLAYER_SIZE, PLAYER_SIZE))
        self.rect = self.curr_image.get_rect(topleft=(PLAYER_SIZE, PLAYER_SIZE))
        self.level = level

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

    def render(self, display):
        display.blit(self.curr_image, self.rect)