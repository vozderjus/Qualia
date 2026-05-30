import os

import pygame
from constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_BULLET_VELOCITY, PLAYER_FIRE_COOLDOWN
from states.pause_menu import PauseMenu
from states.state import State
from world.level import Level
from entities.player import Player
from entities.bullet import Bullet

class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.level = Level()
        self.player = Player(self.game, self.level)
        
        # обработка пуль и их кулдауна
        self.bullets = []
        self.time_since_shot = PLAYER_FIRE_COOLDOWN

    def update(self, delta_time, actions):
        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        
        self.player.update(delta_time, actions)
        self.time_since_shot += delta_time

        if actions['fire'] and self.time_since_shot >= PLAYER_FIRE_COOLDOWN:
            self.spawn_bullet()
            self.time_since_shot = 0

        self.update_bullets(delta_time)

    def spawn_bullet(self):
        # берем необходимые координаты
        spawn_point = self.player.rect.center
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
        self.bullets.append(new_bullet)
    
    def update_bullets(self, delta_time):
        for bullet in self.bullets[:]: # проходимся по копии списка 
            bullet.update(delta_time)

            if not self.game.game_canvas.get_rect().colliderect(bullet.rect):
                self.bullets.remove(bullet)
                continue

            if self.level.collides_with_wall(bullet.rect):
                self.bullets.remove(bullet)

    def render_bullets(self, display):
        for bullet in self.bullets:
            bullet.render(display)

    def render(self, display):
        display.fill((0, 0, 0))
        self.level.render(display)
        self.player.render(display)
        self.render_bullets(display)
