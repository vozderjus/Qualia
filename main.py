import sys
import os
import pygame
from src.core.constants import WIDTH, HEIGHT, FPS, GameState, HeroState, STEP_INTERVAL, COLORS
from src.grid.grid import Grid
from src.grid.tiles import TileType
from src.entities.hero import Hero
from src.logic.interpreter import RuleInterpreter, RULE_MAP

def get_resource_path(relative_path: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RuleGrid v0.2")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    
    grid = Grid(16, 16)
    hero = Hero()
    interpreter = RuleInterpreter()
    
    grid.set_tile(1, 1, TileType.START)
    grid.set_tile(1, 1, TileType.RULE_RIGHT)
    grid.set_tile(2, 1, TileType.RULE_RIGHT)
    grid.set_tile(3, 1, TileType.RULE_DOWN)
    grid.set_tile(3, 2, TileType.RULE_DOWN)
    grid.set_tile(3, 3, TileType.RULE_RIGHT)
    grid.set_tile(4, 3, TileType.RULE_RIGHT)
    grid.set_tile(5, 3, TileType.EXIT)
    grid.set_tile(4, 2, TileType.TRAP)
    
    start_x, start_y = 1, 1
    hero.reset(start_x, start_y)
    interpreter.load_from_grid(grid)

    app_state = GameState.RUNNING
    sim_state = "IDLE"
    debug_mode = False
    last_step_time = pygame.time.get_ticks()
    
    print("[System] SPACE to Play/Pause. F1 for Debug.")

    try:
        while app_state != GameState.EXITING:
            dt = clock.tick(FPS)
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    app_state = GameState.EXITING
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        app_state = GameState.EXITING
                    elif event.key == pygame.K_F1:
                        debug_mode = not debug_mode
                    elif event.key == pygame.K_SPACE:
                        if sim_state == "IDLE" or sim_state == "TERMINATED":
                            hero.reset(start_x, start_y)
                            interpreter.load_from_grid(grid)
                            sim_state = "PLAYING"
                            last_step_time = current_time
                            print("[Sim] Started.")
                        elif sim_state == "PLAYING":
                            sim_state = "IDLE"
                            print("[Sim] Paused.")

            if sim_state == "PLAYING" and current_time - last_step_time >= STEP_INTERVAL * 1000:
                hero_state = interpreter.step(hero, grid)
                last_step_time = current_time
                
                if hero_state in (HeroState.WIN, HeroState.LOSE, HeroState.IDLE):
                    sim_state = "TERMINATED"
                    print(f"[Sim] Finished: {hero_state}")

            screen.fill(COLORS["bg"])

            for y in range(grid.height):
                for x in range(grid.width):
                    tile = grid.get_tile(x, y)
                    color = COLORS["bg"]
                    if tile == TileType.WALL: color = COLORS['wall']
                    elif tile == TileType.START: color = COLORS['start']
                    elif tile == TileType.EXIT: color = COLORS['exit']
                    elif tile in (TileType.RULE_RIGHT, TileType.RULE_UP, TileType.RULE_LEFT, TileType.RULE_DOWN):
                        color = COLORS['rule']
                    elif tile == TileType.TRAP: color = COLORS['trap']
                    
                    pygame.draw.rect(screen, color, grid.to_pixel_rect(x, y))
                    pygame.draw.rect(screen, COLORS["grid_line"], grid.to_pixel_rect(x, y), 1)
            
            hero_color_map = {
                HeroState.IDLE: COLORS["hero_idle"],
                HeroState.MOVING: COLORS["hero_moving"],
                HeroState.LOSE: COLORS["hero_lose"],
                HeroState.WIN: COLORS["hero_win"]
            }

            hero_color = hero_color_map.get(hero.state, (255, 0, 255))
            hero_rect = grid.to_pixel_rect(hero.x, hero.y).inflate(-8, -8)
            pygame.draw.rect(screen, hero_color, hero_rect)
            pygame.draw.rect(screen, (0, 0, 0), hero_rect, 2)

            status_text = f"STATE: {sim_state} | HERO: {hero.state}"
            if sim_state == "TERMINATED":
                status_text += f" | {'YOU WIN!' if hero.state == HeroState.WIN else 'GAME OVER'}"
            prompt_surf = font.render(status_text, True, COLORS["text"])
            screen.blit(prompt_surf, (10, HEIGHT - 30))
            
            if debug_mode:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill(COLORS["debug_overlay"])
                screen.blit(overlay, (0, 0))

                debug_lines = [
                    f"FPS: {int(clock.get_fps())}",
                    f"Hero Pos: ({hero.x}, {hero.y})",
                    f"Hero FSM: {hero.state}",
                    f"Steps: {hero.steps_taken}",
                    f"Queue: {len(interpreter.queue)}",
                    f"Next: {interpreter.current_rule}",
                    f"Tick Delta: {current_time - last_step_time}ms"
                ]
                for i, line in enumerate(debug_lines):
                    screen.blit(font.render(line, True, (240, 240, 240)), (15, 15 + i * 22))

            pygame.display.flip()

    except KeyboardInterrupt:
        print("\n[System] Interrupted.")
    finally:
        pygame.quit()
        print("[System] Clean exit.")

if __name__ == "__main__":
    main()