import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from constants import PLAYER_BULLET_DAMAGE_RANGE, PLAYER_MAX_HP
from run_state import RunState


class RunStateTests(unittest.TestCase):
    def test_advance_floor_marks_cleared_and_heals_player(self):
        run_state = RunState.new_run(total_floors=5, starting_hp=PLAYER_MAX_HP)
        run_state.max_player_hp = 140
        run_state.player_hp = 60

        advanced = run_state.advance_floor()

        self.assertTrue(advanced)
        self.assertEqual(run_state.current_floor, 2)
        self.assertEqual(run_state.cleared_floors, [1])
        self.assertEqual(run_state.player_hp, 130)

    def test_player_bullet_damage_range_includes_bonus(self):
        run_state = RunState.new_run(total_floors=5)
        run_state.player_damage_bonus = 3

        self.assertEqual(
            run_state.get_player_bullet_damage_range(),
            (
                PLAYER_BULLET_DAMAGE_RANGE[0] + 3,
                PLAYER_BULLET_DAMAGE_RANGE[1] + 3,
            ),
        )

    def test_purchase_shop_offer_spends_currency_and_stores_upgrade(self):
        run_state = RunState.new_run(total_floors=5)
        run_state.currency = 25
        offer = SimpleNamespace(
            cost=10,
            effect_type="bullet_damage",
            value=4,
            name="Осколки",
        )

        success, message = run_state.purchase_shop_offer(offer)

        self.assertTrue(success)
        self.assertEqual(message, "Урон +4")
        self.assertEqual(run_state.currency, 15)
        self.assertEqual(run_state.player_damage_bonus, 4)
        self.assertIn("Осколки +4", run_state.upgrades)
        self.assertEqual(run_state.shop_purchase_count, 1)

    def test_shop_price_multiplier_grows_with_floor_and_shop_progress(self):
        run_state = RunState.new_run(total_floors=5)
        base_multiplier = run_state.get_shop_price_multiplier()

        run_state.current_floor = 3
        run_state.register_shop_purchase()
        run_state.register_shop_reroll()

        self.assertGreater(
            run_state.get_shop_price_multiplier(),
            base_multiplier,
        )


if __name__ == "__main__":
    unittest.main()
