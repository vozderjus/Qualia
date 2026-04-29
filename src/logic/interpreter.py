from collections import deque
from src.grid.grid import Grid
from src.grid.tiles import TileType
from src.entities.hero import Hero
from src.core.constants import HeroState

RULE_MAP = {
    TileType.RULE_RIGHT: (1, 0),
    TileType.RULE_LEFT: (-1, 0),
    TileType.RULE_UP: (0, -1),
    TileType.RULE_DOWN: (0, 1),
}

class RuleInterpreter:
    def __init__(self):
        self.queue: deque[tuple[int, int]] = deque()
        self.current_rule: tuple[int, int] | None = None

    def load_from_grid(self, grid: Grid) -> None:
        self.queue.clear()
        for y in range(grid.height):
            for x in range(grid.width):
                tile = grid.get_tile(x, y)
                if tile in RULE_MAP:
                    self.queue.append(RULE_MAP[tile])
        self.current_rule = None

    def reset(self) -> None:
        self.queue.clear()
        self.current_rule = None

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def step(self, hero: Hero, grid: Grid) -> str:
        current_tile = grid.get_tile(hero.x, hero.y)
        
        if current_tile == TileType.EXIT:
            self.current_rule = None
            return HeroState.WIN
        
        if current_tile not in RULE_MAP:
            self.current_rule = None
            return HeroState.IDLE

        self.current_rule = self.queue.popleft()
        return hero.try_execute_rule(grid, *self.current_rule)