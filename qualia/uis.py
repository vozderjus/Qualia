import pygame


class Button:
    def __init__(self, x, y, image, scale):
        width, height = image.get_width(), image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale))
        )
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)