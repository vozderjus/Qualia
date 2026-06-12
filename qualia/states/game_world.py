import os

import pygame
from constants import CAMERA_ZOOM, PLAYER_BULLET_VELOCITY, PLAYER_FIRE_COOLDOWN, FLOOR_CONFIGS
from entities.bullet import Bullet
from entities.camera import Camera
from entities.level_exit import LevelExit
from entities.sniper_eye_enemy import SniperEye
from entities.orange_eye_enemy import OrangeEye
from entities.player import Player
from entities.shotgun_eye_enemy import ShotgunEye
from states.pause_menu import PauseMenu
from states.state import State
from world.bsp_generator import BSPGenerator
from world.level import Level

clock = pygame.time.Clock()

class Game_World(State):
    def __init__(self, game):
        # эээ основные импорты, создаие импорта и тп
        State.__init__(self, game)
        self.total_floors = len(FLOOR_CONFIGS)
        self.current_floor = 1
        self.level = None
        self.player = None
        self.rooms = []
        self.current_room_id = None
        self.camera = None

        # обработка пуль и их кулдауна
        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = PLAYER_FIRE_COOLDOWN
        
        # враги!
        self.enemies = []
        self.pending_enemy_spawns = []
        self.floor_exit = None
        self.floor_exit_room_id = None

        self.build_floor(self.current_floor)

    def get_floor_settings(self, floor_number):
        config_index = min(max(0, floor_number - 1), self.total_floors - 1)
        return FLOOR_CONFIGS[config_index]

    def center_camera_on_player(self):
        self.camera.x = self.player.rect.centerx - self.camera.visible_width() / 2
        self.camera.y = self.player.rect.centery - self.camera.visible_height() / 2
        self.camera.clamp(self.level.pixel_width, self.level.pixel_height)

    def build_floor(self, floor_number, player_hp=100):
        settings = self.get_floor_settings(floor_number)
        generated_level = BSPGenerator(
            settings["map_width"],
            settings["map_height"],
            max_depth=settings["max_depth"],
            enemy_count=settings["enemy_count"],
        ).generate()

        self.level = Level(generated_level.tiles)
        self.player = Player(self.game, self.level, generated_level.player_spawn)
        self.player.hp = player_hp
        self.rooms = generated_level.rooms
        self.current_room_id = None
        self.camera = Camera(self.game.GAME_W, self.game.GAME_H, CAMERA_ZOOM)
        self.center_camera_on_player()

        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = PLAYER_FIRE_COOLDOWN
        self.enemies = []
        self.pending_enemy_spawns = []

        for index, enemy_spawn in enumerate(generated_level.enemy_spawns):
            enemy_class = [OrangeEye, ShotgunEye, SniperEye][index % 3]
            self.pending_enemy_spawns.append(
                {
                    'room_id': enemy_spawn.room_id,
                    'position': enemy_spawn.position,
                    'enemy_class': enemy_class,
                }
            )

        if floor_number < self.total_floors and generated_level.exit_spawn is not None:
            self.floor_exit = LevelExit(generated_level.exit_spawn)
            self.floor_exit_room_id = generated_level.exit_room_id
        else:
            self.floor_exit = None
            self.floor_exit_room_id = None

    def advance_to_next_floor(self):
        if self.current_floor >= self.total_floors:
            return

        player_hp = self.player.hp
        self.current_floor += 1
        self.build_floor(self.current_floor, player_hp)
        self.game.actions['interact'] = False

    def get_room_world_rect(self, room):
        room_x, room_y, room_w, room_h = room
        return pygame.Rect(
            room_x * self.level.tile_size,
            room_y * self.level.tile_size,
            room_w * self.level.tile_size,
            room_h * self.level.tile_size,
        )

    def get_room_id_for_point(self, point):
        for room_id, room in enumerate(self.rooms):
            if self.get_room_world_rect(room).collidepoint(point):
                return room_id

        return None

    def spawn_room_enemies(self, room_id):
        if room_id is None:
            return

        for spawn_data in self.pending_enemy_spawns[:]:
            if spawn_data['room_id'] != room_id:
                continue

            enemy_class = spawn_data['enemy_class']
            enemy = enemy_class(
                self.game,
                self.level,
                self.player,
                spawn_data['position'],
            )
            enemy.room_id = room_id
            self.enemies.append(enemy)
            self.pending_enemy_spawns.remove(spawn_data)

    def update_floor_exit(self, delta_time, actions):
        if self.floor_exit is None:
            return False

        self.floor_exit.update(delta_time)

        if self.floor_exit.can_interact(self.player.rect) and actions['interact']:
            self.advance_to_next_floor()
            return True

        return False

    # ======== ВСЕ АПДЕЙТЫ ========
    def update(self, delta_time, actions):
        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
            return

        self.player.update(delta_time, actions)
        player_room_id = self.get_room_id_for_point(self.player.rect.center)
        if player_room_id != self.current_room_id:
            self.current_room_id = player_room_id
            self.spawn_room_enemies(player_room_id)

        self.time_since_shot += delta_time
        self.camera.smooth_follow(
            self.player.rect.centerx,
            self.player.rect.centery,
            speed=5,
            delta_time=delta_time
        )
        self.camera.clamp(self.level.pixel_width, self.level.pixel_height)

        if self.update_floor_exit(delta_time, actions):
            return

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

            level_rect = pygame.Rect(0, 0, self.level.pixel_width, self.level.pixel_height)
            if not level_rect.colliderect(bullet.rect):
                self.player_bullets.remove(bullet)
                continue

            if self.level.collides_with_wall(bullet.rect):
                self.player_bullets.remove(bullet)

    def update_enemies(self, delta_time):
        for enemy in self.enemies[:]:
            shot_data = enemy.update(delta_time)

            if shot_data is not None:
                for direction in shot_data['directions']:
                    self.spawn_enemy_bullet(
                        shot_data['origin'],
                        direction,
                        shot_data['speed'],
                    )

            if enemy.is_dead():
                self.enemies.remove(enemy)

    def update_enemy_bullets(self, delta_time):
        for bullet in self.enemies_bullets[:]:
            bullet.update(delta_time)

            level_rect = pygame.Rect(0, 0, self.level.pixel_width, self.level.pixel_height)
            if not level_rect.colliderect(bullet.rect):
                self.enemies_bullets.remove(bullet)
                continue

            if self.level.collides_with_wall(bullet.rect):
                self.enemies_bullets.remove(bullet)
    
    # ======== ВСЕ СПАВНЫ ========
    def spawn_player_bullet(self):
        # берем необходимые координаты
        spawn_point = self.player.get_shot_origin()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
        scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT

        # высчитываем экранные координаты мыши в мировые
        world_mouse = self.camera.screen_to_world(
            mouse_x,
            mouse_y,
            scale_x,
            scale_y,
        )

        # направление вектора стрельбы (для мыши)
        direction = pygame.Vector2(
            world_mouse[0] - spawn_point[0],
            world_mouse[1] - spawn_point[1],
        )

        # байпасс если вдруг длина вектора 0 (чтоб не упала нормализация)
        if direction.length_squared() == 0:
            return

        # применение всех метрик
        velocity = direction.normalize() * PLAYER_BULLET_VELOCITY
        new_bullet = Bullet(spawn_point, velocity)
        self.player_bullets.append(new_bullet)

    def spawn_enemy_bullet(self, origin, direction, speed):
        velocity = direction * speed
        bullet = Bullet(origin, velocity)
        self.enemies_bullets.append(bullet)

    # ======== ВЫЧИСЛЕНИЯ КОЛЛИЗИЙ ========
    def handle_player_to_enemy_collisions(self):
        for player_bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if not enemy.is_combat_ready():
                    continue

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
            enemy.render(display, self.camera)

    def render_player_bullets(self, display):
        for bullet in self.player_bullets:
            bullet.render(display, self.camera)

    def render_enemies_bullets(self, display):
        for bullet in self.enemies_bullets:
            bullet.render(display, self.camera)

    def render_floor_exit(self, display):
        if self.floor_exit is not None:
            self.floor_exit.render(display, self.camera)

    def render_hud(self, display):
        self.game.draw_text(
            display,
            f"Этаж {self.current_floor}/{self.total_floors}",
            (255, 255, 255),
            120,
            30,
            24,
        )

        if self.floor_exit is not None and self.floor_exit.can_interact(self.player.rect):
            self.game.draw_text(
                display,
                "SPACE - перейти на следующий этаж",
                (210, 240, 255),
                self.game.GAME_W / 2,
                self.game.GAME_H - 40,
                24,
            )
        elif self.current_floor == self.total_floors:
            self.game.draw_text(
                display,
                "Финальный этаж. Босс будет добавлен позже.",
                (255, 220, 160),
                self.game.GAME_W / 2,
                self.game.GAME_H - 40,
                24,
            )

    def render(self, display):
        display.fill((0, 0, 0))
        self.level.render(display, self.camera)
        self.render_floor_exit(display)

        self.player.render(display, self.camera)
        self.render_player_bullets(display)

        self.render_enemies(display)
        self.render_enemies_bullets(display)
        self.render_hud(display)
