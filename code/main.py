import os
import pygame
import constants

pygame.init()
pygame.display.set_caption("Qualia")

display_surface = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
main_menu = constants.main_menu_img.convert()

play_button = pygame.image.load("images/play_b_ph.png").convert()
play_button = pygame.transform.scale(play_button, (256, 128))
play_button_rect = play_button.get_rect(center = (constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 - 64))

exit_button = pygame.image.load("images/exit_b_ph.png").convert_alpha()
exit_button = pygame.transform.scale(exit_button, (256, 128))
exit_button_rect = exit_button.get_rect(center = (constants.WINDOW_WIDTH / 2, constants.WINDOW_HEIGHT / 2 + 128))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    display_surface.blit(main_menu, (0, 0))
    main_menu.blit(play_button, play_button_rect)
    main_menu.blit(exit_button, exit_button_rect)
    pygame.display.update()

pygame.quit()