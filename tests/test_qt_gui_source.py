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
            "Create Midi Port",
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

    def test_connection_actions_and_spin_arrows_are_hidden(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")
        connection_card_source = source[
            source.index("def _build_connection_card") : source.index("def _build_color_card")
        ]

        self.assertIn('QPushButton("Create Midi Port")', connection_card_source)
        self.assertIn('QPushButton("Test Connection")', connection_card_source)
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
        mapping_card_source = source[
            source.index("def _build_mapping_card") : source.index("def _build_execution_card")
        ]
        self.assertIn('QPushButton("Edit Custom Led Layout")', mapping_card_source)
        self.assertNotIn("mapping_preview_layout.addWidget(self.mapping_preview", mapping_card_source)
        self.assertNotIn('QPushButton("POP OUT")', source)
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

    def test_connection_card_opens_separate_wireless_and_wired_setup_dialogs(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")
        connection_card_source = source[
            source.index("def _build_connection_card") : source.index("def _build_color_card")
        ]

        self.assertIn('self._combo("output_mode", ["Wireless", "Wired"])', source)
        self.assertNotIn('QPushButton("Settings")', source)
        self.assertIn('QPushButton("Wireless Setup")', source)
        self.assertIn('QPushButton("Wired Setup")', source)
        self.assertIn('QPushButton("Test Connection")', connection_card_source)
        self.assertIn('QPushButton("Create Midi Port")', connection_card_source)
        self.assertNotIn("ConnectionPreview()", connection_card_source)
        self.assertIn("def _open_wireless_setup", source)
        self.assertIn("def _open_wired_setup", source)
        self.assertIn("self.wireless_settings_dialog", source)
        self.assertIn("self.wired_settings_dialog", source)
        self.assertIn("def _refresh_connection_mode", source)
        self.assertIn('QPushButton("Find COM Ports")', source)
        self.assertIn("def _test_serial_connection", source)
        self.assertIn("Serial test frame sent", source)
        self.assertIn("Found {len(self.serial_port_infos)} COM port", source)
        self.assertIn("describe_serial_error", source)
        self.assertIn("build_serial_test_frame", source)
        self.assertIn("Serial test frame sent", source)
        self.assertIn("test_duration_s = 4.0", source)
        self.assertIn("while time.monotonic() < deadline", source)

    def test_setup_dialog_bottom_buttons_are_save_buttons(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")
        connection_card_source = source[
            source.index("def _build_connection_card") : source.index("def _build_color_card")
        ]

        self.assertIn('wireless_save = QPushButton("Save")', connection_card_source)
        self.assertIn('wired_save = QPushButton("Save")', connection_card_source)
        self.assertNotIn('QPushButton("Close")', connection_card_source)
        self.assertIn("wireless_save.clicked.connect(self._save_wireless_setup)", source)
        self.assertIn("wired_save.clicked.connect(self._save_wired_setup)", source)

    def test_create_midi_port_prompts_for_loopmidi_when_driver_is_missing(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")
        create_port_source = source[
            source.index("def _create_virtual_port") : source.index("def _start")
        ]

        self.assertIn("virtual_midi_driver_available", source)
        self.assertIn("driver_available, driver_message", create_port_source)
        self.assertIn("QMessageBox.warning", create_port_source)
        self.assertLess(
            create_port_source.index("virtual_midi_driver_available"),
            create_port_source.index("PortNameDialog.get_name"),
        )

    def test_palette_preview_is_loaded_when_selected_bridge_loads(self) -> None:
        source = (ROOT / "midi_wled_bridge" / "qt_gui.py").read_text(encoding="utf-8")
        load_selected_source = source[
            source.index("def _load_selected") : source.index("def _set_palette_scale_to_full")
        ]

        self.assertIn('self.fields["velocity_palette_file"]', load_selected_source)
        self.assertIn("self.color_grid_preview.set_palette_file", load_selected_source)


if __name__ == "__main__":
    unittest.main()
