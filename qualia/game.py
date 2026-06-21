import os
import time

import pygame
from audio_manager import MAIN_MENU_TRACK, AudioManager
from constants import WINDOW_HEIGHT, WINDOW_WIDTH
from game_settings import GameSettings
from states.title import Title

pygame.init()
pygame.display.set_caption("Qualia")


KEY_ACTIONS = {
    pygame.K_a: "left",
    pygame.K_d: "right",
    pygame.K_w: "up",
    pygame.K_s: "down",
    pygame.K_LSHIFT: "dodge",
    pygame.K_RSHIFT: "dodge",
    pygame.K_SPACE: "interact",
    pygame.K_p: "pause",
    pygame.K_e: "inventory",
    pygame.K_RETURN: "start",
    pygame.K_F1: "debug_toggle",
}



class Game():
    def __init__(self):
        self.GAME_W, self.GAME_H = 1280, 720
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
        self.game_canvas = pygame.Surface((self.GAME_W, self.GAME_H))
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.running, self.playing = True, True
        self.actions = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "dodge": False,
            "interact": False,
            "pause": False,
            "inventory": False,
            "start": False,
            "fire": False,
            "debug_toggle": False,
        }
        self.dt, self.prev_time = 0, 0 #framerate independance
        self.state_stack = [] #game states management
        self.run_state = None
        self.settings = GameSettings()
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.playing, self.running = False, False
                    continue

                self.set_action_for_key(event.key, True)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.actions['fire'] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.playing, self.running = False, False
                    continue

                self.set_action_for_key(event.key, False)

            if event.type == pygame.MOUSEBUTTONUP:
                self.actions['fire'] = False

    def set_action_for_key(self, key, is_pressed):
        action = KEY_ACTIONS.get(key)
        if action is None:
            return

        self.actions[action] = is_pressed
    
    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)
        self.clock.tick(60)
    
    # рендер наших сцен
    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pygame.transform.scale(self.game_canvas, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0, 0))
        self.draw_text(self.screen, f"{int(self.clock.get_fps())}", (255, 255, 255), self.GAME_W / 2, self.GAME_H - 50, 20)
        pygame.display.flip()
    
    # вычисляем разницу между нынешним кадром и предыдущим кадром
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
    
    def load_assets(self):
        self.images_dir = os.path.join("images")
        self.audio_dir = os.path.join("audio")
        self.font = pygame.font.Font(os.path.join("font", "PixelifySans-VariableFont_wght.ttf"), 80)
        self.audio = AudioManager(self.settings, self.audio_dir)
        self.audio.load()

    def sync_audio_settings(self):
        self.audio.apply_settings()

    def play_music(self, track):
        self.audio.play_music(track)

    def ensure_main_menu_music(self):
        self.play_music(MAIN_MENU_TRACK)

    def stop_music(self):
        self.audio.stop_music()

    def fadeout_music(self):
        self.audio.fadeout_music()

    def play_random_player_shot_sound(self):
        self.audio.play_random_player_shot_sound()

    def play_enemy_shot_sound(self, sound_key):
        self.audio.play_enemy_shot_sound(sound_key)

    def play_enemy_hit_sound(self):
        self.audio.play_enemy_hit_sound()

    def play_player_hit_sound(self):
        self.audio.play_player_hit_sound()

    def play_pickup_sound(self):
        self.audio.play_pickup_sound()

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
