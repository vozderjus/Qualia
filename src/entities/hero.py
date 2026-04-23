from src.core.constants import HeroState, COLORS
from src.grid.grid import Grid

class Hero:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.state = HeroState.IDLE
        self.steps_taken = 0

    def reset(self, start_x: int, start_y: int) -> None:
        self.x, self.y = start_x, start_y
        self.state = HeroState.IDLE
        self.steps_taken = 0

    def set_state(self, new_state: str) -> None:
        self.state = new_state

    def try_execute_rule(self, grid: Grid, dx: int, dy: int) -> str:
        """

        Args:
            grid (Grid): сетка
            dx (int): куда хотим перейти по x
            dy (int): куда хотим перейти по y

        Returns:
            str: состояние на момент после перехода: 'MOVING', 'WIN', 'LOSE' или None
        """
        if self.state not in (HeroState.IDLE, HeroState.MOVING):
            return self.state
        
        nx, ny = self.x + dx, self.y + dy
        self.steps_taken += 1
        
        if not grid.is_valid(nx, ny) or grid.is_solid(nx, ny):
            self.set_state(HeroState.LOSE)
            return HeroState.LOSE
   
        if grid.is_hazardous(nx, ny):
            self.set_state(HeroState.LOSE)
            return HeroState.LOSE

        self.x, self.y = nx, ny

        if grid.get_tile(nx, ny) == 3:
            self.set_state(HeroState.WIN)
            return HeroState.WIN

        if self.steps_taken > 64:
            self.set_state(HeroState.LOSE)
            return HeroState.LOSE
        
        self.set_state(HeroState.MOVING)
        return HeroState.MOVING