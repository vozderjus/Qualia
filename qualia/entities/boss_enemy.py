import random

import pygame
from constants import BOSS_HP, BOSS_SIZE
from entities.basic_enemy import Enemy
from entities.boss_behaviors import build_boss_phase_configs


class BossEnemy(Enemy):
    def __init__(self, game, level, player, pos):
        base_image = pygame.image.load("images/boss.png").convert_alpha()
        image = pygame.transform.scale(base_image, (BOSS_SIZE, BOSS_SIZE))

        super().__init__(
            game=game,
            level=level,
            player=player,
            pos=pos,
            image=image,
            hp=BOSS_HP,
            speed=160,
            fire_cooldown=1.05,
            role="boss",
        )
        self.display_name = "Архон Пустоты"
        self.is_boss = True
        self.phase_configs = build_boss_phase_configs()
        self.phase_index = 0
        self.phase_label = self.phase_configs[0].label
        self.attack_cycle = ()
        self.attack_cycle_index = 0
        self.strafe_direction = random.choice((-1, 1))
        self.strafe_switch_interval = 1.35
        self.strafe_timer = self.strafe_switch_interval
        self.awareness_radius = max(self.level.pixel_width, self.level.pixel_height)
        self.spawn_duration = 0.9
        self.spawn_timer = self.spawn_duration
        self.heat_drop_range = (30, 45)
        self.apply_phase_settings(force=True)

    def get_hp_ratio(self):
        if self.max_hp <= 0:
            return 0.0

        return self.hp / self.max_hp

    def get_phase_config(self):
        hp_ratio = self.get_hp_ratio()
        for index, phase_config in enumerate(self.phase_configs):
            if hp_ratio >= phase_config.min_hp_ratio:
                return index, phase_config

        last_index = len(self.phase_configs) - 1
        return last_index, self.phase_configs[last_index]

    def apply_phase_settings(self, force=False):
        phase_index, phase_config = self.get_phase_config()

        if not force and phase_index == self.phase_index:
            return

        self.phase_index = phase_index
        self.phase = phase_config.phase_id
        self.phase_label = phase_config.label
        self.speed = phase_config.speed
        self.fire_cooldown = phase_config.fire_cooldown
        self.preferred_min_range = phase_config.preferred_min_range
        self.preferred_max_range = phase_config.preferred_max_range
        self.movement_behavior = phase_config.movement_behavior
        self.attack_cycle = phase_config.attack_cycle
        self.attack_cycle_index = 0
        self.strafe_timer = self.strafe_switch_interval
        self.strafe_direction = random.choice((-1, 1))

    def update_strafe_direction(self, delta_time):
        self.strafe_timer = max(0.0, self.strafe_timer - delta_time)
        if self.strafe_timer > 0.0:
            return

        self.strafe_timer = self.strafe_switch_interval
        self.strafe_direction *= -1

    def request_attack(self, context):
        if not self.attack_cycle:
            return None

        attack_behavior = self.attack_cycle[
            self.attack_cycle_index % len(self.attack_cycle)
        ]
        attack_data = attack_behavior.get_attack_data(self, context)

        if attack_data is not None:
            self.attack_cycle_index = (
                self.attack_cycle_index + 1
            ) % len(self.attack_cycle)

        return attack_data

    def get_phase_color(self):
        _, phase_config = self.get_phase_config()
        return phase_config.color

    def update(self, delta_time):
        if self.update_spawn_state(delta_time):
            return None

        self.apply_phase_settings()
        self.update_fire_timer(delta_time)
        self.update_strafe_direction(delta_time)

        context = self.build_context()
        move_vector = self.movement_behavior.get_movement_vector(self, context)
        self.move_with_collision(move_vector, delta_time)
        context = self.build_context()

        return self.request_attack(context)

    def render(self, display, camera=None):
        phase_color = self.get_phase_color()

        if camera is None:
            render_rect = self.rect
        else:
            render_rect = camera.apply_rect(self.rect)

        aura_radius = max(render_rect.width, render_rect.height)
        aura_surface = pygame.Surface(
            (aura_radius * 2, aura_radius * 2),
            pygame.SRCALPHA,
        )
        aura_alpha = 50 if self.is_spawning else 78
        pygame.draw.circle(
            aura_surface,
            (*phase_color, aura_alpha),
            (aura_radius, aura_radius),
            aura_radius,
        )
        aura_rect = aura_surface.get_rect(center=render_rect.center)
        display.blit(aura_surface, aura_rect)

        super().render(display, camera)

        if self.is_spawning:
            return

        ring_radius = max(render_rect.width, render_rect.height) // 2 + 8
        ring_width = max(2, render_rect.width // 18)
        pygame.draw.circle(
            display,
            phase_color,
            render_rect.center,
            ring_radius,
            ring_width,
        )
