import os

import pygame
from states.state import State
from states.pause_menu import PauseMenu

class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.player = Player(self.game)
    
    def update(self, delta_time, actions):
        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.player.update(delta_time, actions)

    
    def render(self, display):
        display.fill((0, 0, 0))
        text = self.game.draw_text(
            display,
            "Game state loaded successfully",
            (255, 255, 255),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2,
            40
        )
        self.player.render(display)

class Player():
    def __init__(self, game):
        self.game = game
        self.position_x, self.position_y = 200, 200
        self.current_frame, self.last_frame_update = 0, 0
        self.curr_image = pygame.image.load("images/main_character.png").convert_alpha()
        self.curr_image = pygame.transform.scale(self.curr_image, (200, 200))    
    def update(self, delta_time, actions):
        # получаем направление движения
        direction_x = actions['right'] - actions['left']
        direction_y = actions['down'] - actions['up']
        # обновление позиции
        self.position_x += 200 * delta_time * direction_x
        self.position_y += 200 * delta_time * direction_y
    
    def render(self, display):
        display.blit(self.curr_image, (self.position_x, self.position_y))