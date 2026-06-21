import random
from dataclasses import dataclass

import pygame
from constants import HEAT_DROP_RANGE


@dataclass(slots=True)
class EnemyContext:
    enemy_center: pygame.Vector2
    player_center: pygame.Vector2
    target_center: pygame.Vector2
    last_known_player_position: pygame.Vector2
    offset_to_target: pygame.Vector2
    distance_to_target: float
    direction_to_target: pygame.Vector2
    angle_to_target: float
    has_line_of_sight: bool
    has_detected_player: bool
    player_in_awareness_zone: bool
    can_shoot: bool
    in_preferred_range: bool
    preferred_min_range: float
    preferred_max_range: float

class Enemy():
    def __init__(self, game, level, player, pos, image, hp, speed, fire_cooldown, role):
        # базовые импорты
        self.game = game
        self.level = level
        self.player = player

        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.hp = hp
        self.max_hp = hp
        self.speed = speed

        self.fire_cooldown = fire_cooldown
        self.time_since_shot = fire_cooldown

        self.active = False
        self.phase = None
        self.phase_timer = 0
        self.attack_behavior = None
        self.movement_behavior = None

        self.preferred_min_range = 0
        self.preferred_max_range = 0
        self.contact_damage = 1
        self.room_id = None
        self.role = role
        self.spawn_center = pygame.Vector2(pos)
        self.awareness_radius = 420
        self.has_detected_player = False
        self.last_known_player_position = pygame.Vector2(self.rect.center)
        self.heat_drop_range = HEAT_DROP_RANGE
        self.is_spawning = True
        self.spawn_duration = 0.45
        self.spawn_timer = self.spawn_duration
        self.detection_telegraph_duration = 0.5
        self.detection_telegraph_timer = 0.0
        self.shot_sound_key = None

    # сбор контекста (позиция игрока, расстояние до игрока, линия взгляда, готовность к выстрелу)
    def build_context(self):
        enemy_center = pygame.Vector2(self.rect.center)
        player_center = pygame.Vector2(self.player.rect.center)
        was_detected_player = self.has_detected_player

        has_line_of_sight = self.level.has_line_of_sight(
            self.rect.center,
            self.player.rect.center,
        )
        player_in_awareness_zone = (
            player_center.distance_to(self.spawn_center) <= self.awareness_radius
        )

        if has_line_of_sight and player_in_awareness_zone:
            self.has_detected_player = True
            self.last_known_player_position = player_center.copy()
        elif not player_in_awareness_zone:
            self.has_detected_player = False

        if self.has_detected_player and not was_detected_player:
            self.detection_telegraph_timer = self.detection_telegraph_duration

        if self.has_detected_player:
            if has_line_of_sight:
                target_center = player_center
            else:
                target_center = self.last_known_player_position.copy()
        else:
            target_center = enemy_center.copy()

        offset_to_target = target_center - enemy_center
        distance_to_target = offset_to_target.length()

        if distance_to_target > 0:
            direction_to_target = offset_to_target.normalize()
            angle_to_target = direction_to_target.as_polar()[1]
        else:
            direction_to_target = pygame.Vector2()
            angle_to_target = 0.0

        can_shoot = self.can_shoot()

        in_preferred_range = (
            self.preferred_min_range <= distance_to_target <= self.preferred_max_range
        )

        return EnemyContext(
            enemy_center=enemy_center,
            player_center=player_center,
            target_center=target_center,
            last_known_player_position=self.last_known_player_position.copy(),
            offset_to_target=offset_to_target,
            distance_to_target=distance_to_target,
            direction_to_target=direction_to_target,
            angle_to_target=angle_to_target,
            has_line_of_sight=has_line_of_sight,
            has_detected_player=self.has_detected_player,
            player_in_awareness_zone=player_in_awareness_zone,
            can_shoot=can_shoot,
            in_preferred_range=in_preferred_range,
            preferred_min_range=self.preferred_min_range,
            preferred_max_range=self.preferred_max_range,
        )

    def move_with_collision(self, move_vector, delta_time):
        if move_vector.length_squared() > 1:
            move_vector = move_vector.normalize()

        move_x = move_vector.x * self.speed * delta_time
        move_y = move_vector.y * self.speed * delta_time

        next_rect_x = self.rect.copy()
        next_rect_x.x += int(move_x)
        if not self.level.collides_with_wall(next_rect_x):
            self.rect.x = next_rect_x.x

        next_rect_y = self.rect.copy()
        next_rect_y.y += int(move_y)
        if not self.level.collides_with_wall(next_rect_y):
            self.rect.y = next_rect_y.y

    def request_attack(self, context):
        if self.attack_behavior is None:
            return None

        return self.attack_behavior.get_attack_data(self, context)

    def update(self, delta_time):
        if self.update_spawn_state(delta_time):
            return None

        self.update_fire_timer(delta_time)

        context = self.build_context()
        if self.movement_behavior is not None:
            move_vector = self.movement_behavior.get_movement_vector(self, context)
            self.move_with_collision(move_vector, delta_time)
            context = self.build_context()

        return self.request_attack(context)

    def update_spawn_state(self, delta_time):
        if not self.is_spawning:
            return False

        self.spawn_timer = max(0.0, self.spawn_timer - delta_time)

        if self.spawn_timer == 0.0:
            self.is_spawning = False

        return self.is_spawning

    def is_combat_ready(self):
        return not self.is_spawning

    def render_spawn_effect(self, display, anchor_rect, scaled_image):
        if not self.is_spawning:
            display.blit(scaled_image, anchor_rect)
            return

        progress = 1.0 - (self.spawn_timer / self.spawn_duration)
        alpha = max(60, int(255 * progress))
        scale_factor = 0.55 + 0.45 * progress
        spawn_width = max(1, int(anchor_rect.width * scale_factor))
        spawn_height = max(1, int(anchor_rect.height * scale_factor))
        spawn_image = pygame.transform.scale(
            scaled_image,
            (spawn_width, spawn_height),
        )
        spawn_image.set_alpha(alpha)
        spawn_rect = spawn_image.get_rect(center=anchor_rect.center)

        ring_radius = max(anchor_rect.width, anchor_rect.height) * (0.35 + 0.45 * progress)
        ring_width = max(2, anchor_rect.width // 16)
        ring_color = (255, 210, 120)

        display.blit(spawn_image, spawn_rect)
        pygame.draw.circle(
            display,
            ring_color,
            anchor_rect.center,
            int(ring_radius),
            ring_width,
        )
        
    def update_fire_timer(self, delta_time):
        self.time_since_shot += delta_time

    def can_shoot(self):
        return self.time_since_shot >= self.fire_cooldown

    def reset_shot_timer(self):
        self.time_since_shot = 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def is_dead(self):
        return self.hp <= 0

    def roll_heat_drop(self):
        return random.randint(*self.heat_drop_range)

    def get_shot_origin(self):
        return self.rect.center

    def render(self, display, camera=None):
        if camera is None:
            self.render_spawn_effect(display, self.rect, self.image.copy())
            return

        screen_rect = camera.apply_rect(self.rect)
        scaled_image = pygame.transform.scale(self.image, screen_rect.size)
        self.render_spawn_effect(display, screen_rect, scaled_image)
