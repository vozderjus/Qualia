import pygame
from constants import PLAYER_BULLET_SIZE


class Bullet():
    def __init__(
        self,
        pos,
        velocity,
        damage,
        remaining_bounces=0,
        speed_loss_per_bounce=0,
    ):
        self.image = pygame.Surface((PLAYER_BULLET_SIZE, PLAYER_BULLET_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            (255, 255, 0), 
            (PLAYER_BULLET_SIZE / 2, PLAYER_BULLET_SIZE / 2), 
            PLAYER_BULLET_SIZE / 2
        )
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(velocity)
        self.damage = damage
        self.remaining_bounces = remaining_bounces
        self.speed_loss_per_bounce = speed_loss_per_bounce
        self.rect = self.image.get_rect(center=self.pos) # используется в рендере
    
    def update(self, delta_time):
        self.pos += self.vel * delta_time
        self.sync_rect()

    def sync_rect(self):
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def bounce(self, hit_x=False, hit_y=False):
        if self.remaining_bounces <= 0:
            return False

        if hit_x:
            self.vel.x *= -1
        if hit_y:
            self.vel.y *= -1

        self.remaining_bounces -= 1

        if self.vel.length_squared() == 0:
            return False

        new_speed = max(0.0, self.vel.length() - self.speed_loss_per_bounce)
        if new_speed <= 0:
            return False

        self.vel.scale_to_length(new_speed)
        return True
    
    def render(self, display, camera=None):
        if camera is None:
            display.blit(self.image, self.rect)
            return

        screen_rect = camera.apply_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, screen_rect.size)
        display.blit(scaled_image, screen_rect)
