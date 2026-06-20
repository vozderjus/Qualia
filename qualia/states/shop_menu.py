import pygame
from shop_content import SHOP_REROLL_COST
from states.state import State
from ui_helpers import (ButtonStyle, PanelStyle, draw_button, draw_panel, draw_text,
                        get_scaled_mouse_pos, load_font, make_overlay, wrap_text)

PANEL_SIZE = (1020, 560)
PANEL_STYLE = PanelStyle(
    fill_color=(20, 26, 34),
    border_color=(154, 124, 88),
    border_radius=20,
    border_width=4,
)
ACTION_BUTTON_STYLE = ButtonStyle(
    fill_color=(44, 48, 58),
    border_color=(132, 115, 98),
    text_color=(246, 236, 216),
    hover_fill_color=(88, 73, 59),
    hover_border_color=(236, 199, 138),
    disabled_fill_color=(34, 34, 38),
    disabled_border_color=(82, 76, 72),
    disabled_text_color=(145, 140, 136),
)

CARD_WIDTH = 280
CARD_HEIGHT = 300
CARD_GAP = 28
CARD_TOP = 150
BUY_BUTTON_MARGIN_X = 20
BUY_BUTTON_HEIGHT = 48
BUY_BUTTON_BOTTOM_OFFSET = 74
BUY_BUTTON_LABEL = "Купить"
DESCRIPTION_TOP = 104
DESCRIPTION_LINE_STEP = 24
DESCRIPTION_MAX_LINES = 3
PRICE_TOP = 182
REROLL_BUTTON_SIZE = (290, 52)
CLOSE_BUTTON_SIZE = (150, 52)
FOOTER_BUTTON_Y_OFFSET = 90
MESSAGE_DURATION = 1.75
REROLL_BUTTON_LEFT_OFFSET = 70
CLOSE_BUTTON_RIGHT_OFFSET = 220
CURRENCY_LABEL_CENTER_OFFSET = 120
REROLL_INFO_CENTER_OFFSET = 240
MESSAGE_BOTTOM_OFFSET = 28


class ShopMenu(State):
    def __init__(self, game, world):
        super().__init__(game)
        self.world = world
        self.clicked = False
        self.message = ""
        self.message_color = (220, 220, 220)
        self.message_timer = 0.0
        self.title_font = load_font(36)
        self.heading_font = load_font(28)
        self.body_font = load_font(22)
        self.small_font = load_font(20)
        self.button_font = load_font(24)
        self.overlay = make_overlay((self.game.GAME_W, self.game.GAME_H), 210, color=(6, 8, 14))
        self.panel_rect = pygame.Rect(0, 0, *PANEL_SIZE)
        self.panel_rect.center = (self.game.GAME_W // 2, self.game.GAME_H // 2)
        self.card_rects = self.build_card_rects()
        self.reroll_rect = pygame.Rect(
            self.panel_rect.left + REROLL_BUTTON_LEFT_OFFSET,
            self.panel_rect.bottom - FOOTER_BUTTON_Y_OFFSET,
            *REROLL_BUTTON_SIZE,
        )
        self.close_rect = pygame.Rect(
            self.panel_rect.right - CLOSE_BUTTON_RIGHT_OFFSET,
            self.panel_rect.bottom - FOOTER_BUTTON_Y_OFFSET,
            *CLOSE_BUTTON_SIZE,
        )
        self.game.reset_keys()

    def build_card_rects(self):
        total_width = CARD_WIDTH * 3 + CARD_GAP * 2
        start_x = self.panel_rect.centerx - total_width // 2
        y = self.panel_rect.top + CARD_TOP
        return [
            pygame.Rect(start_x + index * (CARD_WIDTH + CARD_GAP), y, CARD_WIDTH, CARD_HEIGHT)
            for index in range(3)
        ]

    def get_buy_rect(self, card_rect):
        return pygame.Rect(
            card_rect.left + BUY_BUTTON_MARGIN_X,
            card_rect.bottom - BUY_BUTTON_BOTTOM_OFFSET,
            card_rect.width - BUY_BUTTON_MARGIN_X * 2,
            BUY_BUTTON_HEIGHT,
        )

    def set_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = MESSAGE_DURATION

    def draw_offer_card(self, display, offer, rect, mouse_pos):
        hovered = rect.collidepoint(mouse_pos)
        affordable = self.world.run_state.currency >= offer.cost

        fill_color = (33, 39, 50)
        border_color = (110, 125, 156)
        text_color = (245, 245, 245)

        if hovered and affordable:
            fill_color = (55, 70, 94)
            border_color = (240, 214, 152)
        elif hovered:
            fill_color = (48, 42, 44)
            border_color = (168, 92, 96)

        pygame.draw.rect(display, fill_color, rect, border_radius=16)
        pygame.draw.rect(display, border_color, rect, 4, border_radius=16)

        draw_text(
            display,
            offer.name,
            text_color,
            rect.centerx,
            rect.top + 42,
            self.heading_font,
            center=True,
        )

        description_lines = wrap_text(
            offer.description,
            self.small_font,
            rect.width - BUY_BUTTON_MARGIN_X * 2,
        )[:DESCRIPTION_MAX_LINES]
        for line_index, line in enumerate(description_lines):
            draw_text(
                display,
                line,
                (225, 225, 230),
                rect.left + BUY_BUTTON_MARGIN_X,
                rect.top + DESCRIPTION_TOP + line_index * DESCRIPTION_LINE_STEP,
                self.small_font,
            )

        draw_text(
            display,
            f"Цена: {offer.cost} жара",
            (255, 190, 80) if affordable else (210, 100, 100),
            rect.left + BUY_BUTTON_MARGIN_X,
            rect.top + PRICE_TOP,
            self.body_font,
        )

        buy_rect = self.get_buy_rect(rect)
        draw_button(
            display,
            buy_rect,
            BUY_BUTTON_LABEL,
            mouse_pos,
            self.button_font,
            ACTION_BUTTON_STYLE,
            enabled=affordable,
        )
        return buy_rect

    def update(self, delta_time, actions):
        self.message_timer = max(0.0, self.message_timer - delta_time)

        mouse_pos = get_scaled_mouse_pos(self.game)
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if mouse_pressed and not self.clicked:
            if self.close_rect.collidepoint(mouse_pos):
                self.exit_state()
                self.game.reset_keys()
                return

            if self.reroll_rect.collidepoint(mouse_pos):
                success, message = self.world.try_reroll_shop_offers()
                if success:
                    self.set_message(message, (155, 245, 180))
                else:
                    self.set_message(message, (245, 135, 135))
            else:
                for index, rect in enumerate(self.card_rects):
                    if self.get_buy_rect(rect).collidepoint(mouse_pos):
                        success, message = self.world.try_buy_shop_offer(index)
                        if success:
                            self.set_message(message, (155, 245, 180))
                        else:
                            self.set_message(message, (245, 135, 135))
                        break

            self.clicked = True

        if not mouse_pressed:
            self.clicked = False

        self.game.reset_keys()

    def render(self, display):
        self.prev_state.render(display)
        mouse_pos = get_scaled_mouse_pos(self.game)

        display.blit(self.overlay, (0, 0))
        draw_panel(display, self.panel_rect, PANEL_STYLE)
        draw_text(
            display,
            "Лавка жаровщика",
            (255, 230, 190),
            self.panel_rect.centerx,
            self.panel_rect.top + 42,
            self.title_font,
            center=True,
        )
        draw_text(
            display,
            f"Жар: {self.world.run_state.currency}",
            (255, 190, 80),
            self.panel_rect.left + CURRENCY_LABEL_CENTER_OFFSET,
            self.panel_rect.top + 92,
            self.body_font,
            center=True,
        )
        draw_text(
            display,
            f"Обновить ассортимент: {SHOP_REROLL_COST} жара",
            (220, 220, 230),
            self.panel_rect.right - REROLL_INFO_CENTER_OFFSET,
            self.panel_rect.top + 92,
            self.body_font,
            center=True,
        )

        for index, offer in enumerate(self.world.shop_offers):
            self.draw_offer_card(display, offer, self.card_rects[index], mouse_pos)

        draw_button(
            display,
            self.reroll_rect,
            "Обновить список",
            mouse_pos,
            self.button_font,
            ACTION_BUTTON_STYLE,
            enabled=self.world.run_state.currency >= SHOP_REROLL_COST,
        )
        draw_button(
            display,
            self.close_rect,
            "Уйти",
            mouse_pos,
            self.button_font,
            ACTION_BUTTON_STYLE,
        )

        if self.message_timer > 0.0:
            draw_text(
                display,
                self.message,
                self.message_color,
                self.panel_rect.centerx,
                self.panel_rect.bottom - MESSAGE_BOTTOM_OFFSET,
                self.body_font,
                center=True,
            )
