from src.grid.tiles import TileType
from src.grid.rules import RULE_REGISTER, is_rule_tile

class Inventory:
    def __init__(self, tiles_config: dict[TileType, int]):
        self.slots: dict[TileType, int] = tiles_config.copy()
        self.selected_tile: TileType | None = None
    
    def can_place(self, tile_type: TileType):
        return self.slots.get(tile_type, 0) > 0
    
    def consume(self, tile_type: str):
        if self.can_place(tile_type):
            self.slots[tile_type] -= 1
            return True
        return False
    
    def get_count(self, tile_type: str):
        return self.slots.get(tile_type, 0)
    
    def refund(self, tile_type: str):
        self.slots[tile_type] = self.get_count(tile_type) + 1
    
    def select_tile(self, tile_type: TileType | None):
        self.selected_tile = tile_type
    
    def get_selected(self):
        return self.selected_tile
    
    def to_dict(self):
        return {
            "slots": {k.value: v for k, v in self.slots.items()},
            "selected": self.get_selected().value if self.get_selected() else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        slots = {TileType(k): v for k, v in data["slots"].items()}
        inv = cls(slots)
        if data.get("selected") is None:
            inv.select_tile(TileType(data["selected"]))
        
        return inv
    
    @classmethod
    def create_default(cls):
        default_slots = {}

        for rule_type, meta in RULE_REGISTER.items():
            default_slots[rule_type.name] = meta.default_count
        return cls(default_slots)
