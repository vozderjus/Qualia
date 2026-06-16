import os

import pygame


class DebugHUD:
    def __init__(self, game, world):
        self.game = game
        self.world = world
        self.visible = False
        self.clicked = False
        self.heat_amount = 50
        self.font_path = os.path.join("font", "Keleti-Regular.ttf")

        self.overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 170))

        self.panel_rect = pygame.Rect(0, 0, 960, 560)
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

        floor_y = panel.top + 220
        prev_width = 170
        next_width = 170
        floor_button_width = 82
        floor_button_gap = 10

        buttons.append(
            self.make_button(
                panel.left + 30,
                floor_y + 10,
                prev_width,
                50,
                "Пред. этаж",
                "prev_floor",
            )
        )
        buttons.append(
            self.make_button(
                panel.right - 30 - next_width,
                floor_y + 10,
                next_width,
                48,
                "След. этаж",
                "next_floor",
            )
        )

        total_floors = self.world.total_floors
        row_width = total_floors * floor_button_width + (total_floors - 1) * floor_button_gap
        start_x = panel.centerx - row_width // 2

        for floor_number in range(1, total_floors + 1):
            buttons.append(
                self.make_button(
                    start_x + (floor_number - 1) * (floor_button_width + floor_button_gap),
                    floor_y + 10,
                    floor_button_width,
                    48,
                    str(floor_number),
                    f"floor:{floor_number}",
                )
            )

        heat_y = panel.top + 350
        buttons.extend(
            [
                self.make_button(panel.left + 30, heat_y, 80, 48, "-10", "heat_down"),
                self.make_button(panel.left + 122, heat_y, 80, 48, "+10", "heat_up"),
                self.make_button(panel.left + 250, heat_y, 250, 48, "Добавить жар", "add_heat"),
                self.make_button(panel.left + 520, heat_y, 250, 48, "Убрать жар", "remove_heat"),
            ]
        )

        util_y = panel.top + 470
        buttons.extend(
            [
                self.make_button(panel.left + 30, util_y, 250, 48, "Полное лечение", "heal_full"),
                self.make_button(panel.left + 300, util_y, 250, 48, "Очистить комнату", "clear_room"),
                self.make_button(panel.left + 570, util_y, 250, 48, "Закрыть HUD", "close"),
            ]
        )

        return buttons

    def draw_text(self, display, text, color, x, y, size=24, center=False):
        font = pygame.font.Font(self.font_path, size)
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            display.blit(text_surface, text_rect)
            return

        display.blit(text_surface, (x, y))

    def draw_button(self, display, button, mouse_pos):
        rect = button["rect"]
        hovered = rect.collidepoint(mouse_pos)
        is_current_floor = button["action"] == f"floor:{self.world.current_floor}"

        fill_color = (42, 46, 56)
        border_color = (116, 102, 88)
        text_color = (240, 235, 225)

        if hovered:
            fill_color = (58, 64, 76)
            border_color = (180, 158, 132)

        if is_current_floor:
            fill_color = (90, 74, 56)
            border_color = (235, 196, 132)

        pygame.draw.rect(display, fill_color, rect, border_radius=10)
        pygame.draw.rect(display, border_color, rect, 3, border_radius=10)
        self.draw_text(
            display,
            button["label"],
            text_color,
            rect.centerx,
            rect.centery,
            24,
            center=True,
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

        if mouse_pressed and not self.clicked:
            for button in self.build_buttons():
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
        pygame.draw.rect(display, (22, 26, 34), panel, border_radius=18)
        pygame.draw.rect(display, (148, 122, 92), panel, 3, border_radius=18)

        self.draw_text(
            display,
            "Панель отладки",
            (255, 228, 188),
            panel.centerx,
            panel.top + 36,
            36,
            center=True,
        )
        self.draw_text(
            display,
            "F1 - скрыть панель",
            (190, 180, 170),
            panel.centerx,
            panel.top + 72,
            20,
            center=True,
        )

        self.draw_text(
            display,
            f"Этаж: {self.world.current_floor}/{self.world.total_floors}    HP: {self.world.player.hp}/{self.world.run_state.max_player_hp}",
            (240, 236, 228),
            panel.left + 30,
            panel.top + 108,
            24,
        )
        self.draw_text(
            display,
            f"Жар: {self.world.run_state.currency}    Враги: {len(self.world.enemies)}    Ожидают: {len(self.world.pending_enemy_spawns)}",
            (220, 214, 204),
            panel.left + 30,
            panel.top + 140,
            22,
        )
        self.draw_text(
            display,
            f"Комната: {self.world.current_room_id}    Заблокирована: {self.world.locked_room_id}",
            (190, 186, 182),
            panel.left + 30,
            panel.top + 168,
            20,
        )

        separator_color = (92, 82, 74)
        pygame.draw.line(display, separator_color, (panel.left + 30, panel.top + 198), (panel.right - 30, panel.top + 198), 2)
        pygame.draw.line(display, separator_color, (panel.left + 30, panel.top + 318), (panel.right - 30, panel.top + 318), 2)
        pygame.draw.line(display, separator_color, (panel.left + 30, panel.top + 438), (panel.right - 30, panel.top + 438), 2)

        self.draw_text(display, "Этажи", (232, 214, 188), panel.left + 30, panel.top + 204, 22)
        self.draw_text(display, "Жар", (232, 214, 188), panel.left + 30, panel.top + 324, 22)
        self.draw_text(
            display,
            f"Шаг изменения: {self.heat_amount}",
            (232, 190, 150),
            panel.left + 120,
            panel.top + 324,
            20,
        )
        self.draw_text(display, "Действия", (232, 214, 188), panel.left + 30, panel.top + 444, 22)

        for button in buttons:
            self.draw_button(display, button, mouse_pos)
