import os
import pygame
import code.constants as constants
from code.scenes.menu import MenuScene
from code.scenes.settings import SettingsScene
from code.uis import Button
pygame.init()
pygame.display.set_caption("Qualia")

display_surface = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))

main_menu = MenuScene()
settings = SettingsScene()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    action = main_menu.draw()
    if action == 'play':
        print('play')
    elif action == 'exit':
        running = False
    elif action == 'settings':
        settings.draw()

    pygame.display.update()


pygame.quit()