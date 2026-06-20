import sys
import unittest
from pathlib import Path
from unittest.mock import Mock


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

    def test_apply_audio_stub_delegates_to_game_audio_sync(self):
        settings = GameSettings()
        game = Mock()

        settings.apply_audio_stub(game)

        game.apply_audio_settings.assert_called_once()


if __name__ == "__main__":
    unittest.main()
