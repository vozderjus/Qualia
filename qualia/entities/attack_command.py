from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class AttackCommand:
    origin: tuple[int, int]
    directions: tuple[pygame.Vector2, ...]
    speed: float
    damage_range: tuple[int, int]
    sound_key: str | None = None
    bounce_range: tuple[int, int] | None = None
    speed_loss_per_bounce: int = 0
