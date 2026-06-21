import random

import pygame
from constants import PLAYER_BULLET_VELOCITY
from entities.bullet import Bullet
from entities.floating_damage_text import FloatingDamageText
from entities.heat_pickup import HeatPickup


class CombatSystem:
    def __init__(self, world):
        self.world = world

    def reset(self):
        self.world.player_bullets = []
        self.world.enemies_bullets = []
        self.world.damage_texts = []
        self.world.heat_pickups = []
        self.world.time_since_shot = self.world.run_state.get_player_fire_cooldown()

    def spawn_damage_text(self, value, position, color):
        self.world.damage_texts.append(
            FloatingDamageText(self.world.game, value, position, color)
        )

    def update_damage_texts(self, delta_time):
        for damage_text in self.world.damage_texts[:]:
            if not damage_text.update(delta_time):
                self.world.damage_texts.remove(damage_text)

    def spawn_heat_drop(self, enemy):
        amount = enemy.roll_heat_drop()
        self.world.heat_pickups.append(HeatPickup(enemy.rect.center, amount))

    def remove_enemy(self, enemy):
        if enemy not in self.world.enemies:
            return

        self.world.enemies.remove(enemy)
        self.world.encounter_manager.track_removed_enemy(enemy)
        if enemy is self.world.boss:
            self.world.boss = None
            self.world.pending_boss_spawn = None
            self.world.pending_victory = True
            return

        self.spawn_heat_drop(enemy)

    def update_heat_pickups(self, delta_time):
        for heat_pickup in self.world.heat_pickups:
            heat_pickup.update(delta_time)

    def handle_heat_pickup_player_collisions(self):
        for heat_pickup in self.world.heat_pickups[:]:
            if not heat_pickup.can_collect(self.world.player.rect):
                continue

            self.world.run_state.add_currency(heat_pickup.amount)
            self.spawn_damage_text(
                f"+{heat_pickup.amount} жар",
                heat_pickup.rect.midtop,
                (255, 170, 70),
            )
            self.world.heat_pickups.remove(heat_pickup)

    def update_player_bullets(self, delta_time):
        for bullet in self.world.player_bullets[:]:
            bullet.update(delta_time)

            level_rect = pygame.Rect(0, 0, self.world.level.pixel_width, self.world.level.pixel_height)
            if not level_rect.colliderect(bullet.rect):
                self.world.player_bullets.remove(bullet)
                continue

            if self.world.level.collides_with_wall(bullet.rect):
                self.world.player_bullets.remove(bullet)

    def update_enemies(self, delta_time):
        for enemy in self.world.enemies[:]:
            if enemy.is_dead():
                self.remove_enemy(enemy)
                if self.world.pending_victory:
                    return
                continue

            attack_command = enemy.update(delta_time)

            if attack_command is not None:
                for direction in attack_command.directions:
                    self.spawn_enemy_bullet(
                        attack_command.origin,
                        direction,
                        attack_command.speed,
                        attack_command.damage_range,
                        attack_command.bounce_range,
                        attack_command.speed_loss_per_bounce,
                    )

            if enemy.is_dead():
                self.remove_enemy(enemy)
                if self.world.pending_victory:
                    return

    def update_enemy_bullets(self, delta_time):
        for bullet in self.world.enemies_bullets[:]:
            level_rect = pygame.Rect(0, 0, self.world.level.pixel_width, self.world.level.pixel_height)
            next_pos = bullet.pos.copy()
            hit_x = False
            hit_y = False

            next_x = bullet.pos.x + bullet.vel.x * delta_time
            next_rect_x = bullet.rect.copy()
            next_rect_x.center = (int(next_x), int(bullet.pos.y))
            if self.world.level.collides_with_wall(next_rect_x):
                hit_x = True
            else:
                next_pos.x = next_x

            next_y = bullet.pos.y + bullet.vel.y * delta_time
            next_rect_y = bullet.rect.copy()
            next_rect_y.center = (int(next_pos.x), int(next_y))
            if self.world.level.collides_with_wall(next_rect_y):
                hit_y = True
            else:
                next_pos.y = next_y

            bullet.pos = next_pos
            bullet.sync_rect()

            if hit_x or hit_y:
                if not bullet.bounce(hit_x, hit_y):
                    self.world.enemies_bullets.remove(bullet)
                    continue

                if bullet.vel.length_squared() > 0:
                    bullet.pos += bullet.vel.normalize() * 2
                    bullet.sync_rect()

            if not level_rect.colliderect(bullet.rect):
                self.world.enemies_bullets.remove(bullet)

    def spawn_player_bullet(self):
        spawn_point = self.world.player.get_shot_origin()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale_x = self.world.game.GAME_W / self.world.game.SCREEN_WIDTH
        scale_y = self.world.game.GAME_H / self.world.game.SCREEN_HEIGHT

        world_mouse = self.world.camera.screen_to_world(
            mouse_x,
            mouse_y,
            scale_x,
            scale_y,
        )

        direction = pygame.Vector2(
            world_mouse[0] - spawn_point[0],
            world_mouse[1] - spawn_point[1],
        )

        if direction.length_squared() == 0:
            return

        velocity = direction.normalize() * PLAYER_BULLET_VELOCITY
        damage = random.randint(*self.world.run_state.get_player_bullet_damage_range())
        self.world.player_bullets.append(Bullet(spawn_point, velocity, damage))
        self.world.game.play_random_player_shot_sound()

    def spawn_enemy_bullet(
        self,
        origin,
        direction,
        speed,
        damage_range,
        bounce_range=None,
        speed_loss_per_bounce=0,
    ):
        velocity = direction * speed
        damage = random.randint(*damage_range)
        remaining_bounces = 0
        if bounce_range is not None:
            remaining_bounces = random.randint(*bounce_range)

        self.world.enemies_bullets.append(
            Bullet(
                origin,
                velocity,
                damage,
                remaining_bounces=remaining_bounces,
                speed_loss_per_bounce=speed_loss_per_bounce,
            )
        )

    def handle_player_to_enemy_collisions(self):
        for player_bullet in self.world.player_bullets[:]:
            for enemy in self.world.enemies[:]:
                if not enemy.is_combat_ready():
                    continue

                if player_bullet.rect.colliderect(enemy.rect):
                    self.world.game.play_enemy_hit_sound()
                    self.spawn_damage_text(
                        player_bullet.damage,
                        enemy.rect.midtop,
                        (255, 235, 120),
                    )
                    enemy.take_damage(player_bullet.damage)
                    if enemy.is_dead():
                        self.remove_enemy(enemy)

                    if player_bullet in self.world.player_bullets:
                        self.world.player_bullets.remove(player_bullet)

                    if self.world.pending_victory:
                        return

                    break

    def handle_enemy_to_player_collisions(self):
        for enemy_bullet in self.world.enemies_bullets[:]:
            if enemy_bullet.rect.colliderect(self.world.player.rect):
                self.world.game.play_player_hit_sound()
                self.spawn_damage_text(
                    enemy_bullet.damage,
                    self.world.player.rect.midtop,
                    (255, 120, 120),
                )
                self.world.player.take_damage(enemy_bullet.damage)

                if enemy_bullet in self.world.enemies_bullets:
                    self.world.enemies_bullets.remove(enemy_bullet)

    def render_player_bullets(self, display):
        for bullet in self.world.player_bullets:
            bullet.render(display, self.world.camera)

    def render_enemy_bullets(self, display):
        for bullet in self.world.enemies_bullets:
            bullet.render(display, self.world.camera)

    def render_heat_pickups(self, display):
        for heat_pickup in self.world.heat_pickups:
            heat_pickup.render(display, self.world.camera)

    def render_damage_texts(self, display):
        for damage_text in self.world.damage_texts:
            damage_text.render(display, self.world.camera)
