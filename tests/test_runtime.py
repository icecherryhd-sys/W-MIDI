import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from midi_wled_bridge import runtime


class RuntimeTests(unittest.TestCase):
    def test_app_root_uses_executable_folder_when_frozen(self) -> None:
        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", r"C:\Portable W-MIDI\W-MIDI.exe"),
        ):
            self.assertEqual(Path(r"C:\Portable W-MIDI"), runtime.app_root())

    def test_bridge_prefix_uses_frozen_executable_cli_mode(self) -> None:
        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", r"C:\Portable W-MIDI\W-MIDI.exe"),
        ):
            self.assertEqual(
                [r"C:\Portable W-MIDI\W-MIDI.exe", "--bridge-cli"],
                runtime.bridge_command_prefix(),
            )

    def test_bridge_prefix_uses_python_module_during_source_development(self) -> None:
        with patch.object(sys, "frozen", False, create=True):
            self.assertEqual(
                [sys.executable, "-m", "midi_wled_bridge.cli"],
                runtime.bridge_command_prefix(),
            )


if __name__ == "__main__":
    unittest.main()
