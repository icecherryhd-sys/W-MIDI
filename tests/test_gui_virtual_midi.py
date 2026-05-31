import unittest
from pathlib import Path

from midi_wled_bridge.gui import DEFAULT_GUI_SETTINGS, build_subprocess_argv


class GuiVirtualMidiTests(unittest.TestCase):
    def test_gui_start_args_include_virtual_midi_udp_port_when_selected(self) -> None:
        settings = dict(DEFAULT_GUI_SETTINGS)
        settings.update({"midi_port": "W-MIDI", "virtual_midi_udp_port": 32001})

        argv = build_subprocess_argv(settings)

        self.assertIn("--virtual-midi-udp-port", argv)
        self.assertIn("32001", argv)

    def test_gui_contains_requested_create_port_dialog_labels(self) -> None:
        source = Path("midi_wled_bridge/gui.py").read_text(encoding="utf-8")

        self.assertIn('"Create New Midi Port"', source)
        self.assertIn('"Cancel"', source)
        self.assertIn('"Add"', source)
        self.assertIn('value="W-MIDI"', source)

    def test_gui_start_args_include_palette_scaling_when_sun_mode_is_selected(self) -> None:
        settings = dict(DEFAULT_GUI_SETTINGS)
        settings["scale_velocity_palette_to_full"] = True

        argv = build_subprocess_argv(settings)

        self.assertIn("--scale-velocity-palette-to-full", argv)


if __name__ == "__main__":
    unittest.main()
