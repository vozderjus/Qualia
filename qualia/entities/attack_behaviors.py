from constants import (BLUE_BULLET_BOUNCE_RANGE, BLUE_BULLET_DAMAGE_RANGE,
                       BLUE_BULLET_SPEED_LOSS_PER_BOUNCE, BLUE_BULLET_VELOCITY,
                       ENEMY_BULLET_DAMAGE_RANGE, ENEMY_BULLET_VELOCITY,
                       HEART_BULLET_DAMAGE_RANGE, HEART_BULLET_VELOCITY,
                       SNIPER_BULLET_DAMAGE_RANGE, SNIPER_BULLET_VELOCITY)
from entities.attack_command import AttackCommand


class SingleShotAttack:
    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            return AttackCommand(
                origin=enemy.get_shot_origin(),
                directions=(context.direction_to_target,),
                speed=ENEMY_BULLET_VELOCITY,
                damage_range=ENEMY_BULLET_DAMAGE_RANGE,
                sound_key=enemy.shot_sound_key,
            )

        return None


class ConeShotAttack:
    def __init__(self, spread_angles=None):
        self.spread_angles = spread_angles or (-12, 0, 12)

    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            directions = tuple(
                context.direction_to_target.rotate(angle)
                for angle in self.spread_angles
            )
            return AttackCommand(
                origin=enemy.get_shot_origin(),
                directions=directions,
                speed=ENEMY_BULLET_VELOCITY,
                damage_range=ENEMY_BULLET_DAMAGE_RANGE,
                sound_key=enemy.shot_sound_key,
            )

        return None


class SniperAttack:
    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            return AttackCommand(
                origin=enemy.get_shot_origin(),
                directions=(context.direction_to_target,),
                speed=SNIPER_BULLET_VELOCITY,
                damage_range=SNIPER_BULLET_DAMAGE_RANGE,
                sound_key=enemy.shot_sound_key,
            )

        return None


class RicochetShotAttack:
    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            return AttackCommand(
                origin=enemy.get_shot_origin(),
                directions=(context.direction_to_target,),
                speed=BLUE_BULLET_VELOCITY,
                damage_range=BLUE_BULLET_DAMAGE_RANGE,
                sound_key=enemy.shot_sound_key,
                bounce_range=BLUE_BULLET_BOUNCE_RANGE,
                speed_loss_per_bounce=BLUE_BULLET_SPEED_LOSS_PER_BOUNCE,
            )

        return None


class HeartAttack:
    def __init__(self, spread_angles=None):
        self.spread_angles = spread_angles or (0, 45, 90, 135, 180, 225, 270, 315, 360)

    def get_attack_data(self, enemy, context):
        if (
            context.has_detected_player
            and context.can_shoot
            and context.has_line_of_sight
            and context.in_preferred_range
            and context.distance_to_target > 0
        ):
            enemy.reset_shot_timer()
            directions = tuple(
                context.direction_to_target.rotate(angle)
                for angle in self.spread_angles
            )
            return AttackCommand(
                origin=enemy.get_shot_origin(),
                directions=directions,
                speed=HEART_BULLET_VELOCITY,
                damage_range=HEART_BULLET_DAMAGE_RANGE,
                sound_key=enemy.shot_sound_key,
            )

        return None
