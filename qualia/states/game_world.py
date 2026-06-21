import random

import pygame
from constants import CAMERA_ZOOM
from entities.camera import Camera
from entities.player import Player
from entities.shop_keeper import ShopKeeper
from run_state import RunState
from shop_content import SHOP_REROLL_COST, roll_shop_offer, roll_shop_offers
from states.debug_hud import DebugHUD
from states.game_over import GameOver
from states.game_victory import GameVictory
from states.pause_menu import PauseMenu
from states.player_ui import PlayerUI
from states.state import State
from world.combat_system import CombatSystem
from world.encounter_manager import EncounterManager
from world.floor_builder import FloorBuilder
from world.floor_definitions import FLOOR_DEFINITIONS


class GameWorld(State):
    def __init__(self, game, run_state=None):
        State.__init__(self, game)
        self.floor_definitions = FLOOR_DEFINITIONS
        self.total_floors = len(self.floor_definitions)
        self.run_state = run_state or RunState.new_run(self.total_floors)
        self.game.run_state = self.run_state
        self.current_floor = self.run_state.current_floor
        self.current_floor_definition = None
        self.level = None
        self.level_renderer = None
        self.player = None
        self.rooms = []
        self.current_room_id = None
        self.camera = None

        self.player_bullets = []
        self.enemies_bullets = []
        self.time_since_shot = self.run_state.get_player_fire_cooldown()

        self.enemies = []
        self.pending_enemy_spawns_by_room = {}
        self.pending_enemy_spawn_count = 0
        self.alive_enemy_counts_by_room = {}
        self.floor_exit = None
        self.floor_exit_room_id = None
        self.locked_room_id = None
        self.pending_lock_room_id = None
        self.active_room_doors = []
        self.pending_room_doors = []
        self.cleared_room_ids = set()
        self.boss = None
        self.boss_room_id = None
        self.pending_boss_spawn = None
        self.pending_victory = False
        self.player_ui = None
        self.damage_texts = []
        self.heat_pickups = []
        self.shop_room_id = None
        self.shop_keeper = None
        self.shop_trigger_armed = True
        self.shop_offers = []
        self.current_floor_has_shop = False
        self.debug_hud = DebugHUD(self.game, self)
        self.floor_builder = FloorBuilder()
        self.encounter_manager = EncounterManager(self)
        self.combat_system = CombatSystem(self)

        self.build_floor(self.run_state.current_floor)

    def get_floor_definition(self, floor_number):
        definition_index = min(max(0, floor_number - 1), self.total_floors - 1)
        return self.floor_definitions[definition_index]

    def center_camera_on_player(self):
        self.camera.x = self.player.rect.centerx - self.camera.visible_width() / 2
        self.camera.y = self.player.rect.centery - self.camera.visible_height() / 2
        self.camera.clamp(self.level.pixel_width, self.level.pixel_height)

    def should_spawn_shop(self, floor_definition):
        chance = max(0.0, min(1.0, floor_definition.shop_spawn_chance))
        return random.random() < chance

    def build_floor(self, floor_number):
        floor_definition = self.get_floor_definition(floor_number)
        self.current_floor_definition = floor_definition
        self.current_floor_has_shop = self.should_spawn_shop(floor_definition)

        if floor_definition.music_track is not None:
            self.game.play_music(floor_definition.music_track)
        else:
            self.game.stop_music()

        floor_build = self.floor_builder.build(
            floor_definition,
            has_shop=self.current_floor_has_shop,
        )
        self.level = floor_build.level
        self.level_renderer = floor_build.level_renderer
        self.player = Player(self.game, self.level, floor_build.player_spawn)
        self.run_state.apply_to_player(self.player)
        self.player_ui = PlayerUI(self.game, self.player.hp, self.run_state.max_player_hp)
        self.rooms = floor_build.rooms
        self.current_room_id = None
        self.camera = Camera(self.game.GAME_W, self.game.GAME_H, CAMERA_ZOOM)
        self.center_camera_on_player()
        self.encounter_manager.prepare_floor_layout()

        self.combat_system.reset()
        self.enemies = []
        self.pending_enemy_spawns_by_room = {}
        for enemy_spawn in floor_build.enemy_spawns:
            self.pending_enemy_spawns_by_room.setdefault(
                enemy_spawn.room_id,
                [],
            ).append(enemy_spawn)
        self.pending_enemy_spawn_count = len(floor_build.enemy_spawns)
        self.alive_enemy_counts_by_room = {}
        self.locked_room_id = None
        self.pending_lock_room_id = None
        self.active_room_doors = []
        self.pending_room_doors = []
        self.cleared_room_ids = set()
        self.boss = None
        self.boss_room_id = floor_build.boss_room_id
        self.pending_boss_spawn = floor_build.boss_spawn
        self.pending_victory = False
        self.shop_room_id = floor_build.shop_room_id
        self.shop_keeper = None
        self.shop_trigger_armed = True
        self.shop_offers = []
        self.level.clear_dynamic_blockers()

        self.floor_exit = floor_build.floor_exit
        self.floor_exit_room_id = floor_build.floor_exit_room_id

        if self.current_floor_has_shop and floor_build.shop_spawn is not None:
            self.shop_keeper = ShopKeeper(
                self.game,
                floor_build.shop_spawn,
                floor_build.shop_room_id,
            )
            self.shop_offers = self.roll_shop_offers_for_current_run()

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
        self.shop_offers[offer_index] = self.roll_shop_offer_for_current_run(
            offer.effect_type
        )
        return True, f"Куплено: {offer.name}"

    def get_shop_price_multiplier(self):
        return self.run_state.get_shop_price_multiplier()

    def get_shop_reroll_cost(self):
        return max(
            SHOP_REROLL_COST,
            int(round(SHOP_REROLL_COST * self.get_shop_price_multiplier())),
        )

    def roll_shop_offer_for_current_run(self, effect_type):
        return roll_shop_offer(
            effect_type,
            price_multiplier=self.get_shop_price_multiplier(),
        )

    def roll_shop_offers_for_current_run(self):
        return roll_shop_offers(
            price_multiplier=self.get_shop_price_multiplier(),
        )

    def try_reroll_shop_offers(self):
        if not self.shop_offers:
            return False, "Лавка пока пуста"

        reroll_cost = self.get_shop_reroll_cost()
        if not self.run_state.spend_currency(reroll_cost):
            self.sync_player_ui()
            return False, "Недостаточно жара для обновления"

        self.run_state.register_shop_reroll()
        self.shop_offers = self.roll_shop_offers_for_current_run()
        self.sync_player_ui()
        return True, "Ассортимент обновлен"

    def clear_current_room_enemies(self):
        self.encounter_manager.clear_current_room_enemies()

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
            self.player.dodge_cooldown_ratio(),
        )

    def complete_boss_victory(self):
        if not self.pending_victory:
            return False

        self.pending_victory = False
        self.run_state.sync_from_player(self.player)
        self.run_state.mark_floor_cleared()
        self.encounter_manager.unlock_room()
        self.combat_system.reset()
        self.game.run_state = self.run_state
        self.game.actions['fire'] = False
        self.game.actions['interact'] = False

        victory_state = GameVictory(self.game)
        victory_state.enter_state()
        return True

    def spawn_damage_text(self, value, position, color):
        self.combat_system.spawn_damage_text(value, position, color)

    def remove_enemy(self, enemy):
        self.combat_system.remove_enemy(enemy)

    def update(self, delta_time, actions):
        if self.complete_boss_victory():
            return

        if actions['debug_toggle']:
            self.debug_hud.toggle()
            self.game.actions['debug_toggle'] = False
            self.game.actions['fire'] = False
            return

        if self.debug_hud.visible:
            self.debug_hud.update()
            if self.complete_boss_victory():
                return
            self.game.actions['fire'] = False
            self.sync_player_ui()
            return

        if actions['pause']:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
            return

        self.player.update(delta_time, actions)
        player_room_id = self.encounter_manager.get_room_id_for_point(self.player.rect.center)
        if player_room_id != self.current_room_id:
            self.current_room_id = player_room_id
            spawned_any = self.encounter_manager.spawn_room_enemies(player_room_id)
            if spawned_any:
                self.encounter_manager.queue_room_lock(player_room_id)

        self.encounter_manager.update_shop_keeper(delta_time)
        if self.encounter_manager.update_shop_trigger():
            self.game.actions['fire'] = False
            return

        self.time_since_shot += delta_time
        self.camera.smooth_follow(
            self.player.rect.centerx,
            self.player.rect.centery,
            speed=5,
            delta_time=delta_time,
        )
        self.camera.clamp(self.level.pixel_width, self.level.pixel_height)

        if self.encounter_manager.update_floor_exit(delta_time, actions):
            return

        if (
            actions['fire']
            and self.player.can_fire()
            and self.time_since_shot >= self.run_state.get_player_fire_cooldown()
        ):
            self.combat_system.spawn_player_bullet()
            self.time_since_shot = 0

        self.combat_system.update_player_bullets(delta_time)
        self.combat_system.update_enemies(delta_time)
        if self.complete_boss_victory():
            return
        self.combat_system.update_enemy_bullets(delta_time)
        self.combat_system.update_heat_pickups(delta_time)

        self.combat_system.handle_player_to_enemy_collisions()
        if self.complete_boss_victory():
            return
        self.combat_system.handle_enemy_to_player_collisions()
        self.combat_system.handle_heat_pickup_player_collisions()
        self.encounter_manager.update_room_lock_state(delta_time)
        self.combat_system.update_damage_texts(delta_time)
        self.run_state.sync_from_player(self.player)
        self.sync_player_ui()

        if self.player.is_dead():
            new_state = GameOver(self.game)
            new_state.enter_state()
            return

    # ======== ВСЕ РЕНДЕРЫ ========
    def render_enemies(self, display):
        for enemy in self.enemies:
            enemy.render(display, self.camera)

    def render_hud(self, display):
        self.sync_player_ui()

        if self.player_ui is not None:
            self.player_ui.render(display)

    def render_boss_ui(self, display):
        if self.boss is None or not self.boss.is_combat_ready():
            return

        hp_ratio = 0
        if self.boss.max_hp > 0:
            hp_ratio = max(0, min(1, self.boss.hp / self.boss.max_hp))

        bar_width = 520
        bar_height = 22
        bar_rect = pygame.Rect(
            self.game.GAME_W // 2 - bar_width // 2,
            44,
            bar_width,
            bar_height,
        )
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_rect.width * hp_ratio)
        phase_color = self.boss.get_phase_color()

        pygame.draw.rect(display, (34, 18, 24), bar_rect, border_radius=10)
        if fill_rect.width > 0:
            pygame.draw.rect(display, phase_color, fill_rect, border_radius=10)
        pygame.draw.rect(display, (236, 225, 212), bar_rect, 3, border_radius=10)

        self.game.draw_text(
            display,
            self.boss.display_name,
            (255, 238, 214),
            self.game.GAME_W / 2,
            20,
            28,
        )
        self.game.draw_text(
            display,
            self.boss.phase_label,
            phase_color,
            self.game.GAME_W / 2,
            82,
            20,
        )

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
            return

        if not self.current_floor_definition.is_boss_floor:
            return

        if self.boss is not None:
            prompt_text = "Победите босса, чтобы завершить забег"
            prompt_color = (255, 220, 160)
        elif self.pending_boss_spawn is not None:
            if self.current_room_id == self.boss_room_id:
                prompt_text = "Зал босса пробуждается"
            else:
                prompt_text = "Найдите зал босса"
            prompt_color = (210, 230, 255)
        else:
            return

        self.game.draw_text(
            display,
            prompt_text,
            prompt_color,
            self.game.GAME_W / 2,
            self.game.GAME_H - 40,
            24,
        )

    def render(self, display):
        display.fill((0, 0, 0))
        self.level_renderer.render(display, self.camera)
        if self.floor_exit is not None:
            self.floor_exit.render(display, self.camera)
        self.combat_system.render_heat_pickups(display)
        if self.shop_keeper is not None:
            self.shop_keeper.render(display, self.camera)
        for door in self.active_room_doors:
            door.render(display, self.camera)

        self.player.render(display, self.camera)
        self.combat_system.render_player_bullets(display)

        self.render_enemies(display)
        self.combat_system.render_enemy_bullets(display)
        self.combat_system.render_damage_texts(display)
        self.render_hud(display)
        self.render_boss_ui(display)
        self.render_world_prompt(display)

        if self.debug_hud.visible:
            self.debug_hud.render(display)


Game_World = GameWorld
