from dataclasses import dataclass, field

from constants import PLAYER_BULLET_DAMAGE_RANGE, PLAYER_FIRE_COOLDOWN, PLAYER_MAX_HP


@dataclass
class RunState:
    total_floors: int
    current_floor: int = 1
    player_hp: int = PLAYER_MAX_HP
    max_player_hp: int = PLAYER_MAX_HP
    player_damage_bonus: int = 0
    player_fire_cooldown_bonus: float = 0.0
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

    def add_currency(self, amount):
        self.currency = max(0, self.currency + amount)

    def spend_currency(self, amount):
        if amount <= 0:
            return True

        if self.currency < amount:
            return False

        self.currency -= amount
        return True

    def get_player_bullet_damage_range(self):
        base_min, base_max = PLAYER_BULLET_DAMAGE_RANGE
        return (
            base_min + self.player_damage_bonus,
            base_max + self.player_damage_bonus,
        )

    def get_player_fire_cooldown(self):
        return max(0.05, PLAYER_FIRE_COOLDOWN - self.player_fire_cooldown_bonus)

    def sync_from_player(self, player):
        self.set_player_hp(player.hp)

    def apply_to_player(self, player):
        player.max_hp = self.max_player_hp
        player.hp = min(self.player_hp, self.max_player_hp)

    def heal_to_full(self):
        self.player_hp = self.max_player_hp

    def purchase_shop_offer(self, offer):
        if not self.spend_currency(offer.cost):
            return False, "Недостаточно жара"

        if offer.effect_type == "max_hp":
            self.max_player_hp += int(offer.value)
            self.player_hp = min(self.max_player_hp, self.player_hp + int(offer.value))
            self.upgrades.append(f"{offer.name} +{int(offer.value)}")
            return True, f"Макс. HP +{int(offer.value)}"

        if offer.effect_type == "bullet_damage":
            self.player_damage_bonus += int(offer.value)
            self.upgrades.append(f"{offer.name} +{int(offer.value)}")
            return True, f"Урон +{int(offer.value)}"

        if offer.effect_type == "fire_rate":
            max_bonus = PLAYER_FIRE_COOLDOWN - 0.05
            remaining_bonus = max(0.0, max_bonus - self.player_fire_cooldown_bonus)
            applied_bonus = min(float(offer.value), remaining_bonus)

            if applied_bonus <= 0:
                self.currency += offer.cost
                return False, "Скорострельность уже на пределе"

            self.player_fire_cooldown_bonus += applied_bonus
            applied_ms = int(round(applied_bonus * 1000))
            self.upgrades.append(f"{offer.name} -{applied_ms}мс")
            return True, f"Кулдаун -{applied_ms} мс"

        self.currency += offer.cost
        return False, "Неизвестное улучшение"

    def heal_after_level(self):
        self.set_player_hp(self.player_hp + self.max_player_hp // 2)

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
