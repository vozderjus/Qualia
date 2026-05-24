import pygame

display_surface = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))

class SettingsScene():
    def __init__(self):
        pass

    def draw(self):
        pygame.draw.rect(display_surface, (0, 0, 0), ((0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT)))