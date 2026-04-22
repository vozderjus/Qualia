import sys
import os
import pygame
from src.core.constants import WIDTH, HEIGHT, FPS, GameState, COLORS
from src.grid.grid import Grid
from src.grid.tiles import TileType

grid = Grid(16, 16)

grid.set_tile(0, 0, TileType.START)
grid.set_tile(15, 15, TileType.EXIT)
grid.set_tile(8, 8, TileType.WALL)

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
                print(grid.debug_info(highlight_x=8, highlight_y=8))
                for y in range(grid.height):
                    for x in range(grid.width):
                        tile = grid.get_tile(x, y)
                        color = (40, 40, 50)  # EMPTY
                        if tile == TileType.WALL: color = (100, 100, 110)
                        elif tile == TileType.START: color = (76, 175, 80)
                        elif tile == TileType.EXIT: color = (255, 193, 7)
                        pygame.draw.rect(screen, color, grid.to_pixel_rect(x, y))
                        pygame.draw.rect(screen, (60, 60, 70), grid.to_pixel_rect(x, y), 1)

            pygame.display.flip()
            clock.tick(FPS)

    except KeyboardInterrupt:
        print("[System] Interrupted by user.")
    finally:
        pygame.quit()
        print("[System] Clean exit.")

if __name__ == "__main__":
    main()