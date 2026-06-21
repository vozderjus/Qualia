from states.shop_menu import ShopMenu


class WorldInteractionSystem:
    def __init__(self, world):
        self.world = world

    def update_shop_keeper(self, delta_time):
        if self.world.shop_keeper is not None:
            self.world.shop_keeper.update(delta_time)

    def update_shop_trigger(self):
        if (
            self.world.shop_keeper is None
            or self.world.current_room_id != self.world.shop_room_id
        ):
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
        if (
            self.world.floor_exit.can_interact(self.world.player.rect)
            and actions["interact"]
        ):
            self.world.advance_to_next_floor()
            return True

        return False
