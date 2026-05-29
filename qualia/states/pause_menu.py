import os

import pygame
from states.state import State


class PauseMenu(State):
    def __init__(self, game):
        self.game = game
        State.__init__(self, game)
        self.menu_img = pygame.image.load(os.path.join("images", "pause_menu.png"))
        self.menu_img = pygame.transform.scale(self.menu_img, (400, 700))
        self.menu_rect = self.menu_img.get_rect()
        self.menu_rect.center = (self.game.GAME_W / 2, self.game.GAME_H / 2)
        
        self.buttons = self._create_buttons()
        self.clicked = False
    
    def _create_buttons(self):
        center_x, center_y = self.game.GAME_W / 2, self.game.GAME_H / 2
        menu_left, menu_top = self.menu_rect.left, self.menu_rect.top

        resume_img = pygame.image.load(
            os.path.join("images", "pause_play_b_active.png")
        ).convert_alpha()
        settings_img = pygame.image.load(
            os.path.join("images", "pause_settings_b_active.png")
        ).convert_alpha()
        main_menu_img = pygame.image.load(
            os.path.join("images", "pause_exit_b_active.png")
        ).convert_alpha()
        
        resume_img = pygame.transform.scale(resume_img, (400, 700))
        settings_img = pygame.transform.scale(settings_img, (400, 700))
        main_menu_img = pygame.transform.scale(main_menu_img, (400, 700))
        
        return {
            "resume": {
                "image": resume_img,
                "overlay_rect": self.menu_rect.copy(),
                "rect": pygame.Rect(menu_left + 40, menu_top + 180, 320, 70),
            },
            "settings": {
                "image": settings_img,
                "overlay_rect": self.menu_rect.copy(),
                "rect": pygame.Rect(menu_left + 40, menu_top + 300, 320, 70),
            },
            "main_menu": {
                "image": main_menu_img,
                "overlay_rect": self.menu_rect.copy(),
                "rect": pygame.Rect(menu_left + 40, menu_top + 420, 320, 70),
            },
        }

    def get_menu_action(self):
        action = None
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for name, button_data in self.buttons.items():
            if button_data["rect"].collidepoint(mouse_pos):
                if mouse_pressed and not self.clicked:
                    self.clicked = True
                    action = name

        if not mouse_pressed:
            self.clicked = False

        return action

    def update(self, delta_time, actions):
        if actions["start"]:
            self.exit_state()
            self.game.reset_keys()
            return

        action = self.get_menu_action()

        if action == "resume":
            self.exit_state()
        elif action == "settings":
            print("settings")
        elif action == "main_menu":
            self.game.state_stack.pop()
            self.game.state_stack.pop()

        self.game.reset_keys()

    def render_buttons(self, display):
        mouse_pos = pygame.mouse.get_pos()

        for button_data in self.buttons.values():
            if button_data["rect"].collidepoint(mouse_pos):
                display.blit(button_data["image"], button_data["overlay_rect"])
    
    def render(self, display):
        self.prev_state.render(display)
        display.blit(self.menu_img, self.menu_rect)
        self.render_buttons(display)