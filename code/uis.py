import pygame
from code.constants import WINDOW_WIDTH, WINDOW_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class Button():
    def __init__(self, x, y, image, scale):
        width, height = image.get_width(), image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        # draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))

