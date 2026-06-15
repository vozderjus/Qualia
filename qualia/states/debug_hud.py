import os

import pygame


class DebugHUD:
    def __init__(self, game, world):
        self.game = game
        self.world = world
        self.visible = False
        self.clicked = False
        self.heat_amount = 50
        self.font_path = os.path.join("font", "PixelifySans-VariableFont_wght.ttf")

        self.overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H), pygame.SRCALPHA)
        self.overlay.fill((7, 10, 18, 190))

        self.panel_rect = pygame.Rect(0, 0, 820, 500)
        self.panel_rect.center = (self.game.GAME_W // 2, self.game.GAME_H // 2)

    def toggle(self):
        self.visible = not self.visible
        self.clicked = False

    def get_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
        scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
        return mouse_x * scale_x, mouse_y * scale_y

    def make_button(self, x, y, width, height, label, action):
        return {
            "rect": pygame.Rect(x, y, width, height),
            "label": label,
            "action": action,
        }

    def build_buttons(self):
        panel = self.panel_rect
        buttons = []

        buttons.append(
            self.make_button(
                panel.left + 36,
                panel.top + 126,
                144,
                48,
                "Пред. этаж",
                "prev_floor",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 640,
                panel.top + 126,
                144,
                48,
                "След. этаж",
                "next_floor",
            )
        )

        floor_button_width = 78
        floor_button_gap = 12
        floor_row_y = panel.top + 126
        total_floors = self.world.total_floors
        total_width = total_floors * floor_button_width + (total_floors - 1) * floor_button_gap
        start_x = panel.centerx - total_width // 2

        for floor_number in range(1, total_floors + 1):
            buttons.append(
                self.make_button(
                    start_x + (floor_number - 1) * (floor_button_width + floor_button_gap),
                    floor_row_y,
                    floor_button_width,
                    48,
                    str(floor_number),
                    f"floor:{floor_number}",
                )
            )

        buttons.append(
            self.make_button(
                panel.left + 36,
                panel.top + 256,
                80,
                48,
                "-10",
                "heat_down",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 298,
                panel.top + 256,
                80,
                48,
                "+10",
                "heat_up",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 410,
                panel.top + 256,
                174,
                48,
                "Добавить жар",
                "add_heat",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 610,
                panel.top + 256,
                174,
                48,
                "Убрать жар",
                "remove_heat",
            )
        )

        buttons.append(
            self.make_button(
                panel.left + 36,
                panel.top + 364,
                220,
                52,
                "Полное лечение",
                "heal_full",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 300,
                panel.top + 364,
                220,
                52,
                "Очистить комнату",
                "clear_room",
            )
        )
        buttons.append(
            self.make_button(
                panel.left + 564,
                panel.top + 364,
                220,
                52,
                "Закрыть HUD",
                "close",
            )
        )

        return buttons

    def draw_text_left(self, display, text, color, x, y, size=24):
        font = pygame.font.Font(self.font_path, size)
        text_surface = font.render(text, True, color)
        display.blit(text_surface, (x, y))

    def draw_button(self, display, button, mouse_pos):
        rect = button["rect"]
        hovered = rect.collidepoint(mouse_pos)

        fill_color = (50, 60, 78)
        border_color = (120, 145, 185)

        if hovered:
            fill_color = (70, 84, 110)
            border_color = (180, 205, 245)

        if button["action"] == f"floor:{self.world.current_floor}":
            fill_color = (85, 100, 135)
            border_color = (240, 235, 180)

        pygame.draw.rect(display, fill_color, rect, border_radius=10)
        pygame.draw.rect(display, border_color, rect, 3, border_radius=10)
        self.game.draw_text(
            display,
            button["label"],
            (245, 245, 245),
            rect.centerx,
            rect.centery,
            24,
        )

    def apply_action(self, action):
        if action == "prev_floor":
            self.world.jump_to_floor(self.world.current_floor - 1)
            return

        if action == "next_floor":
            self.world.jump_to_floor(self.world.current_floor + 1)
            return

        if action.startswith("floor:"):
            target_floor = int(action.split(":")[1])
            self.world.jump_to_floor(target_floor)
            return

        if action == "heat_down":
            self.heat_amount = max(10, self.heat_amount - 10)
            return

        if action == "heat_up":
            self.heat_amount = min(999, self.heat_amount + 10)
            return

        if action == "add_heat":
            self.world.run_state.add_currency(self.heat_amount)
            self.world.spawn_damage_text(
                f"+{self.heat_amount} жар",
                self.world.player.rect.midtop,
                (255, 180, 90),
            )
            self.world.sync_player_ui()
            return

        if action == "remove_heat":
            actual_removed = min(self.heat_amount, self.world.run_state.currency)
            self.world.run_state.add_currency(-actual_removed)
            if actual_removed > 0:
                self.world.spawn_damage_text(
                    f"-{actual_removed} жар",
                    self.world.player.rect.midtop,
                    (180, 220, 255),
                )
            self.world.sync_player_ui()
            return

        if action == "heal_full":
            self.world.heal_player_to_full()
            return

        if action == "clear_room":
            self.world.clear_current_room_enemies()
            return

        if action == "close":
            self.visible = False

    def update(self):
        mouse_pos = self.get_mouse_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        buttons = self.build_buttons()

        if mouse_pressed and not self.clicked:
            for button in buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self.apply_action(button["action"])
                    break

            self.clicked = True

        if not mouse_pressed:
            self.clicked = False

    def render(self, display):
        mouse_pos = self.get_mouse_pos()
        buttons = self.build_buttons()
        panel = self.panel_rect

        display.blit(self.overlay, (0, 0))
        pygame.draw.rect(display, (22, 28, 39), panel, border_radius=18)
        pygame.draw.rect(display, (110, 130, 170), panel, 4, border_radius=18)

        self.game.draw_text(
            display,
            "DEBUG HUD",
            (255, 255, 255),
            panel.centerx,
            panel.top + 38,
            34,
        )
        self.game.draw_text(
            display,
            "F1 - скрыть | ЛКМ - действие",
            (190, 200, 220),
            panel.centerx,
            panel.top + 76,
            20,
        )

        self.draw_text_left(
            display,
            f"Этаж: {self.world.current_floor}/{self.world.total_floors}",
            (245, 245, 245),
            panel.left + 36,
            panel.top + 102,
            24,
        )
        self.draw_text_left(
            display,
            f"HP: {self.world.player.hp}/{self.world.run_state.max_player_hp}",
            (245, 245, 245),
            panel.left + 36,
            panel.top + 202,
            24,
        )
        self.draw_text_left(
            display,
            f"Жар: {self.world.run_state.currency}",
            (255, 190, 90),
            panel.left + 300,
            panel.top + 202,
            24,
        )
        self.draw_text_left(
            display,
            f"Врагов в мире: {len(self.world.enemies)}",
            (220, 225, 240),
            panel.left + 470,
            panel.top + 202,
            24,
        )
        self.draw_text_left(
            display,
            f"Ожидают спавна: {len(self.world.pending_enemy_spawns)}",
            (220, 225, 240),
            panel.left + 470,
            panel.top + 232,
            20,
        )
        self.draw_text_left(
            display,
            f"Шаг жара: {self.heat_amount}",
            (255, 230, 170),
            panel.left + 136,
            panel.top + 266,
            24,
        )
        self.draw_text_left(
            display,
            f"Текущая комната: {self.world.current_room_id}",
            (210, 220, 235),
            panel.left + 36,
            panel.top + 324,
            22,
        )
        self.draw_text_left(
            display,
            f"Заблокированная комната: {self.world.locked_room_id}",
            (210, 220, 235),
            panel.left + 360,
            panel.top + 324,
            22,
        )

        for button in buttons:
            self.draw_button(display, button, mouse_pos)
