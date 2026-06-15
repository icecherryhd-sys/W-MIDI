import tempfile
import unittest
from pathlib import Path

from tools.firmware.generate_wled_palette import (
    load_scaled_palette,
    render_palette_header,
)


class FirmwarePaletteExportTests(unittest.TestCase):
    def test_load_scaled_palette_expands_launchpad_range_to_full_rgb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            palette_file = Path(tmp) / "Default"
            palette_file.write_text(
                "0, 0 0 0;\n"
                "1, 7 0 0;\n"
                "2, 0 31 63;\n",
                encoding="utf-8",
            )

            palette = load_scaled_palette(palette_file)

            self.assertEqual((0, 0, 0), palette[0])
            self.assertEqual((28, 0, 0), palette[1])
            self.assertEqual((0, 125, 255), palette[2])

    def test_render_palette_header_contains_128_rgb_entries(self) -> None:
        palette = {0: (0, 0, 0), 1: (28, 0, 0), 127: (255, 255, 255)}

        header = render_palette_header(palette)

        self.assertIn("constexpr uint8_t W_MIDI_PALETTE[128][3]", header)
        self.assertIn("{28, 0, 0}", header)
        self.assertIn("{255, 255, 255}", header)
        self.assertEqual(128, header.count("{") - 1)


if __name__ == "__main__":
    unittest.main()
