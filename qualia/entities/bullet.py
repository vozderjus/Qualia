import pygame
from constants import PLAYER_BULLET_SIZE


class Bullet():
    def __init__(self, pos, velocity):
        self.image = pygame.Surface((PLAYER_BULLET_SIZE, PLAYER_BULLET_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            (255, 255, 0), 
            (PLAYER_BULLET_SIZE / 2, PLAYER_BULLET_SIZE / 2), 
            PLAYER_BULLET_SIZE / 2
        )
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity)
        self.rect = self.image.get_rect(center=self.pos) # используется в рендере
    
    def update(self, delta_time):
        self.pos += self.vel * delta_time
        self.rect.center = (int(self.pos.x), int(self.pos.y))
    
    def render(self, display, camera=None):
        if camera is None:
            display.blit(self.image, self.rect)
            return

        screen_rect = camera.apply_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, screen_rect.size)
        display.blit(scaled_image, screen_rect)
