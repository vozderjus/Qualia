# === MADE BY AI ===

from dataclasses import dataclass

import pygame


@dataclass
class GameSettings:
    master_volume: float = 0.8

    def set_master_volume(self, value):
        self.master_volume = max(0.0, min(1.0, value))

    def change_master_volume(self, delta):
        self.set_master_volume(self.master_volume + delta)

    def get_master_volume_percent(self):
        return int(round(self.master_volume * 100))

    def apply_audio_stub(self):
        try:
            pygame.mixer.music.set_volume(self.master_volume)
        except pygame.error:
            return
