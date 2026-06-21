from world.room_layout_cache import RoomLayoutCache
from world.room_lock_system import RoomLockSystem
from world.world_interaction_system import WorldInteractionSystem


class EncounterManager:
    def __init__(self, world):
        self.world = world
        self.layout_cache = RoomLayoutCache()
        self.room_lock_system = RoomLockSystem(world, self.layout_cache)
        self.interaction_system = WorldInteractionSystem(world)

    def prepare_floor_layout(self):
        self.layout_cache.prepare(self.world.level, self.world.rooms)

    def get_room_id_for_point(self, point):
        return self.layout_cache.get_room_id_for_point(point)

    def has_living_room_enemies(self, room_id):
        return self.world.alive_enemy_counts_by_room.get(room_id, 0) > 0

    def track_spawned_enemy(self, enemy):
        if enemy.room_id is None:
            return

        current_count = self.world.alive_enemy_counts_by_room.get(enemy.room_id, 0)
        self.world.alive_enemy_counts_by_room[enemy.room_id] = current_count + 1

    def track_removed_enemy(self, enemy):
        if enemy.room_id is None:
            return

        current_count = self.world.alive_enemy_counts_by_room.get(enemy.room_id, 0)
        if current_count <= 1:
            self.world.alive_enemy_counts_by_room.pop(enemy.room_id, None)
            return

        self.world.alive_enemy_counts_by_room[enemy.room_id] = current_count - 1

    def queue_room_lock(self, room_id):
        self.room_lock_system.queue_room_lock(room_id)

    def unlock_room(self):
        self.room_lock_system.unlock_room()

    def spawn_room_enemies(self, room_id):
        if room_id is None or room_id == self.world.shop_room_id:
            return False

        spawned_any = False
        room_spawns = self.world.pending_enemy_spawns_by_room.pop(room_id, [])
        if room_spawns:
            self.world.pending_enemy_spawn_count = max(
                0,
                self.world.pending_enemy_spawn_count - len(room_spawns),
            )

        for spawn_data in room_spawns:
            enemy = spawn_data.enemy_class(
                self.world.game,
                self.world.level,
                self.world.player,
                spawn_data.position,
            )
            enemy.room_id = room_id
            self.world.enemies.append(enemy)
            self.track_spawned_enemy(enemy)
            spawned_any = True

        if (
            self.world.pending_boss_spawn is not None
            and self.world.pending_boss_spawn.room_id == room_id
        ):
            boss = self.world.pending_boss_spawn.boss_class(
                self.world.game,
                self.world.level,
                self.world.player,
                self.world.pending_boss_spawn.position,
            )
            boss.room_id = room_id
            self.world.boss = boss
            self.world.enemies.append(boss)
            self.track_spawned_enemy(boss)
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

        if (
            self.world.locked_room_id is not None
            and not self.has_living_room_enemies(self.world.locked_room_id)
        ):
            self.unlock_room()

    def update_shop_keeper(self, delta_time):
        self.interaction_system.update_shop_keeper(delta_time)

    def update_shop_trigger(self):
        return self.interaction_system.update_shop_trigger()

    def update_floor_exit(self, delta_time, actions):
        return self.interaction_system.update_floor_exit(delta_time, actions)

    def update_room_lock_state(self, delta_time):
        self.room_lock_system.update(
            delta_time,
            self.has_living_room_enemies,
        )
