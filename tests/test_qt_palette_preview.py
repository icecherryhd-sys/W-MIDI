import tempfile
import unittest
from pathlib import Path

from midi_wled_bridge.qt_gui import (
    brighten_preview_rgb,
    load_preview_palette,
    palette_grid_position,
)


class QtPalettePreviewTests(unittest.TestCase):
    def test_preview_loads_velocity_rgb_values_from_selected_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            palette = Path(tmp) / "palette.txt"
            palette.write_text("1:1,2,3\n127:250,251,252\n", encoding="utf-8")

            colors = load_preview_palette(str(palette))

            self.assertEqual((1, 2, 3), colors[0])
            self.assertEqual((250, 251, 252), colors[-1])
            self.assertEqual(128, len(colors))

    def test_grid_positions_use_four_bottom_up_blocks(self) -> None:
        self.assertEqual((0, 7), palette_grid_position(0))
        self.assertEqual((3, 7), palette_grid_position(3))
        self.assertEqual((0, 6), palette_grid_position(4))
        self.assertEqual((3, 0), palette_grid_position(31))
        self.assertEqual((4, 7), palette_grid_position(32))
        self.assertEqual((15, 0), palette_grid_position(127))

    def test_preview_brightness_preserves_black_and_lifts_dim_colors(self) -> None:
        self.assertEqual((0, 0, 0), brighten_preview_rgb((0, 0, 0)))
        self.assertEqual((60, 60, 60), brighten_preview_rgb((15, 15, 15)))
        self.assertEqual((252, 124, 60), brighten_preview_rgb((63, 31, 15)))


if __name__ == "__main__":
    unittest.main()
