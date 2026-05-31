import unittest

from midi_wled_bridge.cli import build_config, build_parser
from midi_wled_bridge.palette import scale_palette_to_full


class PaletteScalingTests(unittest.TestCase):
    def test_scales_launchpad_range_to_full_rgb_without_mutating_source(self) -> None:
        palette = {1: (0, 31, 63), 2: (7, 0, 0)}

        scaled = scale_palette_to_full(palette)

        self.assertEqual({1: (0, 125, 255), 2: (28, 0, 0)}, scaled)
        self.assertEqual({1: (0, 31, 63), 2: (7, 0, 0)}, palette)

    def test_clamps_palette_values_that_are_already_above_launchpad_range(self) -> None:
        self.assertEqual({1: (255, 255, 255)}, scale_palette_to_full({1: (64, 120, 255)}))

    def test_cli_sun_mode_scales_palette_used_by_bridge(self) -> None:
        args = build_parser().parse_args(
            [
                "--virtual-midi-udp-port",
                "32000",
                "--velocity-palette",
                "1:0,31,63",
                "--scale-velocity-palette-to-full",
            ]
        )

        config = build_config(args)

        self.assertEqual({1: (0, 125, 255)}, config.velocity_palette)


if __name__ == "__main__":
    unittest.main()
