import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "qualia"))

from game_settings import GameSettings


class GameSettingsTests(unittest.TestCase):
    def test_master_volume_is_clamped_to_valid_range(self):
        settings = GameSettings()

        settings.set_master_volume(1.7)
        self.assertEqual(settings.master_volume, 1.0)

        settings.set_master_volume(-0.2)
        self.assertEqual(settings.master_volume, 0.0)

    def test_sfx_volume_is_clamped_to_valid_range(self):
        settings = GameSettings()

        settings.set_sfx_volume(1.4)
        self.assertEqual(settings.sfx_volume, 1.0)

        settings.set_sfx_volume(-0.5)
        self.assertEqual(settings.sfx_volume, 0.0)

    def test_master_volume_percent_matches_stored_value(self):
        settings = GameSettings()
        settings.set_master_volume(0.42)

        self.assertEqual(settings.get_master_volume_percent(), 42)


if __name__ == "__main__":
    unittest.main()
