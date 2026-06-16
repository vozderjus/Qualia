import random

import pygame
from constants import (
    CAMERA_ZOOM,
    PLAYER_BULLET_VELOCITY,
)
from entities.bullet import Bullet
from entities.camera import Camera
from entities.floating_damage_text import FloatingDamageText
from entities.heat_pickup import HeatPickup
from entities.level_exit import LevelExit
from entities.player import Player
from entities.room_door import RoomDoor
from entities.shop_keeper import ShopKeeper
from run_state import RunState
from shop_content import SHOP_REROLL_COST, roll_shop_offer, roll_shop_offers
from states.debug_hud import DebugHUD
from states.game_over import GameOver
from states.pause_menu import PauseMenu
from states.shop_menu import ShopMenu
from states.state import State
from world.bsp_generator import BSPGenerator
from world.floor_definitions import FLOOR_DEFINITIONS
from world.level import Level
from states.player_ui import PlayerUI

clock = pygame.time.Clock()

class Game_World(State):
    def __init__(self, game, run_state=None):
        # эээ основные импорты, создаие импорта и тп
        State.__init__(self, game)
        self.floor_definitions = FLOOR_DEFINITIONS
        self.total_floors = len(self.floor_definitions)
        self.run_state = run_state or RunState.new_run(self.total_floors)
        self.game.run_state = self.run_state
        self.current_floor = self.run_state.current_floor
        self.current_floor_definition = None
        self.level = None
        self.player = None
        self.rooms = []
        self.current_room_id = None
        self.camera = None

        # обработка пуль и их кулдауна
        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = self.run_state.get_player_fire_cooldown()
        
        # враги!
        self.enemies = []
        self.pending_enemy_spawns = []
        self.floor_exit = None
        self.floor_exit_room_id = None
        self.locked_room_id = None
        self.pending_lock_room_id = None
        self.active_room_doors = []
        self.pending_room_doors = []
        self.cleared_room_ids = set()
        self.player_ui = None
        self.damage_texts = []
        self.heat_pickups = []
        self.shop_room_id = None
        self.shop_keeper = None
        self.shop_trigger_armed = True
        self.shop_offers = []
        self.debug_hud = DebugHUD(self.game, self)

        self.build_floor(self.run_state.current_floor)

    def get_floor_definition(self, floor_number):
        definition_index = min(max(0, floor_number - 1), self.total_floors - 1)
        return self.floor_definitions[definition_index]

    def center_camera_on_player(self):
        self.camera.x = self.player.rect.centerx - self.camera.visible_width() / 2
        self.camera.y = self.player.rect.centery - self.camera.visible_height() / 2
        self.camera.clamp(self.level.pixel_width, self.level.pixel_height)

    def build_floor(self, floor_number):
        floor_definition = self.get_floor_definition(floor_number)
        self.current_floor_definition = floor_definition
        generated_level = BSPGenerator(
            floor_definition.map_width,
            floor_definition.map_height,
            max_depth=floor_definition.max_depth,
            enemy_count=floor_definition.enemy_count,
            has_shop=floor_definition.has_shop,
        ).generate()

        self.level = Level(
            generated_level.tiles,
            floor_tile_path=floor_definition.floor_tile_path,
            wall_tile_path=floor_definition.wall_tile_path,
            floor_tint=floor_definition.floor_tint,
            wall_tint=floor_definition.wall_tint,
        )
        self.player = Player(self.game, self.level, generated_level.player_spawn)
        self.run_state.apply_to_player(self.player)
        self.player_ui = PlayerUI(self.game, self.player.hp, self.run_state.max_player_hp)
        self.rooms = generated_level.rooms
        self.current_room_id = None
        self.camera = Camera(self.game.GAME_W, self.game.GAME_H, CAMERA_ZOOM)
        self.center_camera_on_player()

        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = self.run_state.get_player_fire_cooldown()
        self.enemies = []
        self.pending_enemy_spawns = []
        self.locked_room_id = None
        self.pending_lock_room_id = None
        self.active_room_doors = []
        self.pending_room_doors = []
        self.cleared_room_ids = set()
        self.damage_texts = []
        self.heat_pickups = []
        self.shop_room_id = generated_level.shop_room_id
        self.shop_keeper = None
        self.shop_trigger_armed = True
        self.shop_offers = []
        self.level.clear_dynamic_blockers()

        for index, enemy_spawn in enumerate(generated_level.enemy_spawns):
            enemy_class = floor_definition.enemy_pool[index % len(floor_definition.enemy_pool)]
            self.pending_enemy_spawns.append(
                {
                    'room_id': enemy_spawn.room_id,
                    'position': enemy_spawn.position,
                    'enemy_class': enemy_class,
                }
            )

        if floor_definition.has_exit and generated_level.exit_spawn is not None:
            self.floor_exit = LevelExit(generated_level.exit_spawn)
            self.floor_exit_room_id = generated_level.exit_room_id
        else:
            self.floor_exit = None
            self.floor_exit_room_id = None

        if floor_definition.has_shop and generated_level.shop_spawn is not None:
            self.shop_keeper = ShopKeeper(
                self.game,
                generated_level.shop_spawn,
                generated_level.shop_room_id,
            )
            self.shop_offers = roll_shop_offers()

    def advance_to_next_floor(self):
        self.run_state.sync_from_player(self.player)

        if not self.run_state.advance_floor():
            return

        self.current_floor = self.run_state.current_floor
        self.build_floor(self.current_floor)
        self.game.actions['interact'] = False

    def jump_to_floor(self, floor_number):
        target_floor = max(1, min(floor_number, self.total_floors))
        if target_floor == self.current_floor:
            return

        self.run_state.sync_from_player(self.player)
        self.run_state.current_floor = target_floor
        self.current_floor = target_floor
        self.build_floor(target_floor)
        self.game.actions['interact'] = False
        self.game.actions['fire'] = False

    def heal_player_to_full(self):
        self.run_state.heal_to_full()
        self.run_state.apply_to_player(self.player)
        self.sync_player_ui()

    def try_buy_shop_offer(self, offer_index):
        if offer_index < 0 or offer_index >= len(self.shop_offers):
            return False, "Предложение не найдено"

        offer = self.shop_offers[offer_index]
        success, message = self.run_state.purchase_shop_offer(offer)
        if not success:
            self.sync_player_ui()
            return False, message

        self.run_state.apply_to_player(self.player)
        self.sync_player_ui()
        self.shop_offers[offer_index] = roll_shop_offer(offer.effect_type)
        return True, f"Куплено: {offer.name}"

    def try_reroll_shop_offers(self):
        if not self.shop_offers:
            return False, "Лавка пока пуста"

        if not self.run_state.spend_currency(SHOP_REROLL_COST):
            self.sync_player_ui()
            return False, "Недостаточно жара для обновления"

        self.shop_offers = roll_shop_offers()
        self.sync_player_ui()
        return True, "Ассортимент обновлен"

    def clear_current_room_enemies(self):
        target_room_id = self.locked_room_id
        if target_room_id is None:
            target_room_id = self.current_room_id

        if target_room_id is None:
            return

        for enemy in self.enemies[:]:
            if enemy.room_id == target_room_id:
                self.remove_enemy(enemy)

        if self.locked_room_id is not None and not self.has_living_room_enemies(self.locked_room_id):
            self.unlock_room()

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

    def room_to_world_center(self, room):
        room_x, room_y, room_w, room_h = room
        center_x = (room_x + room_w // 2) * self.level.tile_size + self.level.tile_size // 2
        center_y = (room_y + room_h // 2) * self.level.tile_size + self.level.tile_size // 2
        return center_x, center_y

    def is_floor_tile(self, tile_x, tile_y):
        if tile_y < 0 or tile_y >= len(self.level.tiles):
            return False
        if tile_x < 0 or tile_x >= len(self.level.tiles[0]):
            return False

        return self.level.tiles[tile_y][tile_x] == self.level.FLOOR.value

    def group_contiguous_positions(self, positions):
        if not positions:
            return []

        sorted_positions = sorted(positions)
        groups = []
        group_start = sorted_positions[0]
        previous = sorted_positions[0]

        for position in sorted_positions[1:]:
            if position == previous + 1:
                previous = position
                continue

            groups.append((group_start, previous))
            group_start = position
            previous = position

        groups.append((group_start, previous))
        return groups

    def build_room_doors(self, room_id):
        room_x, room_y, room_w, room_h = self.rooms[room_id]
        tile_size = self.level.tile_size
        doors = []

        top_openings = [
            tile_x
            for tile_x in range(room_x, room_x + room_w)
            if self.is_floor_tile(tile_x, room_y) and self.is_floor_tile(tile_x, room_y - 1)
        ]
        for start_x, end_x in self.group_contiguous_positions(top_openings):
            boundary_y = room_y * tile_size
            rect = pygame.Rect(
                start_x * tile_size,
                boundary_y - tile_size // 2,
                (end_x - start_x + 1) * tile_size,
                tile_size,
            )
            doors.append(RoomDoor(rect, "top"))

        bottom_openings = [
            tile_x
            for tile_x in range(room_x, room_x + room_w)
            if self.is_floor_tile(tile_x, room_y + room_h - 1) and self.is_floor_tile(tile_x, room_y + room_h)
        ]
        for start_x, end_x in self.group_contiguous_positions(bottom_openings):
            boundary_y = (room_y + room_h) * tile_size
            rect = pygame.Rect(
                start_x * tile_size,
                boundary_y - tile_size // 2,
                (end_x - start_x + 1) * tile_size,
                tile_size,
            )
            doors.append(RoomDoor(rect, "bottom"))

        left_openings = [
            tile_y
            for tile_y in range(room_y, room_y + room_h)
            if self.is_floor_tile(room_x, tile_y) and self.is_floor_tile(room_x - 1, tile_y)
        ]
        for start_y, end_y in self.group_contiguous_positions(left_openings):
            boundary_x = room_x * tile_size
            rect = pygame.Rect(
                boundary_x - tile_size // 2,
                start_y * tile_size,
                tile_size,
                (end_y - start_y + 1) * tile_size,
            )
            doors.append(RoomDoor(rect, "left"))

        right_openings = [
            tile_y
            for tile_y in range(room_y, room_y + room_h)
            if self.is_floor_tile(room_x + room_w - 1, tile_y) and self.is_floor_tile(room_x + room_w, tile_y)
        ]
        for start_y, end_y in self.group_contiguous_positions(right_openings):
            boundary_x = (room_x + room_w) * tile_size
            rect = pygame.Rect(
                boundary_x - tile_size // 2,
                start_y * tile_size,
                tile_size,
                (end_y - start_y + 1) * tile_size,
            )
            doors.append(RoomDoor(rect, "right"))

        return doors

    def has_living_room_enemies(self, room_id):
        return any(enemy.room_id == room_id for enemy in self.enemies)

    def queue_room_lock(self, room_id):
        if room_id is None or room_id in self.cleared_room_ids:
            return

        self.pending_lock_room_id = room_id
        self.pending_room_doors = self.build_room_doors(room_id)

    def can_close_room(self, room_id, doors):
        if room_id is None or not doors:
            return False

        room_rect = self.get_room_world_rect(self.rooms[room_id])
        margin = self.level.tile_size
        safe_rect = room_rect.inflate(-(margin * 2), -(margin * 2))

        if safe_rect.width <= 0 or safe_rect.height <= 0:
            safe_rect = room_rect

        if not safe_rect.contains(self.player.rect):
            return False

        for door in doors:
            if door.rect.colliderect(self.player.rect):
                return False

        return True

    def lock_room(self, room_id, doors):
        self.pending_lock_room_id = None
        self.pending_room_doors = []
        self.locked_room_id = room_id
        self.active_room_doors = doors
        for door in self.active_room_doors:
            door.start_deploy()
        self.level.set_dynamic_blockers([door.rect for door in self.active_room_doors])

    def unlock_room(self):
        if self.locked_room_id is not None:
            self.cleared_room_ids.add(self.locked_room_id)

        self.locked_room_id = None
        self.pending_lock_room_id = None
        self.active_room_doors = []
        self.pending_room_doors = []
        self.level.clear_dynamic_blockers()

    def spawn_room_enemies(self, room_id):
        if room_id is None:
            return False

        if room_id == self.shop_room_id:
            return False

        spawned_any = False

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
            spawned_any = True

        return spawned_any

    def update_shop_keeper(self, delta_time):
        if self.shop_keeper is not None:
            self.shop_keeper.update(delta_time)

    def update_shop_trigger(self):
        if self.shop_keeper is None or self.current_room_id != self.shop_room_id:
            self.shop_trigger_armed = True
            return False

        player_in_range = self.shop_keeper.can_trigger(self.player.rect)
        if not player_in_range:
            self.shop_trigger_armed = True
            return False

        if not self.shop_trigger_armed:
            return False

        self.shop_trigger_armed = False
        shop_menu = ShopMenu(self.game, self)
        shop_menu.enter_state()
        return True

    def update_floor_exit(self, delta_time, actions):
        if self.floor_exit is None:
            return False

        self.floor_exit.update(delta_time)

        if self.floor_exit.can_interact(self.player.rect) and actions['interact']:
            self.advance_to_next_floor()
            return True

        return False

    def sync_player_ui(self):
        if self.player_ui is None or self.player is None:
            return

        self.player_ui.sync(
            self.player.hp,
            self.run_state.max_player_hp,
            self.current_floor,
            self.total_floors,
            self.current_floor_definition.name,
            self.run_state.currency,
        )

    def spawn_damage_text(self, value, position, color):
        self.damage_texts.append(
            FloatingDamageText(self.game, value, position, color)
        )

    def update_damage_texts(self, delta_time):
        for damage_text in self.damage_texts[:]:
            if not damage_text.update(delta_time):
                self.damage_texts.remove(damage_text)

    def spawn_heat_drop(self, enemy):
        amount = enemy.roll_heat_drop()
        self.heat_pickups.append(HeatPickup(enemy.rect.center, amount))

    def remove_enemy(self, enemy):
        if enemy not in self.enemies:
            return

        self.spawn_heat_drop(enemy)
        self.enemies.remove(enemy)

    def update_heat_pickups(self, delta_time):
        for heat_pickup in self.heat_pickups:
            heat_pickup.update(delta_time)

    def handle_heat_pickup_player_collisions(self):
        for heat_pickup in self.heat_pickups[:]:
            if not heat_pickup.can_collect(self.player.rect):
                continue

            self.run_state.add_currency(heat_pickup.amount)
            self.spawn_damage_text(
                f"+{heat_pickup.amount} жар",
                heat_pickup.rect.midtop,
                (255, 170, 70),
            )
            self.heat_pickups.remove(heat_pickup)

    def update_room_lock_state(self, delta_time):
        for door in self.active_room_doors:
            door.update(delta_time)

        if self.pending_lock_room_id is not None:
            if self.current_room_id == self.pending_lock_room_id and self.can_close_room(
                self.pending_lock_room_id,
                self.pending_room_doors,
            ):
                self.lock_room(self.pending_lock_room_id, self.pending_room_doors.copy())

        if self.locked_room_id is None:
            return

        if not self.has_living_room_enemies(self.locked_room_id):
            self.unlock_room()

    # ======== ВСЕ АПДЕЙТЫ ========
    def update(self, delta_time, actions):
        if actions['debug_toggle']:
            self.debug_hud.toggle()
            self.game.actions['debug_toggle'] = False
            self.game.actions['fire'] = False
            return

        if self.debug_hud.visible:
            self.debug_hud.update()
            self.game.actions['fire'] = False
            self.sync_player_ui()
            return

        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
            return

        self.player.update(delta_time, actions)
        player_room_id = self.get_room_id_for_point(self.player.rect.center)
        if player_room_id != self.current_room_id:
            self.current_room_id = player_room_id
            spawned_any = self.spawn_room_enemies(player_room_id)
            if spawned_any:
                self.queue_room_lock(player_room_id)

        self.update_shop_keeper(delta_time)
        if self.update_shop_trigger():
            self.game.actions['fire'] = False
            return

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

        if actions['fire'] and self.time_since_shot >= self.run_state.get_player_fire_cooldown():
            self.spawn_player_bullet()
            self.time_since_shot = 0

        self.update_player_bullets(delta_time)
        self.update_enemies(delta_time)
        self.update_enemy_bullets(delta_time)
        self.update_heat_pickups(delta_time)

        self.handle_player_to_enemy_collisions()
        self.handle_enemy_to_player_collisions()
        self.handle_heat_pickup_player_collisions()
        self.update_room_lock_state(delta_time)
        self.update_damage_texts(delta_time)
        self.run_state.sync_from_player(self.player)
        self.sync_player_ui()

        if self.player.is_dead():
            new_state = GameOver(self.game)
            new_state.enter_state()
            return

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
            if enemy.is_dead():
                self.remove_enemy(enemy)
                continue

            shot_data = enemy.update(delta_time)

            if shot_data is not None:
                for direction in shot_data['directions']:
                    self.spawn_enemy_bullet(
                        shot_data['origin'],
                        direction,
                        shot_data['speed'],
                        shot_data['damage_range'],
                    )

            if enemy.is_dead():
                self.remove_enemy(enemy)

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
        damage = random.randint(*self.run_state.get_player_bullet_damage_range())
        new_bullet = Bullet(spawn_point, velocity, damage)
        self.player_bullets.append(new_bullet)

    def spawn_enemy_bullet(self, origin, direction, speed, damage_range):
        velocity = direction * speed
        damage = random.randint(*damage_range)
        bullet = Bullet(origin, velocity, damage)
        self.enemies_bullets.append(bullet)

    # ======== ВЫЧИСЛЕНИЯ КОЛЛИЗИЙ ========
    def handle_player_to_enemy_collisions(self):
        for player_bullet in self.player_bullets[:]:
            for enemy in self.enemies[:]:
                if not enemy.is_combat_ready():
                    continue

                if player_bullet.rect.colliderect(enemy.rect):
                    self.spawn_damage_text(
                        player_bullet.damage,
                        enemy.rect.midtop,
                        (255, 235, 120),
                    )
                    enemy.take_damage(player_bullet.damage)
                    if enemy.is_dead():
                        self.remove_enemy(enemy)

                    if player_bullet in self.player_bullets:
                        self.player_bullets.remove(player_bullet)
                    
                    break
    
    def handle_enemy_to_player_collisions(self):
        for enemy_bullet in self.enemies_bullets[:]:
            if enemy_bullet.rect.colliderect(self.player.rect):
                self.spawn_damage_text(
                    enemy_bullet.damage,
                    self.player.rect.midtop,
                    (255, 120, 120),
                )
                self.player.take_damage(enemy_bullet.damage)

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

    def render_heat_pickups(self, display):
        for heat_pickup in self.heat_pickups:
            heat_pickup.render(display, self.camera)

    def render_damage_texts(self, display):
        for damage_text in self.damage_texts:
            damage_text.render(display, self.camera)

    def render_floor_exit(self, display):
        if self.floor_exit is not None:
            self.floor_exit.render(display, self.camera)

    def render_room_doors(self, display):
        for door in self.active_room_doors:
            door.render(display, self.camera)

    def render_shop_keeper(self, display):
        if self.shop_keeper is not None:
            self.shop_keeper.render(display, self.camera)

    def render_hud(self, display):
        self.sync_player_ui()

        if self.player_ui is not None:
            self.player_ui.render(display)

    def render_world_prompt(self, display):

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
                "Боссовый этаж подготовлен. Босс будет добавлен позже.",
                (255, 220, 160),
                self.game.GAME_W / 2,
                self.game.GAME_H - 40,
                24,
            )

    def render(self, display):
        display.fill((0, 0, 0))
        self.level.render(display, self.camera)
        self.render_floor_exit(display)
        self.render_heat_pickups(display)
        self.render_shop_keeper(display)
        self.render_room_doors(display)

        self.player.render(display, self.camera)
        self.render_player_bullets(display)

        self.render_enemies(display)
        self.render_enemies_bullets(display)
        self.render_damage_texts(display)
        self.render_hud(display)
        self.render_world_prompt(display)

        if self.debug_hud.visible:
            self.debug_hud.render(display)
