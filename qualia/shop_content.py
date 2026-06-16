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


def roll_max_hp_offer():
    value = random.randint(18, 28)
    cost = 14 + value // 2
    return ShopOffer(
        effect_type="max_hp",
        name="Закалка тела",
        description=f"Макс. HP +{value}. Сразу лечит на {value}.",
        cost=cost,
        value=value,
    )


def roll_damage_offer():
    value = random.randint(4, 7)
    cost = 16 + value * 2
    return ShopOffer(
        effect_type="bullet_damage",
        name="Жаркий порох",
        description=f"Урон пули +{value}.",
        cost=cost,
        value=value,
    )


def roll_fire_rate_offer():
    milliseconds = random.choice((12, 16, 20, 24))
    cost = 18 + milliseconds // 2
    return ShopOffer(
        effect_type="fire_rate",
        name="Легкий спуск",
        description=f"Кулдаун выстрела -{milliseconds} мс.",
        cost=cost,
        value=milliseconds / 1000,
    )


def roll_shop_offer(effect_type):
    if effect_type == "max_hp":
        return roll_max_hp_offer()
    if effect_type == "bullet_damage":
        return roll_damage_offer()
    if effect_type == "fire_rate":
        return roll_fire_rate_offer()

    raise ValueError(f"Unknown shop effect type: {effect_type}")


def roll_shop_offers():
    return [
        roll_max_hp_offer(),
        roll_damage_offer(),
        roll_fire_rate_offer(),
    ]
