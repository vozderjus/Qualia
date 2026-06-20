import pygame
from ui_helpers import (ButtonStyle, PanelStyle, draw_button, draw_panel, draw_text,
                        get_scaled_mouse_pos, load_font, make_overlay)

PANEL_SIZE = (960, 560)
PANEL_STYLE = PanelStyle(
    fill_color=(22, 26, 34),
    border_color=(148, 122, 92),
    border_radius=18,
)
BUTTON_STYLE = ButtonStyle(
    fill_color=(42, 46, 56),
    border_color=(116, 102, 88),
    text_color=(240, 235, 225),
    hover_fill_color=(58, 64, 76),
    hover_border_color=(180, 158, 132),
    active_fill_color=(90, 74, 56),
    active_border_color=(235, 196, 132),
    border_radius=10,
)

HEADER_TOP = 36
SUBTITLE_TOP = 72
SUMMARY_TOP = 108
SUMMARY_SECOND_LINE_TOP = 140
ROOM_STATUS_TOP = 168
FLOOR_SECTION_TOP = 220
HEAT_SECTION_TOP = 350
ACTION_SECTION_TOP = 470
SECTION_LINE_Y = (198, 318, 438)
PANEL_PADDING = 30
PREV_NEXT_BUTTON_WIDTH = 170
FLOOR_BUTTON_WIDTH = 82
FLOOR_BUTTON_HEIGHT = 48
FLOOR_BUTTON_GAP = 10
HEAT_STEP_BUTTON_WIDTH = 80
HEAT_ACTION_BUTTON_WIDTH = 250
WIDE_BUTTON_HEIGHT = 48
DEFAULT_HEAT_AMOUNT = 50
HEAT_MIN = 10
HEAT_MAX = 999
HEAT_STEP = 10
FLOOR_LABEL_TOP = 204
HEAT_LABEL_TOP = 324
ACTION_LABEL_TOP = 444


class DebugHUD:
    def __init__(self, game, world):
        self.game = game
        self.world = world
        self.visible = False
        self.clicked = False
        self.heat_amount = DEFAULT_HEAT_AMOUNT
        self.title_font = load_font(36)
        self.body_font = load_font(24)
        self.small_font = load_font(20)
        self.overlay = make_overlay((self.game.GAME_W, self.game.GAME_H), 170)
        self.panel_rect = pygame.Rect(0, 0, *PANEL_SIZE)
        self.panel_rect.center = (self.game.GAME_W // 2, self.game.GAME_H // 2)

    def toggle(self):
        self.visible = not self.visible
        self.clicked = False

    def make_button(self, x, y, width, height, label, action):
        return {
            "rect": pygame.Rect(x, y, width, height),
            "label": label,
            "action": action,
        }

    def build_buttons(self):
        buttons = []
        floor_y = self.panel_rect.top + FLOOR_SECTION_TOP
        buttons.append(
            self.make_button(
                self.panel_rect.left + PANEL_PADDING,
                floor_y + 10,
                PREV_NEXT_BUTTON_WIDTH,
                50,
                "Пред. этаж",
                "prev_floor",
            )
        )
        buttons.append(
            self.make_button(
                self.panel_rect.right - PANEL_PADDING - PREV_NEXT_BUTTON_WIDTH,
                floor_y + 10,
                PREV_NEXT_BUTTON_WIDTH,
                FLOOR_BUTTON_HEIGHT,
                "След. этаж",
                "next_floor",
            )
        )

        total_floors = self.world.total_floors
        row_width = total_floors * FLOOR_BUTTON_WIDTH + (total_floors - 1) * FLOOR_BUTTON_GAP
        start_x = self.panel_rect.centerx - row_width // 2
        for floor_number in range(1, total_floors + 1):
            buttons.append(
                self.make_button(
                    start_x + (floor_number - 1) * (FLOOR_BUTTON_WIDTH + FLOOR_BUTTON_GAP),
                    floor_y + 10,
                    FLOOR_BUTTON_WIDTH,
                    FLOOR_BUTTON_HEIGHT,
                    str(floor_number),
                    f"floor:{floor_number}",
                )
            )

        heat_y = self.panel_rect.top + HEAT_SECTION_TOP
        buttons.extend(
            [
                self.make_button(self.panel_rect.left + PANEL_PADDING, heat_y, HEAT_STEP_BUTTON_WIDTH, WIDE_BUTTON_HEIGHT, "-10", "heat_down"),
                self.make_button(self.panel_rect.left + 122, heat_y, HEAT_STEP_BUTTON_WIDTH, WIDE_BUTTON_HEIGHT, "+10", "heat_up"),
                self.make_button(self.panel_rect.left + 250, heat_y, HEAT_ACTION_BUTTON_WIDTH, WIDE_BUTTON_HEIGHT, "Добавить жар", "add_heat"),
                self.make_button(self.panel_rect.left + 520, heat_y, HEAT_ACTION_BUTTON_WIDTH, WIDE_BUTTON_HEIGHT, "Убрать жар", "remove_heat"),
            ]
        )

        action_y = self.panel_rect.top + ACTION_SECTION_TOP
        buttons.extend(
            [
                self.make_button(self.panel_rect.left + PANEL_PADDING, action_y, 250, WIDE_BUTTON_HEIGHT, "Полное лечение", "heal_full"),
                self.make_button(self.panel_rect.left + 300, action_y, 250, WIDE_BUTTON_HEIGHT, "Очистить комнату", "clear_room"),
                self.make_button(self.panel_rect.left + 570, action_y, 250, WIDE_BUTTON_HEIGHT, "Закрыть HUD", "close"),
            ]
        )

        return buttons

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
            self.heat_amount = max(HEAT_MIN, self.heat_amount - HEAT_STEP)
            return

        if action == "heat_up":
            self.heat_amount = min(HEAT_MAX, self.heat_amount + HEAT_STEP)
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
        mouse_pos = get_scaled_mouse_pos(self.game)
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
        mouse_pos = get_scaled_mouse_pos(self.game)
        buttons = self.build_buttons()

        display.blit(self.overlay, (0, 0))
        draw_panel(display, self.panel_rect, PANEL_STYLE)
        draw_text(
            display,
            "Панель отладки",
            (255, 228, 188),
            self.panel_rect.centerx,
            self.panel_rect.top + HEADER_TOP,
            self.title_font,
            center=True,
        )
        draw_text(
            display,
            "F1 - скрыть панель",
            (190, 180, 170),
            self.panel_rect.centerx,
            self.panel_rect.top + SUBTITLE_TOP,
            self.small_font,
            center=True,
        )
        draw_text(
            display,
            f"Этаж: {self.world.current_floor}/{self.world.total_floors}    HP: {self.world.player.hp}/{self.world.run_state.max_player_hp}",
            (240, 236, 228),
            self.panel_rect.left + PANEL_PADDING,
            self.panel_rect.top + SUMMARY_TOP,
            self.body_font,
        )
        draw_text(
            display,
            f"Жар: {self.world.run_state.currency}    Враги: {len(self.world.enemies)}    Ожидают: {len(self.world.pending_enemy_spawns)}",
            (220, 214, 204),
            self.panel_rect.left + PANEL_PADDING,
            self.panel_rect.top + SUMMARY_SECOND_LINE_TOP,
            self.body_font,
        )
        draw_text(
            display,
            f"Комната: {self.world.current_room_id}    Заблокирована: {self.world.locked_room_id}",
            (190, 186, 182),
            self.panel_rect.left + PANEL_PADDING,
            self.panel_rect.top + ROOM_STATUS_TOP,
            self.small_font,
        )

        separator_color = (92, 82, 74)
        for line_y in SECTION_LINE_Y:
            pygame.draw.line(
                display,
                separator_color,
                (self.panel_rect.left + PANEL_PADDING, self.panel_rect.top + line_y),
                (self.panel_rect.right - PANEL_PADDING, self.panel_rect.top + line_y),
                2,
            )

        draw_text(display, "Этажи", (232, 214, 188), self.panel_rect.left + PANEL_PADDING, self.panel_rect.top + FLOOR_LABEL_TOP, self.body_font)
        draw_text(display, "Жар", (232, 214, 188), self.panel_rect.left + PANEL_PADDING, self.panel_rect.top + HEAT_LABEL_TOP, self.body_font)
        draw_text(
            display,
            f"Шаг изменения: {self.heat_amount}",
            (232, 190, 150),
            self.panel_rect.left + 120,
            self.panel_rect.top + HEAT_LABEL_TOP,
            self.small_font,
        )
        draw_text(display, "Действия", (232, 214, 188), self.panel_rect.left + PANEL_PADDING, self.panel_rect.top + ACTION_LABEL_TOP, self.body_font)

        for button in buttons:
            draw_button(
                display,
                button["rect"],
                button["label"],
                mouse_pos,
                self.body_font,
                BUTTON_STYLE,
                active=button["action"] == f"floor:{self.world.current_floor}",
            )
