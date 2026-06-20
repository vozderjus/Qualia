import os
import random
import time

import pygame
from constants import WINDOW_HEIGHT, WINDOW_WIDTH
from game_settings import GameSettings
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
        self.actions = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
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
        self.audio_available = False
        self.current_music_key = None
        self.current_music_volume_multiplier = 1.0
        self.player_shot_sounds = []
        self.enemy_hit_sound = None
        self.player_hit_sound = None
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
                if event.key == pygame.K_F1:
                    self.actions['debug_toggle'] = True

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
                if event.key == pygame.K_F1:
                    self.actions['debug_toggle'] = False


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
        self.load_sounds()

    def init_audio(self):
        if pygame.mixer.get_init() is not None:
            self.audio_available = True
            return True

        try:
            pygame.mixer.init()
        except pygame.error:
            self.audio_available = False
            return False

        self.audio_available = True
        return True

    def load_sound(self, filename):
        if not self.audio_available:
            return None

        try:
            return pygame.mixer.Sound(os.path.join(self.audio_dir, filename))
        except (pygame.error, FileNotFoundError):
            return None

    def load_sounds(self):
        if not self.init_audio():
            return

        self.player_shot_sounds = [
            sound
            for sound in (
                self.load_sound("floraphonic-fireball-whoosh-1-179125.mp3"),
                self.load_sound("floraphonic-fireball-whoosh-2-179126.mp3"),
                self.load_sound("floraphonic-fireball-whoosh-3-179127.mp3"),
            )
            if sound is not None
        ]
        self.enemy_hit_sound = self.load_sound("u_68csiaifb5-bulletimpact4-442720.mp3")
        self.player_hit_sound = self.load_sound("main character impact.mp3")
        self.apply_audio_settings()

    def apply_audio_settings(self):
        if not self.audio_available:
            return

        sfx_base_volume = self.settings.sfx_volume
        player_shot_volume = sfx_base_volume * 0.35
        enemy_hit_volume = sfx_base_volume * 0.45
        player_hit_volume = sfx_base_volume * 0.55

        for sound in self.player_shot_sounds:
            sound.set_volume(player_shot_volume)

        if self.enemy_hit_sound is not None:
            self.enemy_hit_sound.set_volume(enemy_hit_volume)

        if self.player_hit_sound is not None:
            self.player_hit_sound.set_volume(player_hit_volume)

        try:
            pygame.mixer.music.set_volume(
                self.settings.master_volume * self.current_music_volume_multiplier
            )
        except pygame.error:
            return

    def play_music(self, music_key, filename, loops=-1, volume_multiplier=1.0):
        if not self.audio_available:
            return

        if self.current_music_key == music_key and pygame.mixer.music.get_busy():
            self.current_music_volume_multiplier = volume_multiplier
            self.apply_audio_settings()
            return

        try:
            pygame.mixer.music.load(os.path.join(self.audio_dir, filename))
            pygame.mixer.music.play(loops)
            self.current_music_key = music_key
            self.current_music_volume_multiplier = volume_multiplier
            self.apply_audio_settings()
        except (pygame.error, FileNotFoundError):
            self.current_music_key = None

    def ensure_main_menu_music(self):
        self.play_music("main_menu_theme", "main_menu_theme.mp3", -1)

    def ensure_first_floor_music(self):
        self.play_music(
            "first_floor_theme",
            "first_floor_theme.mp3",
            -1,
            volume_multiplier=1/2,
        )

    def ensure_second_floor_music(self):
        self.play_music(
            "second_floor_theme",
            "second_floor_theme.mp3",
            -1,
            volume_multiplier=1/3,
        )

    def ensure_third_floor_music(self):
        self.play_music(
            "third_floor_theme",
            "third_floor_theme.mp3",
            -1,
            volume_multiplier=1/2,
        )
    def ensure_last_floor_music(self):
        self.play_music(
            "last_floor_theme",
            "last_floor_theme.mp3",
            -1,
            volume_multiplier=1/2,
        )


    def stop_music(self):
        if not self.audio_available:
            return

        try:
            pygame.mixer.music.stop()
        except pygame.error:
            return

        self.current_music_key = None
        self.current_music_volume_multiplier = 1.0

    def fadeout_music(self):
        if not self.audio_available:
            return

        try:
            fade_ms = int(250 + 1150 * self.settings.master_volume)
            pygame.mixer.music.fadeout(fade_ms)
        except pygame.error:
            return

        self.current_music_key = None

    def play_sound(self, sound):
        if sound is None:
            return

        try:
            sound.play()
        except pygame.error:
            return

    def play_random_player_shot_sound(self):
        if not self.player_shot_sounds:
            return

        self.play_sound(random.choice(self.player_shot_sounds))

    def play_enemy_hit_sound(self):
        self.play_sound(self.enemy_hit_sound)

    def play_player_hit_sound(self):
        self.play_sound(self.player_hit_sound)

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
