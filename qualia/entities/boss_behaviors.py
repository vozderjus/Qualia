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


class BossStationaryMovement:
    def get_movement_vector(self, enemy, context):
        return pygame.Vector2()


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


class BossKeepDistanceMovement:
    def get_movement_vector(self, enemy, context):
        if not context.has_detected_player or context.distance_to_target == 0:
            return pygame.Vector2()

        if not context.has_line_of_sight:
            return context.direction_to_target

        strafe = pygame.Vector2(
            -context.direction_to_target.y,
            context.direction_to_target.x,
        ) * enemy.strafe_direction

        if context.distance_to_target < enemy.preferred_min_range:
            return -context.direction_to_target + strafe * 0.25

        if context.distance_to_target > enemy.preferred_max_range:
            return context.direction_to_target * 0.65 + strafe * 0.2

        return strafe * 0.9


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
        sound_key=None,
    ):
        self.spread_angles = spread_angles
        self.speed = speed
        self.damage_range = damage_range
        self.require_line_of_sight = require_line_of_sight
        self.sound_key = sound_key

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
            sound_key=self.sound_key,
        )


class BossWaveFanAttack:
    def __init__(
        self,
        spread_angles,
        wave_offsets,
        speed,
        damage_range,
        require_line_of_sight=True,
        sound_key=None,
    ):
        self.spread_angles = spread_angles
        self.wave_offsets = wave_offsets
        self.speed = speed
        self.damage_range = damage_range
        self.require_line_of_sight = require_line_of_sight
        self.wave_index = 0
        self.sound_key = sound_key

    def get_attack_data(self, enemy, context):
        if not _can_attack(context, self.require_line_of_sight):
            return None

        if not context.in_preferred_range:
            return None

        enemy.reset_shot_timer()
        wave_offset = self.wave_offsets[self.wave_index % len(self.wave_offsets)]
        self.wave_index = (self.wave_index + 1) % len(self.wave_offsets)
        directions = [
            context.direction_to_target.rotate(wave_offset + angle)
            for angle in self.spread_angles
        ]
        return AttackCommand(
            origin=enemy.get_shot_origin(),
            directions=tuple(directions),
            speed=self.speed,
            damage_range=self.damage_range,
            sound_key=self.sound_key,
        )


class BossPerimeterWaveAttack:
    def __init__(
        self,
        projectile_count,
        speed,
        damage_range,
        wave_offsets,
        require_line_of_sight=True,
        sound_key=None,
    ):
        self.projectile_count = projectile_count
        self.speed = speed
        self.damage_range = damage_range
        self.wave_offsets = wave_offsets
        self.require_line_of_sight = require_line_of_sight
        self.wave_index = 0
        self.sound_key = sound_key

    def get_attack_data(self, enemy, context):
        if not _can_attack(context, self.require_line_of_sight):
            return None

        if not context.in_preferred_range:
            return None

        enemy.reset_shot_timer()
        wave_offset = self.wave_offsets[self.wave_index % len(self.wave_offsets)]
        self.wave_index = (self.wave_index + 1) % len(self.wave_offsets)
        base_angle = context.angle_to_target + wave_offset
        angle_step = 360 / self.projectile_count
        directions = [
            pygame.Vector2(1, 0).rotate(base_angle + index * angle_step)
            for index in range(self.projectile_count)
        ]
        return AttackCommand(
            origin=enemy.get_shot_origin(),
            directions=tuple(directions),
            speed=self.speed,
            damage_range=self.damage_range,
            sound_key=self.sound_key,
        )


class BossRicochetBurstAttack:
    def __init__(
        self,
        spread_angles,
        speed,
        damage_range,
        bounce_range,
        speed_loss_per_bounce,
        sound_key=None,
    ):
        self.spread_angles = spread_angles
        self.speed = speed
        self.damage_range = damage_range
        self.bounce_range = bounce_range
        self.speed_loss_per_bounce = speed_loss_per_bounce
        self.sound_key = sound_key

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
            sound_key=self.sound_key,
            bounce_range=self.bounce_range,
            speed_loss_per_bounce=self.speed_loss_per_bounce,
        )


class BossNovaAttack:
    def __init__(self, projectile_count, speed, damage_range, sound_key=None):
        self.projectile_count = projectile_count
        self.speed = speed
        self.damage_range = damage_range
        self.sound_key = sound_key

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
            sound_key=self.sound_key,
        )


def build_boss_phase_configs():
    return (
        BossPhaseConfig(
            phase_id="opening",
            label="Фаза I",
            min_hp_ratio=0.67,
            speed=0,
            fire_cooldown=0.5,
            preferred_min_range=0,
            preferred_max_range=9999,
            movement_behavior=BossStationaryMovement(),
            attack_cycle=(
                BossPerimeterWaveAttack(
                    projectile_count=18,
                    speed=112,
                    damage_range=(6, 8),
                    wave_offsets=(-42, -30, -18, -9, 0, 9, 18, 30, 42, 30, 18, 9, 0, -9, -18, -30),
                    sound_key="heart_enemy_shot",
                ),
            ),
            color=(110, 180, 255),
        ),
        BossPhaseConfig(
            phase_id="pressure",
            label="Фаза II",
            min_hp_ratio=0.34,
            speed=175,
            fire_cooldown=0.86,
            preferred_min_range=240,
            preferred_max_range=360,
            movement_behavior=BossKeepDistanceMovement(),
            attack_cycle=(
                BossRicochetBurstAttack(
                    spread_angles=(-16, 0, 16),
                    speed=275,
                    damage_range=(10, 14),
                    bounce_range=(1, 2),
                    speed_loss_per_bounce=60,
                    sound_key="blue_eye_shot",
                ),
                BossSpreadAttack(
                    spread_angles=(-32, -16, 0, 16, 32),
                    speed=300,
                    damage_range=(11, 14),
                    sound_key="shotgun_enemy_shot",
                ),
            ),
            color=(255, 170, 92),
        ),
        BossPhaseConfig(
            phase_id="rage",
            label="Фаза III",
            min_hp_ratio=0.0,
            speed=205,
            fire_cooldown=0.8,
            preferred_min_range=120,
            preferred_max_range=240,
            movement_behavior=BossRushMovement(),
            attack_cycle=(
                BossNovaAttack(
                    projectile_count=12,
                    speed=300,
                    damage_range=(8, 11),
                    sound_key="heart_enemy_shot",
                ),
                BossRicochetBurstAttack(
                    spread_angles=(-24, -8, 8, 24),
                    speed=410,
                    damage_range=(11, 15),
                    bounce_range=(2, 3),
                    speed_loss_per_bounce=75,
                    sound_key="blue_eye_shot",
                ),
                BossSpreadAttack(
                    spread_angles=(-40, -20, 0, 20, 40),
                    speed=380,
                    damage_range=(11, 14),
                    sound_key="shotgun_enemy_shot",
                ),
            ),
            color=(255, 96, 120),
        ),
    )
