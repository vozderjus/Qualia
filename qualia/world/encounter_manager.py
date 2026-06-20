import pygame
from entities.room_door import RoomDoor
from states.shop_menu import ShopMenu


class EncounterManager:
    def __init__(self, world):
        self.world = world

    def get_room_world_rect(self, room):
        room_x, room_y, room_w, room_h = room
        return pygame.Rect(
            room_x * self.world.level.tile_size,
            room_y * self.world.level.tile_size,
            room_w * self.world.level.tile_size,
            room_h * self.world.level.tile_size,
        )

    def get_room_id_for_point(self, point):
        for room_id, room in enumerate(self.world.rooms):
            if self.get_room_world_rect(room).collidepoint(point):
                return room_id

        return None

    def is_floor_tile(self, tile_x, tile_y):
        if tile_y < 0 or tile_y >= len(self.world.level.tiles):
            return False
        if tile_x < 0 or tile_x >= len(self.world.level.tiles[0]):
            return False

        return self.world.level.tiles[tile_y][tile_x] == self.world.level.FLOOR.value

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
        room_x, room_y, room_w, room_h = self.world.rooms[room_id]
        tile_size = self.world.level.tile_size
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
        return any(enemy.room_id == room_id for enemy in self.world.enemies)

    def queue_room_lock(self, room_id):
        if room_id is None or room_id in self.world.cleared_room_ids:
            return

        self.world.pending_lock_room_id = room_id
        self.world.pending_room_doors = self.build_room_doors(room_id)

    def can_close_room(self, room_id, doors):
        if room_id is None or not doors:
            return False

        room_rect = self.get_room_world_rect(self.world.rooms[room_id])
        margin = self.world.level.tile_size
        safe_rect = room_rect.inflate(-(margin * 2), -(margin * 2))

        if safe_rect.width <= 0 or safe_rect.height <= 0:
            safe_rect = room_rect

        if not safe_rect.contains(self.world.player.rect):
            return False

        for door in doors:
            if door.rect.colliderect(self.world.player.rect):
                return False

        return True

    def lock_room(self, room_id, doors):
        self.world.pending_lock_room_id = None
        self.world.pending_room_doors = []
        self.world.locked_room_id = room_id
        self.world.active_room_doors = doors
        for door in self.world.active_room_doors:
            door.start_deploy()
        self.world.level.set_dynamic_blockers([door.rect for door in self.world.active_room_doors])

    def unlock_room(self):
        if self.world.locked_room_id is not None:
            self.world.cleared_room_ids.add(self.world.locked_room_id)

        self.world.locked_room_id = None
        self.world.pending_lock_room_id = None
        self.world.active_room_doors = []
        self.world.pending_room_doors = []
        self.world.level.clear_dynamic_blockers()

    def spawn_room_enemies(self, room_id):
        if room_id is None or room_id == self.world.shop_room_id:
            return False

        spawned_any = False

        for spawn_data in self.world.pending_enemy_spawns[:]:
            if spawn_data.room_id != room_id:
                continue

            enemy = spawn_data.enemy_class(
                self.world.game,
                self.world.level,
                self.world.player,
                spawn_data.position,
            )
            enemy.room_id = room_id
            self.world.enemies.append(enemy)
            self.world.pending_enemy_spawns.remove(spawn_data)
            spawned_any = True

        if self.world.pending_boss_spawn is not None and self.world.pending_boss_spawn.room_id == room_id:
            boss = self.world.pending_boss_spawn.boss_class(
                self.world.game,
                self.world.level,
                self.world.player,
                self.world.pending_boss_spawn.position,
            )
            boss.room_id = room_id
            self.world.boss = boss
            self.world.enemies.append(boss)
            self.world.pending_boss_spawn = None
            spawned_any = True

        return spawned_any

    def clear_current_room_enemies(self):
        target_room_id = self.world.locked_room_id
        if target_room_id is None:
            target_room_id = self.world.current_room_id

        if target_room_id is None:
            return

        for enemy in self.world.enemies[:]:
            if enemy.room_id == target_room_id:
                self.world.remove_enemy(enemy)

        if self.world.locked_room_id is not None and not self.has_living_room_enemies(self.world.locked_room_id):
            self.unlock_room()

    def update_shop_keeper(self, delta_time):
        if self.world.shop_keeper is not None:
            self.world.shop_keeper.update(delta_time)

    def update_shop_trigger(self):
        if self.world.shop_keeper is None or self.world.current_room_id != self.world.shop_room_id:
            self.world.shop_trigger_armed = True
            return False

        player_in_range = self.world.shop_keeper.can_trigger(self.world.player.rect)
        if not player_in_range:
            self.world.shop_trigger_armed = True
            return False

        if not self.world.shop_trigger_armed:
            return False

        self.world.shop_trigger_armed = False
        ShopMenu(self.world.game, self.world).enter_state()
        return True

    def update_floor_exit(self, delta_time, actions):
        if self.world.floor_exit is None:
            return False

        self.world.floor_exit.update(delta_time)

        if self.world.floor_exit.can_interact(self.world.player.rect) and actions["interact"]:
            self.world.advance_to_next_floor()
            return True

        return False

    def update_room_lock_state(self, delta_time):
        for door in self.world.active_room_doors:
            door.update(delta_time)

        if self.world.pending_lock_room_id is not None:
            if self.world.current_room_id == self.world.pending_lock_room_id and self.can_close_room(
                self.world.pending_lock_room_id,
                self.world.pending_room_doors,
            ):
                self.lock_room(
                    self.world.pending_lock_room_id,
                    self.world.pending_room_doors.copy(),
                )

        if self.world.locked_room_id is None:
            return

        if not self.has_living_room_enemies(self.world.locked_room_id):
            self.unlock_room()
