import pygame

from states.state import State


class GameOver(State):
    def __init__(self, game):
        super().__init__(game)
        self.overlay = pygame.Surface((self.game.GAME_W, self.game.GAME_H), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))

    def update(self, delta_time, actions):
        if actions["start"]:
            self.game.run_state = None
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()

        self.game.reset_keys()

    def render(self, display):
        self.prev_state.render(display)
        display.blit(self.overlay, (0, 0))
        self.game.draw_text(
            display,
            "Вы проиграли",
            (255, 255, 255),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 - 20,
            72,
        )
        self.game.draw_text(
            display,
            "ENTER - в главное меню",
            (220, 220, 220),
            self.game.GAME_W / 2,
            self.game.GAME_H / 2 + 50,
            28,
        )
