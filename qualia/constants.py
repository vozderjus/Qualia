import os
from uis import Button
import pygame

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# MENU_BUTTONS = {
#     "play": {
#         "normal": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 152, 
#                          pygame.image.load("images/play_b_ph.png").convert(), 1),
#         "active": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 152, 
#                          pygame.image.load("images/play_b_ph_active.png").convert(), 1)
#     },
#     "exit": {
#         "normal": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 152, 
#                          pygame.image.load("images/exit_b_ph.png").convert_alpha(), 1),
#         "active": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 152, 
#                          pygame.image.load("images/exit_b_ph_active.png").convert_alpha(), 1)
#     },
#     "settings": {
#         "normal": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 
#                          pygame.image.load("images/settings_b_ph.png").convert(), 1),
#         "active": Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, 
#                          pygame.image.load("images/settings_b_ph_active.png").convert(), 1)
#     }
# }

# main_menu_img = pygame.image.load("images/main_menu_placeholder.png")
