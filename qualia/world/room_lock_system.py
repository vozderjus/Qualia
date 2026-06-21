class RoomLockSystem:
    def __init__(self, world, layout_cache):
        self.world = world
        self.layout_cache = layout_cache

    def queue_room_lock(self, room_id):
        if room_id is None or room_id in self.world.cleared_room_ids:
            return

        room_doors = self.layout_cache.build_room_doors(room_id)
        if not room_doors:
            return

        self.world.pending_lock_room_id = room_id
        self.world.pending_room_doors = room_doors

    def unlock_room(self):
        if self.world.locked_room_id is not None:
            self.world.cleared_room_ids.add(self.world.locked_room_id)

        self.world.locked_room_id = None
        self.world.pending_lock_room_id = None
        self.world.active_room_doors = []
        self.world.pending_room_doors = []
        self.world.level.clear_dynamic_blockers()

    def update(self, delta_time, room_has_enemies):
        for door in self.world.active_room_doors:
            door.update(delta_time)

        if self.world.pending_lock_room_id is not None:
            if (
                self.world.current_room_id == self.world.pending_lock_room_id
                and self._can_close_room(
                    self.world.pending_lock_room_id,
                    self.world.pending_room_doors,
                )
            ):
                self._lock_room(
                    self.world.pending_lock_room_id,
                    self.world.pending_room_doors.copy(),
                )

        if self.world.locked_room_id is None:
            return

        if not room_has_enemies(self.world.locked_room_id):
            self.unlock_room()

    def _can_close_room(self, room_id, doors):
        if room_id is None or not doors:
            return False

        room_rect = self.layout_cache.get_room_rect(room_id)
        margin = self.world.level.tile_size
        safe_rect = room_rect.inflate(-(margin * 2), -(margin * 2))
        if safe_rect.width <= 0 or safe_rect.height <= 0:
            safe_rect = room_rect

        if not safe_rect.contains(self.world.player.rect):
            return False

        return not any(
            door.rect.colliderect(self.world.player.rect)
            for door in doors
        )

    def _lock_room(self, room_id, doors):
        self.world.pending_lock_room_id = None
        self.world.pending_room_doors = []
        self.world.locked_room_id = room_id
        self.world.active_room_doors = doors
        for door in self.world.active_room_doors:
            door.start_deploy()
        self.world.level.set_dynamic_blockers(
            [door.rect for door in self.world.active_room_doors]
        )
