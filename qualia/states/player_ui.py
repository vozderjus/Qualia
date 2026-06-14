import pygame

class HealthBar():
    def __init__(self, curr_hp, max_hp):
        self.x = 25
        self.y = 65
        self.w = 256
        self.h = 32
        self.hp = curr_hp
        self.max_hp = max_hp
    
    def render(self, surface):
        if self.max_hp <= 0:
            ratio = 0
        else:
            ratio = max(0, min(1, self.hp / self.max_hp))
        
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))
