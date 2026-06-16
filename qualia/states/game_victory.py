import pygame
from states.state import State


class GameVictory(State):
    def __init__(self, game):
        super().__init__(game)
        self.overlay = pygame.Surface(
            (self.game.GAME_W, self.game.GAME_H),
            pygame.SRCALPHA,
        )
        self.overlay.fill((8, 10, 18, 185))

    def update(self, delta_time, actions):
        if actions["start"]:
            self.game.run_state = None
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()

        self.game.reset_keys()

    def render(self, display):
        self.prev_state.render(display)
        display.blit(self.overlay, (0, 0))

        run_state = self.game.run_state
        total_upgrades = 0 if run_state is None else len(run_state.upgrades)
        total_heat = 0 if run_state is None else run_state.currency

        self.game.draw_text(
            display,
            "Вы победили",
            (255, 244, 215),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 - 60,
            72,
        )
        self.game.draw_text(
            display,
            f"Жар собрано: {total_heat}",
            (255, 190, 90),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 + 8,
            30,
        )
        self.game.draw_text(
            display,
            f"Улучшений куплено: {total_upgrades}",
            (220, 228, 255),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 + 46,
            28,
        )
        self.game.draw_text(
            display,
            "ENTER - в главное меню",
            (225, 225, 225),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 + 106,
            28,
        )
