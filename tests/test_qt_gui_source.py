import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class QtGuiSourceTests(unittest.TestCase):
    def test_dashboard_contains_requested_cards_and_actions(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")

        for text in (
            "CONNECTION SETTINGS",
            "COLOR ENGINE",
            "LED / MIDI MAPPING",
            "BRIDGE EXECUTION",
            "Save Config",
            "Reload Ports",
            "Create New Midi Port",
            "Find WLED",
            "START BRIDGE",
            "STOP BRIDGE",
        ):
            self.assertIn(text, source)

    def test_dashboard_uses_reference_palette_and_rounded_cards(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")

        self.assertIn("#050505", source)
        self.assertIn("#202020", source)
        self.assertIn("#a8ff4f", source)
        self.assertIn("#ff9d1e", source)
        self.assertIn("border-radius: 24px", source)
        self.assertIn("class ConnectionPreview", source)
        self.assertIn("class ColorGridPreview", source)
        self.assertIn("class MappingPreview", source)
        self.assertIn("load_velocity_palette_file", source)

    def test_launcher_starts_qt_gui(self) -> None:
        source = (ROOT / "tools" / "windows" / "GuiLauncher.cs").read_text(encoding="utf-8")
        self.assertIn("midi_wled_bridge.qt_gui", source)

    def test_qt_gui_does_not_import_legacy_tkinter_gui(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")

        self.assertNotIn("from midi_wled_bridge.gui import", source)
        self.assertIn("from midi_wled_bridge.app_support import", source)

    def test_midi_port_action_lives_below_find_wled_and_spin_arrows_are_hidden(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")

        self.assertLess(source.index('QPushButton("Find WLED")'), source.index('QPushButton("Create New Midi Port")'))
        self.assertIn("QSpinBox::up-button, QSpinBox::down-button", source)
        self.assertIn('button = QPushButton(str(index))', source)
        self.assertIn('remove_button = QPushButton("-")', source)
        self.assertLess(source.index('remove_button = QPushButton("-")'), source.index('add_button = QPushButton("+")'))
        self.assertIn("palette_file_choices", source)
        self.assertIn('self._combo("velocity_palette_file"', source)
        self.assertIn('QPushButton("\u2600")', source)
        self.assertIn('QPushButton("\u263e")', source)
        self.assertIn('palette_preview.setStyleSheet("background: transparent;")', source)
        self.assertIn("palette_layout = QHBoxLayout(palette_preview)", source)
        self.assertIn("color_header = QHBoxLayout()", source)
        self.assertIn("color_header.addWidget(self.palette_sun)", source)
        self.assertIn("color_header.addWidget(self.palette_moon)", source)
        self.assertIn("self.color_grid_preview.setMinimumHeight(140)", source)
        self.assertIn('QPushButton("POP OUT")', source)
        self.assertIn("mapping_preview_layout.addWidget(popout", source)
        self.assertIn('QPushButton("EDIT LAYOUT")', source)
        self.assertIn('QPushButton("SAVE LAYOUT")', source)
        self.assertIn('QPushButton("IMPORT LAYOUT")', source)
        self.assertIn('QPushButton("RESET LAYOUT")', source)
        self.assertIn('("90° Left", 270)', source)
        self.assertIn('("90° Right", 90)', source)
        self.assertIn('("180° Left", 180)', source)
        self.assertIn('("180° Right", 180)', source)
        self.assertIn("class MappingPopout", source)
        self.assertLess(
            source.index('card.layout.addWidget(palette_preview)'),
            source.index('"MODE",', source.index("def _build_color_card")),
        )


if __name__ == "__main__":
    unittest.main()
