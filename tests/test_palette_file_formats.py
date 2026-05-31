import tempfile
import unittest
from pathlib import Path

from midi_wled_bridge.palette import load_velocity_palette_file


class PaletteFileFormatTests(unittest.TestCase):
    def test_loads_zero_based_space_separated_palette_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mat1jaczyyyPalette"
            path.write_text(
                "0, 0 0 0;\n"
                "1, 15 0 0;\n"
                "127, 63 63 63;\n",
                encoding="utf-8",
            )

            palette = load_velocity_palette_file(str(path))

            self.assertEqual((0, 0, 0), palette[0])
            self.assertEqual((15, 0, 0), palette[1])
            self.assertEqual((63, 63, 63), palette[127])


if __name__ == "__main__":
    unittest.main()
