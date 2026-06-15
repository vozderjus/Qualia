from dataclasses import dataclass, field

from constants import PLAYER_MAX_HP


@dataclass
class RunState:
    total_floors: int
    current_floor: int = 1
    player_hp: int = PLAYER_MAX_HP
    max_player_hp: int = PLAYER_MAX_HP
    currency: int = 0
    keys: int = 0
    upgrades: list[str] = field(default_factory=list)
    cleared_floors: list[int] = field(default_factory=list)

    @classmethod
    def new_run(cls, total_floors, starting_hp=PLAYER_MAX_HP):
        return cls(
            total_floors=total_floors,
            current_floor=1,
            player_hp=starting_hp,
            max_player_hp=starting_hp,
        )

    def set_player_hp(self, hp):
        self.player_hp = max(0, min(hp, self.max_player_hp))

    def sync_from_player(self, player):
        self.set_player_hp(player.hp)

    def apply_to_player(self, player):
        player.hp = self.player_hp

    def heal_after_level(self):
        self.player_hp = self.player_hp + self.max_player_hp // 2

    def mark_floor_cleared(self):
        if self.current_floor not in self.cleared_floors:
            self.cleared_floors.append(self.current_floor)

    def can_advance_floor(self):
        return self.current_floor < self.total_floors

    def advance_floor(self):
        if not self.can_advance_floor():
            return False

        self.mark_floor_cleared()
        self.heal_after_level()
        self.current_floor += 1
        return True

    def is_final_floor(self):
        return self.current_floor >= self.total_floors
