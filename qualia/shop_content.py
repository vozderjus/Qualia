import math
import random
from dataclasses import dataclass

SHOP_REROLL_COST = 12


@dataclass(frozen=True, slots=True)
class ShopOffer:
    effect_type: str
    name: str
    description: str
    cost: int
    value: int | float


def scale_shop_cost(base_cost, price_multiplier):
    return max(1, int(math.ceil(base_cost * price_multiplier)))


def roll_max_hp_offer(price_multiplier=1.0):
    value = random.randint(18, 28)
    cost = scale_shop_cost(14 + value // 2, price_multiplier)
    return ShopOffer(
        effect_type="max_hp",
        name="Закалка тела",
        description=f"Макс. HP +{value}. Сразу лечит на {value}.",
        cost=cost,
        value=value,
    )


def roll_damage_offer(price_multiplier=1.0):
    value = random.randint(4, 7)
    cost = scale_shop_cost(16 + value * 2, price_multiplier)
    return ShopOffer(
        effect_type="bullet_damage",
        name="Жаркий порох",
        description=f"Урон пули +{value}.",
        cost=cost,
        value=value,
    )


def roll_fire_rate_offer(price_multiplier=1.0):
    milliseconds = random.choice((12, 16, 20, 24))
    cost = scale_shop_cost(18 + milliseconds // 2, price_multiplier)
    return ShopOffer(
        effect_type="fire_rate",
        name="Легкий спуск",
        description=f"Кулдаун выстрела -{milliseconds} мс.",
        cost=cost,
        value=milliseconds / 1000,
    )


def roll_shop_offer(effect_type, price_multiplier=1.0):
    if effect_type == "max_hp":
        return roll_max_hp_offer(price_multiplier)
    if effect_type == "bullet_damage":
        return roll_damage_offer(price_multiplier)
    if effect_type == "fire_rate":
        return roll_fire_rate_offer(price_multiplier)

    raise ValueError(f"Unknown shop effect type: {effect_type}")


def roll_shop_offers(price_multiplier=1.0):
    return [
        roll_max_hp_offer(price_multiplier),
        roll_damage_offer(price_multiplier),
        roll_fire_rate_offer(price_multiplier),
    ]
