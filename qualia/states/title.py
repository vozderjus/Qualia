import math

import pygame
from states.game_world import GameWorld
from states.settings_menu import SettingsMenu
from states.state import State
from uis import Button


class Title(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg = pygame.image.load("images/main_menu_placeholder.png").convert()
        self.clicked = False
        self.buttons = self._create_buttons()

        self.title_time = 0

    def _make_button_pair(self, x, y, normal_path, active_path):
        return {
            "normal": Button(x, y, pygame.image.load(normal_path).convert_alpha(), 1),
            "active": Button(x, y, pygame.image.load(active_path).convert_alpha(), 1),
        }

    def _create_buttons(self):
        center_x = self.game.GAME_W / 2
        center_y = self.game.GAME_H / 2

        return {
            "play": self._make_button_pair(
                center_x,
                center_y - 100,
                "images/play_b_ph.png",
                "images/play_b_ph_active.png",
            ),
            "settings": self._make_button_pair(
                center_x,
                center_y + 52,
                "images/settings_b_ph.png",
                "images/settings_b_ph_active.png",
            ),
            "exit": self._make_button_pair(
                center_x,
                center_y + 204,
                "images/exit_b_ph.png",
                "images/exit_b_ph_active.png",
            ),
        }

    def update(self, delta_time, actions):
        self.title_time += delta_time
        self.game.ensure_main_menu_music()

        action = self.get_menu_action()

        if action == "play" or actions["start"]:
            self.game.fadeout_music()
            new_state = GameWorld(self.game)
            new_state.enter_state()
        elif action == "settings":
            SettingsMenu(self.game).enter_state()
        elif action == "exit":
            self.game.running = False
            self.game.playing = False

        self.game.reset_keys()

    def get_menu_action(self):
        action = None
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for name, button_states in self.buttons.items():
            normal_button = button_states["normal"]
            hovered = normal_button.rect.collidepoint(mouse_pos)
            if hovered and mouse_pressed and not self.clicked:
                self.clicked = True
                action = name

        if not mouse_pressed:
            self.clicked = False

        return action

    def render_menu(self, display):
        mouse_pos = pygame.mouse.get_pos()

        for button_states in self.buttons.values():
            normal_button = button_states["normal"]
            active_button = button_states["active"]
            hovered = normal_button.rect.collidepoint(mouse_pos)
            current_button = active_button if hovered else normal_button
            current_button.draw(display)

    def render(self, display):
        offset_y = math.sin(self.title_time * 2) * 10

        display.blit(self.bg, (0, 0))
        self.render_menu(display)

        self.game.draw_text(
            display,
            "Qualia",
            (255, 255, 255),
            self.game.GAME_W / 2,
            90 + offset_y,
        )
