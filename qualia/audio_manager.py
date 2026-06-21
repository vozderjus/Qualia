import os
import random
from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class MusicTrack:
    key: str
    filename: str
    volume_multiplier: float = 1.0
    loops: int = -1


MAIN_MENU_TRACK = MusicTrack(
    key="main_menu_theme",
    filename="main_menu_theme.mp3",
)


class AudioManager:
    def __init__(self, settings, audio_dir):
        self.settings = settings
        self.audio_dir = audio_dir
        self.audio_available = False
        self.current_music_key = None
        self.current_music_volume_multiplier = 1.0
        self.player_shot_sounds = []
        self.enemy_shot_sounds = {}
        self.enemy_hit_sound = None
        self.player_hit_sound = None
        self.pickup_sound = None

    def load(self):
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
        self.pickup_sound = self.load_sound("pickup_sound.mp3")
        self.enemy_shot_sounds = {
            "orange_eye_shot": self.load_sound("orange_eye_shot.mp3"),
            "shotgun_enemy_shot": self.load_sound("shotgun_enemy_shot.mp3"),
            "sniper_enemy_shot": self.load_sound("sniper_enemy_shot.mp3"),
            "heart_enemy_shot": self.load_sound("heart_enemy_shot.mp3"),
            "blue_eye_shot": self.load_sound("blue_eye_shot.mp3"),
        }
        self.apply_settings()

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

    def apply_settings(self):
        if not self.audio_available:
            return

        sfx_base_volume = self.settings.sfx_volume
        player_shot_volume = sfx_base_volume * 0.35
        enemy_shot_volume = sfx_base_volume * 0.32
        enemy_hit_volume = sfx_base_volume * 0.45
        player_hit_volume = sfx_base_volume * 0.55
        pickup_volume = sfx_base_volume * 0.4

        for sound in self.player_shot_sounds:
            sound.set_volume(player_shot_volume)

        for sound in self.enemy_shot_sounds.values():
            if sound is not None:
                sound.set_volume(enemy_shot_volume)

        if self.enemy_hit_sound is not None:
            self.enemy_hit_sound.set_volume(enemy_hit_volume)

        if self.player_hit_sound is not None:
            self.player_hit_sound.set_volume(player_hit_volume)

        if self.pickup_sound is not None:
            self.pickup_sound.set_volume(pickup_volume)

        try:
            pygame.mixer.music.set_volume(
                self.settings.master_volume * self.current_music_volume_multiplier
            )
        except pygame.error:
            return

    def play_music(self, track):
        if not self.audio_available or track is None:
            return

        if self.current_music_key == track.key and pygame.mixer.music.get_busy():
            self.current_music_volume_multiplier = track.volume_multiplier
            self.apply_settings()
            return

        try:
            pygame.mixer.music.load(os.path.join(self.audio_dir, track.filename))
            pygame.mixer.music.play(track.loops)
            self.current_music_key = track.key
            self.current_music_volume_multiplier = track.volume_multiplier
            self.apply_settings()
        except (pygame.error, FileNotFoundError):
            self.current_music_key = None

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

    def play_enemy_shot_sound(self, sound_key):
        if sound_key is None:
            return

        self.play_sound(self.enemy_shot_sounds.get(sound_key))

    def play_enemy_hit_sound(self):
        self.play_sound(self.enemy_hit_sound)

    def play_player_hit_sound(self):
        self.play_sound(self.player_hit_sound)

    def play_pickup_sound(self):
        self.play_sound(self.pickup_sound)
