from dataclasses import dataclass
from .tiles import TileType

@dataclass(frozen=True)
class Rules:
    name: str
    color: tuple[int, int, int]
    default_count: int
    description: str

RULE_REGISTER: dict = {
    TileType.RULE_RIGHT: Rules("вправо", (100, 200, 100), 5, "Сдвиг вправо на 1"),
    TileType.RULE_LEFT: Rules("влево", (100, 200, 100), 3, "Сдвиг влево на 1"),
    TileType.RULE_DOWN: Rules("вниз", (100, 200, 100), 3, "Сдвиг вниз на 1"),
    TileType.RULE_UP: Rules("вверх", (100, 200, 100), 3, "Сдвиг вверх на 1"),
    TileType.RULE_ROTATE: Rules("поворот", (200, 150, 50), 2, "Поворот направо по часовой"),
    TileType.RULE_JUMP: Rules("прыжок", (255, 100, 50), 1, "Прыжок через 1 клетку"),
}

def get_rule_meta(tile_type: TileType):
    return RULE_REGISTER.get(tile_type)

def is_rule_tile(tile_type: TileType):
    return tile_type in RULE_REGISTER