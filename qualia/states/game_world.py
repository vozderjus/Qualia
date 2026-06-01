import os

import pygame
from constants import ENEMY_BULLET_VELOCITY, PLAYER_BULLET_VELOCITY, PLAYER_FIRE_COOLDOWN
from entities.bullet import Bullet
from entities.orange_eye_enemy import OrangeEye
from entities.player import Player
from states.pause_menu import PauseMenu
from states.state import State
from world.level import Level
from world.bsp_generator import BSPGenerator

class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)
        generated_level = BSPGenerator(50, 40, max_depth=3, enemy_count=1).generate()
        self.level = Level(generated_level.tiles)
        self.player = Player(self.game, self.level, generated_level.player_spawn)
        
        # обработка пуль и их кулдауна
        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = PLAYER_FIRE_COOLDOWN
        
        # враги!
        self.enemies = [
            OrangeEye(self.game, self.level, self.player, spawn)
            for spawn in generated_level.enemy_spawns
        ]

    # ======== ВСЕ АПДЕЙТЫ ========
    def update(self, delta_time, actions):
        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
            return

        self.player.update(delta_time, actions)
        self.time_since_shot += delta_time

        if actions['fire'] and self.time_since_shot >= PLAYER_FIRE_COOLDOWN:
            self.spawn_player_bullet()
            self.time_since_shot = 0

        self.update_player_bullets(delta_time)
        self.update_enemies(delta_time)
        self.update_enemy_bullets(delta_time)

        self.handle_player_to_enemy_collisions()
        self.handle_enemy_to_player_collisions()

    def update_player_bullets(self, delta_time):
        for bullet in self.player_bullets[:]: # проходимся по копии списка 
            bullet.update(delta_time)

            if not self.game.game_canvas.get_rect().colliderect(bullet.rect):
                self.player_bullets.remove(bullet)
                continue

            if self.level.collides_with_wall(bullet.rect):
                self.player_bullets.remove(bullet)

    def update_enemies(self, delta_time):
        for enemy in self.enemies[:]:
            shot_data = enemy.update(delta_time)

            if shot_data is not None:
                self.spawn_enemy_bullet(
                    shot_data['origin'],
                    shot_data['direction'],
                )

            if enemy.is_dead():
                self.enemies.remove(enemy)

    def update_enemy_bullets(self, delta_time):
        for bullet in self.enemies_bullets[:]:
            bullet.update(delta_time)

            if not self.game.game_canvas.get_rect().colliderect(bullet.rect):
                self.enemies_bullets.remove(bullet)
                continue

            if self.level.collides_with_wall(bullet.rect):
                self.enemies_bullets.remove(bullet)
    
    # ======== ВСЕ СПАВНЫ ========
    def spawn_player_bullet(self):
        # берем необходимые координаты
        spawn_point = self.player.get_shot_origin()
        mouse_pos = pygame.mouse.get_pos()

        # направление вектора стрельбы (для мыши)
        direction = pygame.Vector2(
            mouse_pos[0] - spawn_point[0],
            mouse_pos[1] - spawn_point[1],
        )

        # байпасс если вдруг длина вектора 0 (чтоб не упала нормализация)
        if direction.length_squared() == 0:
            return

        # применение всех метрик
        velocity = direction.normalize() * PLAYER_BULLET_VELOCITY
        new_bullet = Bullet(spawn_point, velocity)
        self.player_bullets.append(new_bullet)

    def spawn_enemy_bullet(self, origin, direction):
        velocity = direction * ENEMY_BULLET_VELOCITY
        bullet = Bullet(origin, velocity)
        self.enemies_bullets.append(bullet)

    # ======== ВЫЧИСЛЕНИЯ КОЛЛИЗИЙ ========
    def handle_player_to_enemy_collisions(self):
        for player_bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if player_bullet.rect.colliderect(enemy.rect):
                    enemy.take_damage(1)

                    if player_bullet in self.player_bullets:
                        self.player_bullets.remove(player_bullet)
                    
                    break
    
    def handle_enemy_to_player_collisions(self):
        for enemy_bullet in self.enemies_bullets[:]:
            if enemy_bullet.rect.colliderect(self.player.rect):
                self.player.take_damage(1)

                if enemy_bullet in self.enemies_bullets:
                    self.enemies_bullets.remove(enemy_bullet)

    # ======== ВСЕ РЕНДЕРЫ ========
    def render_enemies(self, display):
        for enemy in self.enemies:
            enemy.render(display)

    def render_player_bullets(self, display):
        for bullet in self.player_bullets:
            bullet.render(display)

    def render_enemies_bullets(self, display):
        for bullet in self.enemies_bullets:
            bullet.render(display)

    def render(self, display):
        display.fill((0, 0, 0))
        self.level.render(display)

        self.player.render(display)
        self.render_player_bullets(display)

        self.render_enemies(display)
        self.render_enemies_bullets(display)
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        self.game.draw_text(self.game.game_canvas, f"x: {mouse_x}, y: {mouse_y}", (255, 255, 255), 700, 700, 20)
