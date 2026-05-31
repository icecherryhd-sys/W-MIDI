import argparse
import unittest

from midi_wled_bridge.cli import build_config
from midi_wled_bridge.gui import DEFAULT_GUI_SETTINGS, build_subprocess_argv


class MidiChannelCliGuiTests(unittest.TestCase):
    def test_gui_start_args_include_channel_settings(self) -> None:
        settings = dict(DEFAULT_GUI_SETTINGS)
        settings.update(
            {
                "midi_port": "loopMIDI",
                "midi_channel": "2",
                "channel_bank_size": "100",
            }
        )

        argv = build_subprocess_argv(settings)

        self.assertIn("--midi-channel", argv)
        self.assertIn("2", argv)
        self.assertIn("--channel-bank-size", argv)
        self.assertIn("100", argv)

    def test_build_config_keeps_channel_settings(self) -> None:
        args = argparse.Namespace(
            wled_ip="127.0.0.1",
            port=21324,
            midi_port="Fake Port",
            led_count=200,
            base_note=36,
            color_mode="fixed",
            fixed_color=(1, 2, 3),
            velocity_palette={127: (255, 255, 255)},
            velocity_palette_file="",
            midi_channel=2,
            channel_bank_size=100,
            verbose=False,
            frame_interval_ms=5,
            midi_read_burst=64,
        )

        from unittest.mock import patch

        with patch("midi_wled_bridge.cli.resolve_port_name", return_value="Fake Port"):
            config = build_config(args)

        self.assertEqual(2, config.midi_channel)
        self.assertEqual(100, config.channel_bank_size)


if __name__ == "__main__":
    unittest.main()
