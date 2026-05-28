import constants
import pygame
from uis import Button

BUTTONS = {
    "play": {
        "normal": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 - 152, 
                         pygame.image.load("images/play_b_ph.png").convert(), 1),
        "active": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 - 152, 
                         pygame.image.load("images/play_b_ph_active.png").convert(), 1)
    },
    "exit": {
        "normal": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 + 152, 
                         pygame.image.load("images/exit_b_ph.png").convert_alpha(), 1),
        "active": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 + 152, 
                         pygame.image.load("images/exit_b_ph_active.png").convert_alpha(), 1)
    },
    "settings": {
        "normal": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2, 
                         pygame.image.load("images/settings_b_ph.png").convert(), 1),
        "active": Button(constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2, 
                         pygame.image.load("images/settings_b_ph_active.png").convert(), 1)
    }
}

class MenuScene:
    def __init__(self, surface):
        self.surface = surface
        self.buttons = BUTTONS
        self.bg = pygame.image.load("images/main_menu_placeholder.png").convert()
        self.clicked = False
    
    def draw(self):
        action = ''
        self.surface.blit(self.bg, (0, 0))
        #check for collisions and clicks
        pos = pygame.mouse.get_pos()

        if self.buttons["play"]["normal"].rect.collidepoint(pos):
            self.buttons["play"]["active"].draw()
            if pygame.mouse.get_pressed()[0] and self.clicked == False:
                self.clicked = True
                action = 'play'
        else:
            self.buttons["play"]["normal"].draw()

        if self.buttons["exit"]["normal"].rect.collidepoint(pos):
            self.buttons["exit"]["active"].draw()
            if pygame.mouse.get_pressed()[0] and self.clicked == False:
                self.clicked = True
                action = 'exit'
        else:
            self.buttons["exit"]["normal"].draw()

        if self.buttons["settings"]["normal"].rect.collidepoint(pos):
            self.buttons["settings"]["active"].draw()
            if pygame.mouse.get_pressed()[0] and self.clicked == False:
                self.clicked = True
                action = 'settings'
        else:
            self.buttons["settings"]["normal"].draw()

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
