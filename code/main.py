import os
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, main_menu_img
from uis import Button
pygame.init()
pygame.display.set_caption("Qualia")

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
main_menu = main_menu_img.convert()

play_button = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 64, pygame.image.load("images/play_b_ph.png").convert())
exit_button = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 128, pygame.image.load("images/exit_b_ph.png").convert_alpha())
play_button_active = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 64, pygame.image.load("images/play_b_ph_active.png").convert())
exit_button_active = Button(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 128, pygame.image.load("images/exit_b_ph_active.png").convert_alpha())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    display_surface.blit(main_menu, (0, 0))

    if play_button.rect.collidepoint(mouse):
        play_button_active.draw()
    else:
        play_button.draw()

    if exit_button.rect.collidepoint(mouse):
        exit_button_active.draw()
    else:
        exit_button.draw()
    pygame.display.update()


pygame.quit()