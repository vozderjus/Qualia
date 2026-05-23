import pygame
from constants import WINDOW_HEIGHT, WINDOW_WIDTH

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        # draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))
