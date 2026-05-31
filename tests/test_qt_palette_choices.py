import tempfile
import unittest
from pathlib import Path

from midi_wled_bridge.qt_gui import normalize_palette_choice, palette_file_choices


class QtPaletteChoiceTests(unittest.TestCase):
    def test_lists_palette_folder_files_as_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            palettes = root / "palettes"
            palettes.mkdir()
            (palettes / "zeta").write_text("", encoding="utf-8")
            (palettes / "alpha.txt").write_text("", encoding="utf-8")
            (palettes / "nested").mkdir()

            choices = palette_file_choices(root)

            self.assertEqual(
                ("palettes/alpha.txt", "palettes/zeta"),
                choices,
            )

    def test_normalizes_saved_windows_paths_for_dropdown_selection(self) -> None:
        self.assertEqual(
            "palettes/velocity_palette.txt",
            normalize_palette_choice(r"palettes\velocity_palette.txt"),
        )


if __name__ == "__main__":
    unittest.main()
