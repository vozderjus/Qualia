import os
from dataclasses import dataclass
from functools import lru_cache

import pygame

DEFAULT_UI_FONT_PATH = os.path.join("font", "Keleti-Regular.ttf")


@dataclass(frozen=True, slots=True)
class PanelStyle:
    fill_color: tuple[int, int, int]
    border_color: tuple[int, int, int]
    border_radius: int = 18
    border_width: int = 3


@dataclass(frozen=True, slots=True)
class ButtonStyle:
    fill_color: tuple[int, int, int]
    border_color: tuple[int, int, int]
    text_color: tuple[int, int, int]
    hover_fill_color: tuple[int, int, int] | None = None
    hover_border_color: tuple[int, int, int] | None = None
    hover_text_color: tuple[int, int, int] | None = None
    active_fill_color: tuple[int, int, int] | None = None
    active_border_color: tuple[int, int, int] | None = None
    active_text_color: tuple[int, int, int] | None = None
    disabled_fill_color: tuple[int, int, int] | None = None
    disabled_border_color: tuple[int, int, int] | None = None
    disabled_text_color: tuple[int, int, int] | None = None
    border_radius: int = 12
    border_width: int = 3


@lru_cache(maxsize=None)
def load_font(size, path=DEFAULT_UI_FONT_PATH):
    return pygame.font.Font(path, size)


def make_overlay(size, alpha, color=(0, 0, 0)):
    overlay = pygame.Surface(size, pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    return overlay


def get_scaled_mouse_pos(game):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    scale_x = game.GAME_W / game.SCREEN_WIDTH
    scale_y = game.GAME_H / game.SCREEN_HEIGHT
    return mouse_x * scale_x, mouse_y * scale_y


def draw_text(surface, text, color, x, y, font, center=False):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
        return

    surface.blit(text_surface, (x, y))


def draw_panel(surface, rect, style):
    pygame.draw.rect(
        surface,
        style.fill_color,
        rect,
        border_radius=style.border_radius,
    )
    pygame.draw.rect(
        surface,
        style.border_color,
        rect,
        style.border_width,
        border_radius=style.border_radius,
    )


def draw_button(surface, rect, label, mouse_pos, font, style, enabled=True, active=False):
    hovered = enabled and rect.collidepoint(mouse_pos)

    fill_color = style.fill_color
    border_color = style.border_color
    text_color = style.text_color

    if not enabled:
        fill_color = style.disabled_fill_color or fill_color
        border_color = style.disabled_border_color or border_color
        text_color = style.disabled_text_color or text_color
    elif active:
        fill_color = style.active_fill_color or fill_color
        border_color = style.active_border_color or border_color
        text_color = style.active_text_color or text_color
    elif hovered:
        fill_color = style.hover_fill_color or fill_color
        border_color = style.hover_border_color or border_color
        text_color = style.hover_text_color or text_color

    pygame.draw.rect(surface, fill_color, rect, border_radius=style.border_radius)
    pygame.draw.rect(
        surface,
        border_color,
        rect,
        style.border_width,
        border_radius=style.border_radius,
    )
    draw_text(
        surface,
        label,
        text_color,
        rect.centerx,
        rect.centery,
        font,
        center=True,
    )


def wrap_text(text, font, max_width):
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
