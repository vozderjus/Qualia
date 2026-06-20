import os

import pygame
from shop_content import SHOP_REROLL_COST
from states.state import State


class ShopMenu(State):
    def __init__(self, game, world):
        super().__init__(game)
        self.world = world
        self.clicked = False
        self.message = ""
        self.message_color = (220, 220, 220)
        self.message_timer = 0.0
        self.font_path = os.path.join("font", "Keleti-Regular.ttf")

        self.overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H), pygame.SRCALPHA)
        self.overlay.fill((6, 8, 14, 210))

        self.panel_rect = pygame.Rect(0, 0, 1020, 560)
        self.panel_rect.center = (self.game.GAME_W // 2, self.game.GAME_H // 2)
        self.card_rects = self.build_card_rects()
        self.reroll_rect = pygame.Rect(self.panel_rect.left + 70, self.panel_rect.bottom - 90, 290, 52)
        self.close_rect = pygame.Rect(self.panel_rect.right - 220, self.panel_rect.bottom - 90, 150, 52)

        self.game.reset_keys()

    def build_card_rects(self):
        card_width = 280
        card_height = 300
        gap = 28
        total_width = card_width * 3 + gap * 2
        start_x = self.panel_rect.centerx - total_width // 2
        y = self.panel_rect.top + 150

        return [
            pygame.Rect(start_x + index * (card_width + gap), y, card_width, card_height)
            for index in range(3)
        ]

    def get_mouse_pos(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        scale_x = self.game.GAME_W / self.game.SCREEN_WIDTH
        scale_y = self.game.GAME_H / self.game.SCREEN_HEIGHT
        return mouse_x * scale_x, mouse_y * scale_y

    def set_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 1.75

    def draw_left_text(self, display, text, color, x, y, size=22):
        font = pygame.font.Font(self.font_path, size)
        text_surface = font.render(text, True, color)
        display.blit(text_surface, (x, y))

    def draw_center_text(self, display, text, color, x, y, size=22):
        font = pygame.font.Font(self.font_path, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        display.blit(text_surface, text_rect)

    def draw_button(self, display, rect, label, mouse_pos, enabled=True):
        hovered = rect.collidepoint(mouse_pos)
        fill_color = (44, 48, 58)
        border_color = (132, 115, 98)
        text_color = (246, 236, 216)

        if not enabled:
            fill_color = (34, 34, 38)
            border_color = (82, 76, 72)
            text_color = (145, 140, 136)
        elif hovered:
            fill_color = (88, 73, 59)
            border_color = (236, 199, 138)

        pygame.draw.rect(display, fill_color, rect, border_radius=12)
        pygame.draw.rect(display, border_color, rect, 3, border_radius=12)
        self.draw_center_text(
            display,
            label,
            text_color,
            rect.centerx,
            rect.centery,
            24,
        )

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

        self.draw_center_text(
            display,
            offer.name,
            text_color,
            rect.centerx,
            rect.top + 42,
            28,
        )
        self.draw_left_text(
            display,
            offer.description,
            (225, 225, 230),
            rect.left + 20,
            rect.top + 104,
            20,
        )
        self.draw_left_text(
            display,
            f"Цена: {offer.cost} жара",
            (255, 190, 80) if affordable else (210, 100, 100),
            rect.left + 20,
            rect.top + 166,
            24,
        )

        buy_rect = pygame.Rect(rect.left + 20, rect.bottom - 74, rect.width - 40, 48)
        self.draw_button(display, buy_rect, "Купить", mouse_pos, affordable)
        return buy_rect

    def update(self, delta_time, actions):
        self.message_timer = max(0.0, self.message_timer - delta_time)

        mouse_pos = self.get_mouse_pos()
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
                    buy_rect = pygame.Rect(rect.left + 20, rect.bottom - 74, rect.width - 40, 48)
                    if buy_rect.collidepoint(mouse_pos):
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
        mouse_pos = self.get_mouse_pos()

        display.blit(self.overlay, (0, 0))
        pygame.draw.rect(display, (20, 26, 34), self.panel_rect, border_radius=20)
        pygame.draw.rect(display, (154, 124, 88), self.panel_rect, 4, border_radius=20)

        self.draw_center_text(
            display,
            "Лавка жаровщика",
            (255, 230, 190),
            self.panel_rect.centerx,
            self.panel_rect.top + 42,
            36,
        )
        self.draw_center_text(
            display,
            f"Жар: {self.world.run_state.currency}",
            (255, 190, 80),
            self.panel_rect.left + 120,
            self.panel_rect.top + 92,
            24,
        )
        self.draw_center_text(
            display,
            f"Обновить ассортимент: {SHOP_REROLL_COST} жара",
            (220, 220, 230),
            self.panel_rect.right - 240,
            self.panel_rect.top + 92,
            22,
        )

        for index, offer in enumerate(self.world.shop_offers):
            self.draw_offer_card(display, offer, self.card_rects[index], mouse_pos)

        self.draw_button(
            display,
            self.reroll_rect,
            "Обновить список",
            mouse_pos,
            self.world.run_state.currency >= SHOP_REROLL_COST,
        )
        self.draw_button(display, self.close_rect, "Уйти", mouse_pos, True)

        if self.message_timer > 0.0:
            self.draw_center_text(
                display,
                self.message,
                self.message_color,
                self.panel_rect.centerx,
                self.panel_rect.bottom - 28,
                22,
            )
