from dataclasses import dataclass

import pygame
from entities.attack_command import AttackCommand


@dataclass(frozen=True)
class BossPhaseConfig:
    phase_id: str
    label: str
    min_hp_ratio: float
    speed: int
    fire_cooldown: float
    preferred_min_range: float
    preferred_max_range: float
    movement_behavior: object
    attack_cycle: tuple[object, ...]
    color: tuple[int, int, int]


def _can_attack(context, require_line_of_sight=True):
    if not context.has_detected_player:
        return False

    if not context.can_shoot or context.distance_to_target == 0:
        return False

    if require_line_of_sight and not context.has_line_of_sight:
        return False

    return True


class BossStrafeMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player or context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        strafe = pygame.Vector2(
            -context.direction_to_target.y,
            context.direction_to_target.x,
        ) * enemy.strafe_direction
        move_vector = strafe

        if context.distance_to_target > enemy.preferred_max_range:
            move_vector += context.direction_to_target
        elif context.distance_to_target < enemy.preferred_min_range:
            move_vector -= context.direction_to_target * 0.75
        else:
            move_vector += context.direction_to_target * 0.15

        return move_vector


class BossAdvanceMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player or context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        strafe = pygame.Vector2(
            -context.direction_to_target.y,
            context.direction_to_target.x,
        ) * enemy.strafe_direction

        if context.distance_to_target > enemy.preferred_max_range:
            return context.direction_to_target + strafe * 0.35

        if context.distance_to_target < enemy.preferred_min_range:
            return -context.direction_to_target * 0.55 + strafe * 0.25

        return context.direction_to_target * 0.35 + strafe * 0.65


class BossRushMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player or context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        strafe = pygame.Vector2(
            -context.direction_to_target.y,
            context.direction_to_target.x,
        ) * enemy.strafe_direction

        if context.distance_to_target > enemy.preferred_max_range:
            return context.direction_to_target

        if context.distance_to_target > enemy.preferred_min_range:
            return context.direction_to_target + strafe * 0.35

        return strafe + context.direction_to_target * 0.25


class BossSpreadAttack:
    def __init__(
        self,
        spread_angles,
        speed,
        damage_range,
        require_line_of_sight=True,
    ):
        self.spread_angles = spread_angles
        self.speed = speed
        self.damage_range = damage_range
        self.require_line_of_sight = require_line_of_sight

    def get_attack_data(self, enemy, context):
        if not _can_attack(context, self.require_line_of_sight):
            return None

        if not context.in_preferred_range:
            return None

        enemy.reset_shot_timer()
        directions = [
            context.direction_to_target.rotate(angle)
            for angle in self.spread_angles
        ]
        return AttackCommand(
            origin=enemy.get_shot_origin(),
            directions=tuple(directions),
            speed=self.speed,
            damage_range=self.damage_range,
        )


class BossRicochetBurstAttack:
    def __init__(
        self,
        spread_angles,
        speed,
        damage_range,
        bounce_range,
        speed_loss_per_bounce,
    ):
        self.spread_angles = spread_angles
        self.speed = speed
        self.damage_range = damage_range
        self.bounce_range = bounce_range
        self.speed_loss_per_bounce = speed_loss_per_bounce

    def get_attack_data(self, enemy, context):
        if not _can_attack(context):
            return None

        if not context.in_preferred_range:
            return None

        enemy.reset_shot_timer()
        directions = [
            context.direction_to_target.rotate(angle)
            for angle in self.spread_angles
        ]
        return AttackCommand(
            origin=enemy.get_shot_origin(),
            directions=tuple(directions),
            speed=self.speed,
            damage_range=self.damage_range,
            bounce_range=self.bounce_range,
            speed_loss_per_bounce=self.speed_loss_per_bounce,
        )


class BossNovaAttack:
    def __init__(self, projectile_count, speed, damage_range):
        self.projectile_count = projectile_count
        self.speed = speed
        self.damage_range = damage_range

    def get_attack_data(self, enemy, context):
        if not _can_attack(context, require_line_of_sight=False):
            return None

        enemy.reset_shot_timer()
        base_angle = context.angle_to_target
        directions = [
            pygame.Vector2(1, 0).rotate(
                base_angle + index * (360 / self.projectile_count)
            )
            for index in range(self.projectile_count)
        ]
        return AttackCommand(
            origin=enemy.get_shot_origin(),
            directions=tuple(directions),
            speed=self.speed,
            damage_range=self.damage_range,
        )


def build_boss_phase_configs():
    return (
        BossPhaseConfig(
            phase_id="opening",
            label="Фаза I",
            min_hp_ratio=0.67,
            speed=160,
            fire_cooldown=1.05,
            preferred_min_range=220,
            preferred_max_range=380,
            movement_behavior=BossStrafeMovement(),
            attack_cycle=(
                BossSpreadAttack(
                    spread_angles=(-24, -12, 0, 12, 24),
                    speed=430,
                    damage_range=(10, 13),
                ),
                BossSpreadAttack(
                    spread_angles=(-8, 0, 8),
                    speed=520,
                    damage_range=(12, 15),
                ),
            ),
            color=(110, 180, 255),
        ),
        BossPhaseConfig(
            phase_id="pressure",
            label="Фаза II",
            min_hp_ratio=0.34,
            speed=185,
            fire_cooldown=0.86,
            preferred_min_range=180,
            preferred_max_range=320,
            movement_behavior=BossAdvanceMovement(),
            attack_cycle=(
                BossRicochetBurstAttack(
                    spread_angles=(-16, 0, 16),
                    speed=470,
                    damage_range=(10, 14),
                    bounce_range=(1, 2),
                    speed_loss_per_bounce=60,
                ),
                BossSpreadAttack(
                    spread_angles=(-32, -16, 0, 16, 32),
                    speed=450,
                    damage_range=(11, 14),
                ),
            ),
            color=(255, 170, 92),
        ),
        BossPhaseConfig(
            phase_id="rage",
            label="Фаза III",
            min_hp_ratio=0.0,
            speed=225,
            fire_cooldown=0.68,
            preferred_min_range=120,
            preferred_max_range=240,
            movement_behavior=BossRushMovement(),
            attack_cycle=(
                BossNovaAttack(
                    projectile_count=12,
                    speed=360,
                    damage_range=(8, 11),
                ),
                BossRicochetBurstAttack(
                    spread_angles=(-24, -8, 8, 24),
                    speed=520,
                    damage_range=(11, 15),
                    bounce_range=(2, 3),
                    speed_loss_per_bounce=75,
                ),
                BossSpreadAttack(
                    spread_angles=(-40, -20, 0, 20, 40),
                    speed=500,
                    damage_range=(11, 14),
                ),
            ),
            color=(255, 96, 120),
        ),
    )
