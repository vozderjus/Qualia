from enum import IntEnum, auto
from dataclasses import dataclass

class TileType(IntEnum):
    EMPTY = 0
    WALL = 1
    START = 2
    EXIT = 3
    TRAP = 4
    RULE_RIGHT = 5
    RULE_UP = 6
    RULE_LEFT = 7
    RULE_DOWN = 8

@dataclass(frozen=True)
class TileProperties:
    is_solid: bool = False
    is_hazardous: bool = False
    is_rule: bool = False
    is_goal: bool = False
    is_start: bool = False

TILE_PROPERTIES: dict[TileType, TileProperties] = {
    TileType.EMPTY:       TileProperties(),
    TileType.WALL:        TileProperties(is_solid=True),
    TileType.START:       TileProperties(is_start=True),
    TileType.EXIT:        TileProperties(is_goal=True),
    TileType.TRAP:        TileProperties(is_hazardous=True),
    TileType.RULE_RIGHT:  TileProperties(is_rule=True),
    TileType.RULE_UP:     TileProperties(is_rule=True),
    TileType.RULE_LEFT:   TileProperties(is_rule=True),
    TileType.RULE_DOWN:   TileProperties(is_rule=True),
}

def get_tile_props(tile: TileType) -> TileProperties:
    """Быстрый доступ к клеткам

    Args:
        tile (TileType): тип определенной клетки

    Returns:
        TileProperties: состояние клетки
    """
    return TILE_PROPERTIES.get(tile, TILE_PROPERTIES[TileType.EMPTY])