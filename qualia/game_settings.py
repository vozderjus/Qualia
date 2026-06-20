from dataclasses import dataclass


@dataclass
class GameSettings:
    master_volume: float = 0.8
    sfx_volume: float = 0.8

    def set_master_volume(self, value):
        self.master_volume = max(0.0, min(1.0, value))

    def change_master_volume(self, delta):
        self.set_master_volume(self.master_volume + delta)

    def get_master_volume_percent(self):
        return int(round(self.master_volume * 100))

    def set_sfx_volume(self, value):
        self.sfx_volume = max(0.0, min(1.0, value))

    def change_sfx_volume(self, delta):
        self.set_sfx_volume(self.sfx_volume + delta)

    def get_sfx_volume_percent(self):
        return int(round(self.sfx_volume * 100))
