import os

import pygame
from constants import SETTINGS_CREDITS_LINES, SETTINGS_LORE_PARAGRAPHS
from states.state import State


class SettingsMenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.clicked = bool(pygame.mouse.get_pressed()[0])
        self.current_section = "lore"
        self.frozen_background = None
        self.section_scroll = {
            "lore": 0,
            "credits": 0,
        }
        self.active_slider = None
        self.scrollbar_dragging = False
        self.scroll_drag_offset = 0
        self.font_path = os.path.join("font", "Keleti-Regular.ttf")
        self.title_font = pygame.font.Font(
            self.font_path,
            38,
        )
        self.body_font = pygame.font.Font(
            self.font_path,
            22,
        )
        self.small_font = pygame.font.Font(
            self.font_path,
            18,
        )
        self.overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        self.panel_rect = pygame.Rect(0, 0, 920, 660)
        self.panel_rect.center = (self.game.GAME_W // 2, self.game.GAME_H // 2)
        self.buttons = self.build_buttons()

    def enter_state(self):
        super().enter_state()
        self.frozen_background = self.game.game_canvas.copy()

    def build_buttons(self):
        panel = self.panel_rect
        footer_y = panel.bottom - 86

        return {
            "lore": pygame.Rect(panel.left + 40, footer_y, 180, 50),
            "credits": pygame.Rect(panel.left + 236, footer_y, 180, 50),
            "back": pygame.Rect(panel.right - 220, footer_y, 180, 50),
        }

    def update(self, delta_time, actions):
        if actions["pause"]:
            self.exit_state()
            self.game.reset_keys()
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        section_layout = self.get_section_layout()
        slider_layouts = self.get_slider_layouts()

        if mouse_pressed and self.active_slider is not None:
            self.update_slider_from_mouse(self.active_slider, mouse_pos[0], slider_layouts)

        if mouse_pressed and self.scrollbar_dragging:
            self.update_scroll_from_drag(mouse_pos[1], section_layout)

        if mouse_pressed and not self.clicked:
            for action, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.handle_action(action)
                    break
            else:
                if not self.handle_slider_press(mouse_pos, slider_layouts):
                    self.handle_scrollbar_press(mouse_pos, section_layout)

        if not mouse_pressed:
            self.active_slider = None
            self.scrollbar_dragging = False

        self.clicked = mouse_pressed
        self.game.reset_keys()

    def handle_action(self, action):
        if action == "lore":
            self.current_section = "lore"
            self.active_slider = None
            self.scrollbar_dragging = False
            return

        if action == "credits":
            self.current_section = "credits"
            self.active_slider = None
            self.scrollbar_dragging = False
            return

        if action == "back":
            self.active_slider = None
            self.scrollbar_dragging = False
            self.exit_state()

    def draw_text(self, display, text, color, x, y, font, center=False):
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            display.blit(text_surface, text_rect)
            return

        display.blit(text_surface, (x, y))

    def wrap_text(self, text, font, max_width):
        if not text:
            return [""]

        stripped_text = text.strip()
        if not stripped_text:
            return [""]

        words = stripped_text.split()
        if not words:
            return [""]

        lines = []
        current_line = words[0]

        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines

    def normalize_section_source(self, source_lines):
        if isinstance(source_lines, str):
            return [source_lines]

        return list(source_lines)

    def get_content_rect(self):
        return pygame.Rect(
            self.panel_rect.left + 40,
            self.panel_rect.top + 286,
            self.panel_rect.width - 80,
            230,
        )

    def get_slider_layouts(self):
        panel = self.panel_rect
        slider_left = panel.left + 360
        slider_width = 360
        slider_height = 10
        first_row_y = panel.top + 112
        second_row_y = first_row_y + 72

        slider_specs = {
            "master_volume": {
                "label": "Громкость музыки",
                "value": self.game.settings.master_volume,
                "value_percent": self.game.settings.get_master_volume_percent(),
                "row_y": first_row_y,
                "color": (110, 178, 212),
            },
            "sfx_volume": {
                "label": "Громкость эффектов",
                "value": self.game.settings.sfx_volume,
                "value_percent": self.game.settings.get_sfx_volume_percent(),
                "row_y": second_row_y,
                "color": (112, 182, 120),
            },
        }

        layouts = {}
        for slider_name, slider_data in slider_specs.items():
            bar_rect = pygame.Rect(
                slider_left,
                slider_data["row_y"] + 12,
                slider_width,
                slider_height,
            )
            fill_rect = bar_rect.copy()
            fill_rect.width = int(bar_rect.width * slider_data["value"])
            thumb_x = bar_rect.left + int(bar_rect.width * slider_data["value"])
            thumb_x = max(bar_rect.left, min(thumb_x, bar_rect.right))
            thumb_rect = pygame.Rect(0, 0, 18, 26)
            thumb_rect.center = (thumb_x, bar_rect.centery)

            layouts[slider_name] = {
                **slider_data,
                "bar_rect": bar_rect,
                "fill_rect": fill_rect,
                "thumb_rect": thumb_rect,
            }

        return layouts

    def set_slider_value(self, slider_name, value):
        clamped_value = max(0.0, min(1.0, value))

        if slider_name == "master_volume":
            self.game.settings.set_master_volume(clamped_value)
        elif slider_name == "sfx_volume":
            self.game.settings.set_sfx_volume(clamped_value)
        else:
            return

        self.game.settings.apply_audio_stub(self.game)

    def update_slider_from_mouse(self, slider_name, mouse_x, slider_layouts):
        slider_layout = slider_layouts.get(slider_name)
        if slider_layout is None:
            return

        bar_rect = slider_layout["bar_rect"]
        progress = (mouse_x - bar_rect.left) / bar_rect.width
        self.set_slider_value(slider_name, progress)

    def handle_slider_press(self, mouse_pos, slider_layouts):
        for slider_name, slider_layout in slider_layouts.items():
            thumb_hitbox = slider_layout["thumb_rect"].inflate(12, 12)
            if thumb_hitbox.collidepoint(mouse_pos) or slider_layout["bar_rect"].collidepoint(mouse_pos):
                self.active_slider = slider_name
                self.update_slider_from_mouse(slider_name, mouse_pos[0], slider_layouts)
                return True

        return False

    def get_section_lines(self, max_width):
        if self.current_section == "lore":
            header = "Лор"
            source_lines = SETTINGS_LORE_PARAGRAPHS
        else:
            header = "Титры"
            source_lines = SETTINGS_CREDITS_LINES

        body_lines = []
        for line in self.normalize_section_source(source_lines):
            if not line:
                body_lines.append("")
                continue

            body_lines.extend(self.wrap_text(line, self.body_font, max_width))
            if self.current_section == "lore":
                body_lines.append("")

        if self.current_section == "lore" and body_lines and body_lines[-1] == "":
            body_lines.pop()

        return header, body_lines

    def get_section_layout(self):
        content_rect = self.get_content_rect()
        viewport_rect = pygame.Rect(
            content_rect.left + 16,
            content_rect.top + 56,
            content_rect.width - 56,
            content_rect.height - 72,
        )
        scrollbar_rect = pygame.Rect(
            content_rect.right - 20,
            viewport_rect.top,
            8,
            viewport_rect.height,
        )

        header, body_lines = self.get_section_lines(viewport_rect.width - 10)
        line_step = 28
        content_height = max(
            viewport_rect.height,
            len(body_lines) * line_step + 8,
        )
        max_scroll = max(0, content_height - viewport_rect.height)
        scroll_value = min(self.section_scroll[self.current_section], max_scroll)
        self.section_scroll[self.current_section] = scroll_value

        thumb_height = scrollbar_rect.height
        thumb_y = scrollbar_rect.top

        if max_scroll > 0:
            thumb_height = max(
                36,
                int(scrollbar_rect.height * (viewport_rect.height / content_height)),
            )
            track_range = scrollbar_rect.height - thumb_height
            thumb_y = scrollbar_rect.top + int(
                track_range * (scroll_value / max_scroll)
            )

        thumb_rect = pygame.Rect(
            scrollbar_rect.left,
            thumb_y,
            scrollbar_rect.width,
            thumb_height,
        )

        return {
            "content_rect": content_rect,
            "viewport_rect": viewport_rect,
            "scrollbar_rect": scrollbar_rect,
            "thumb_rect": thumb_rect,
            "header": header,
            "body_lines": body_lines,
            "line_step": line_step,
            "content_height": content_height,
            "max_scroll": max_scroll,
            "scroll_value": scroll_value,
        }

    def set_scroll_value(self, value, max_scroll):
        self.section_scroll[self.current_section] = max(
            0,
            min(int(value), max_scroll),
        )

    def handle_scrollbar_press(self, mouse_pos, section_layout):
        if section_layout["max_scroll"] <= 0:
            return

        thumb_rect = section_layout["thumb_rect"]
        scrollbar_rect = section_layout["scrollbar_rect"]

        if thumb_rect.collidepoint(mouse_pos):
            self.scrollbar_dragging = True
            self.scroll_drag_offset = mouse_pos[1] - thumb_rect.top
            return

        if scrollbar_rect.collidepoint(mouse_pos):
            self.scrollbar_dragging = True
            self.scroll_drag_offset = thumb_rect.height // 2
            self.update_scroll_from_drag(mouse_pos[1], section_layout)

    def update_scroll_from_drag(self, mouse_y, section_layout):
        max_scroll = section_layout["max_scroll"]
        if max_scroll <= 0:
            self.scrollbar_dragging = False
            return

        scrollbar_rect = section_layout["scrollbar_rect"]
        thumb_rect = section_layout["thumb_rect"]
        track_range = scrollbar_rect.height - thumb_rect.height

        if track_range <= 0:
            self.set_scroll_value(0, max_scroll)
            return

        thumb_top = mouse_y - self.scroll_drag_offset
        thumb_top = max(scrollbar_rect.top, min(thumb_top, scrollbar_rect.bottom - thumb_rect.height))
        progress = (thumb_top - scrollbar_rect.top) / track_range
        self.set_scroll_value(progress * max_scroll, max_scroll)

    def draw_button(self, display, action, label, hovered, active=False):
        rect = self.buttons[action]
        fill_color = (44, 48, 60)
        border_color = (160, 146, 120)
        text_color = (242, 236, 225)

        if hovered:
            fill_color = (58, 64, 78)
            border_color = (220, 192, 144)

        if active:
            fill_color = (82, 70, 54)
            border_color = (240, 206, 148)

        pygame.draw.rect(display, fill_color, rect, border_radius=10)
        pygame.draw.rect(display, border_color, rect, 3, border_radius=10)
        self.draw_text(
            display,
            label,
            text_color,
            rect.centerx,
            rect.centery,
            self.body_font,
            center=True,
        )

    def render_volume_row(self, display, slider_layout, hovered):
        label_y = slider_layout["row_y"]
        bar_rect = slider_layout["bar_rect"]
        fill_rect = slider_layout["fill_rect"]
        thumb_rect = slider_layout["thumb_rect"]
        track_color = (24, 28, 36)
        border_color = (220, 208, 186)
        thumb_color = slider_layout["color"]

        if hovered or self.active_slider is not None:
            border_color = (240, 220, 184)

        self.draw_text(
            display,
            slider_layout["label"],
            (255, 241, 213),
            self.panel_rect.left + 40,
            label_y,
            self.body_font,
        )
        self.draw_text(
            display,
            f"{slider_layout['value_percent']}%",
            (245, 245, 245),
            self.panel_rect.right - 88,
            label_y,
            self.body_font,
            center=True,
        )

        pygame.draw.rect(display, track_color, bar_rect, border_radius=8)
        if fill_rect.width > 0:
            pygame.draw.rect(display, slider_layout["color"], fill_rect, border_radius=8)
        pygame.draw.rect(display, border_color, bar_rect, 2, border_radius=8)
        pygame.draw.rect(display, thumb_color, thumb_rect, border_radius=9)
        pygame.draw.rect(display, (245, 236, 214), thumb_rect, 2, border_radius=9)

    def render_section_content(self, display):
        section_layout = self.get_section_layout()
        content_rect = section_layout["content_rect"]
        viewport_rect = section_layout["viewport_rect"]
        scrollbar_rect = section_layout["scrollbar_rect"]
        thumb_rect = section_layout["thumb_rect"]
        header = section_layout["header"]
        body_lines = section_layout["body_lines"]
        line_step = section_layout["line_step"]
        scroll_value = section_layout["scroll_value"]
        content_height = section_layout["content_height"]

        pygame.draw.rect(display, (24, 28, 36), content_rect, border_radius=12)
        pygame.draw.rect(display, (110, 116, 130), content_rect, 2, border_radius=12)

        self.draw_text(
            display,
            header,
            (255, 229, 188),
            content_rect.left + 16,
            content_rect.top + 14,
            self.body_font,
        )

        text_surface = pygame.Surface(
            (viewport_rect.width, content_height),
            pygame.SRCALPHA,
        )

        y = 0
        for line in body_lines:
            if line:
                line_surface = self.body_font.render(line, True, (228, 228, 232))
                text_surface.blit(line_surface, (0, y))
            y += line_step

        display.blit(
            text_surface,
            viewport_rect.topleft,
            area=pygame.Rect(
                0,
                scroll_value,
                viewport_rect.width,
                viewport_rect.height,
            ),
        )

        pygame.draw.rect(display, (36, 40, 50), scrollbar_rect, border_radius=6)
        if section_layout["max_scroll"] > 0:
            thumb_color = (224, 194, 144)
            if self.scrollbar_dragging:
                thumb_color = (245, 214, 164)
            pygame.draw.rect(display, thumb_color, thumb_rect, border_radius=6)
        else:
            pygame.draw.rect(display, (88, 92, 104), thumb_rect, border_radius=6)

    def render(self, display):
        if self.frozen_background is not None:
            display.blit(self.frozen_background, (0, 0))
        elif self.prev_state is not None:
            self.prev_state.render(display)
        else:
            display.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()

        display.blit(self.overlay, (0, 0))
        pygame.draw.rect(display, (18, 22, 30), self.panel_rect, border_radius=18)
        pygame.draw.rect(display, (164, 144, 112), self.panel_rect, 3, border_radius=18)

        self.draw_text(
            display,
            "Настройки",
            (255, 239, 205),
            self.panel_rect.centerx,
            self.panel_rect.top + 34,
            self.title_font,
            center=True,
        )

        self.render_volume_block(display)
        self.render_section_content(display)

        self.draw_button(
            display,
            "lore",
            "Лор",
            self.buttons["lore"].collidepoint(mouse_pos),
            active=self.current_section == "lore",
        )
        self.draw_button(
            display,
            "credits",
            "Credits",
            self.buttons["credits"].collidepoint(mouse_pos),
            active=self.current_section == "credits",
        )
        self.draw_button(
            display,
            "back",
            "Назад",
            self.buttons["back"].collidepoint(mouse_pos),
        )

    def render_volume_block(self, display):
        mouse_pos = pygame.mouse.get_pos()
        slider_layouts = self.get_slider_layouts()

        for slider_name in ("master_volume", "sfx_volume"):
            slider_layout = slider_layouts[slider_name]
            hovered = (
                slider_layout["bar_rect"].collidepoint(mouse_pos)
                or slider_layout["thumb_rect"].inflate(12, 12).collidepoint(mouse_pos)
            )
            self.render_volume_row(display, slider_layout, hovered)
