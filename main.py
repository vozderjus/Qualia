import sys
import os
import pygame
from src.core.constants import WIDTH, HEIGHT, FPS, GameState, COLORS


def get_resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def main() -> None:
    pygame.init()
    pygame.display.set_caption("RuleGrid v0.1")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    state = GameState.RUNNING
    debug_mode = False

    print("[System] Pygame initialized. Game Loop started.")

    try:
        while state != GameState.EXITING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    state = GameState.EXITING
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.EXITING
                    elif event.key == pygame.K_F1:
                        debug_mode = not debug_mode
                        print(f"[Debug] Mode: {'ON' if debug_mode else 'OFF'}")

            
            screen.fill(COLORS["bg"])
            
            if debug_mode:
                font = pygame.font.SysFont("consolas", 16)
                fps_text = font.render(f"FPS: {int(clock.get_fps())} | State: {state}", True, COLORS["text"])
                screen.blit(fps_text, (10, 10))

            pygame.display.flip()
            clock.tick(FPS)

    except KeyboardInterrupt:
        print("[System] Interrupted by user.")
    finally:
        pygame.quit()
        print("[System] Clean exit.")

if __name__ == "__main__":
    main()