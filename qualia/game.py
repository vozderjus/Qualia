import os
import time

import pygame
from constants import WINDOW_HEIGHT, WINDOW_WIDTH
from states.title import Title

pygame.init()
pygame.display.set_caption("Qualia")



class Game():
    def __init__(self):
        self.GAME_W, self.GAME_H = 1280, 720
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
        self.game_canvas = pygame.Surface((self.GAME_W, self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.running, self.playing = True, True
        self.actions = {"left": False, "right": False, "up": False, "down": False, "interact": False, "pause": False, "inventory": False, "start": False, "fire": False}
        self.dt, self.prev_time = 0, 0 #framerate independance
        self.state_stack = [] #game states management
        self.clock = pygame.time.Clock()
        self.load_assets()
        self.load_states()

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing, self.running = False, False
            
            # ввод с клавиатуры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing, self.running = False, False
                if event.key == pygame.K_a: # влево
                    self.actions['left'] = True
                if event.key == pygame.K_d: # вправо
                    self.actions['right'] = True
                if event.key == pygame.K_w: # вверх
                    self.actions['up'] = True
                if event.key == pygame.K_s: # вниз
                    self.actions['down'] = True
                if event.key == pygame.K_SPACE: # взаимодействие
                    self.actions['interact'] = True
                if event.key == pygame.K_p: # пауза
                    self.actions['pause'] = True
                if event.key == pygame.K_e: # инвентарь
                    self.actions['inventory'] = True
                if event.key == pygame.K_RETURN: # enter - начать игру
                    self.actions['start'] = True

            if event.type == pygame.MOUSEBUTTONDOWN: # включение огня
                self.actions['fire'] = True

            # обработка конца ввода
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.playing, self.running = False, False
                if event.key == pygame.K_a: # влево
                    self.actions['left'] = False
                if event.key == pygame.K_d: # вправо
                    self.actions['right'] = False
                if event.key == pygame.K_w: # вверх
                    self.actions['up'] = False
                if event.key == pygame.K_s: # вниз
                    self.actions['down'] = False
                if event.key == pygame.K_SPACE: # взаимодействие
                    self.actions['interact'] = False
                if event.key == pygame.K_p: # пауза
                    self.actions['pause'] = False
                if event.key == pygame.K_e: # инвентарь
                    self.actions['inventory'] = False
                if event.key == pygame.K_RETURN: # enter - начать игру
                    self.actions['start'] = False


            if event.type == pygame.MOUSEBUTTONUP: # отключение огня
                self.actions['fire'] = False
    
    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)
        self.clock.tick(60)
    
    # рендер наших сцен
    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))
        self.draw_text(self.screen, f"{int(self.clock.get_fps())}", (255, 255, 255), self.GAME_W / 2, self.GAME_H - 50, 20)
        pygame.display.flip()
    
    # вычисляем разницу между нынешним кадром и предыдущим кадром, чтобы 
    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now
    
    # рендер текста
    def draw_text(self, surface, text, color, x, y, size=None):
        font = self.font
        if size is not None:
            font = pygame.font.Font(os.path.join("font", "PixelifySans-VariableFont_wght.ttf"), size)


        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))    
        surface.blit(text_surface, text_rect)
    
    # подгружаем все необходимые ассеты
    def load_assets(self):
        # указатели на директории
        self.images_dir = os.path.join("images")
        self.audio_dir = os.path.join("audio")
        self.font = pygame.font.Font(os.path.join("font", "PixelifySans-VariableFont_wght.ttf"), 80)
    
    # основной стэк где будут подгружаться все состояния
    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False

if __name__ == '__main__':
    g = Game()
    while g.running:
        g.game_loop()
