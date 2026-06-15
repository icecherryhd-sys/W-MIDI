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

    def test_app_root_uses_release_folder_for_macos_app_bundle(self) -> None:
        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(
                sys,
                "executable",
                r"C:\release\W-MIDI-v1.2.0-macOS-arm64\W-MIDI.app\Contents\MacOS\W-MIDI",
            ),
        ):
            self.assertEqual(
                Path(r"C:\release\W-MIDI-v1.2.0-macOS-arm64"),
                runtime.app_root(),
            )

    def test_bridge_prefix_uses_frozen_executable_cli_mode(self) -> None:
        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "executable", r"C:\Portable W-MIDI\W-MIDI.exe"),
        ):
            self.assertEqual(
                [r"C:\Portable W-MIDI\W-MIDI.exe", "--bridge-cli"],
                runtime.bridge_command_prefix(),
            )

    def test_bridge_prefix_uses_nuitka_executable_cli_mode(self) -> None:
        original = runtime.__dict__.get("__compiled__")
        runtime.__dict__["__compiled__"] = object()
        try:
            with (
                patch.object(sys, "frozen", False, create=True),
                patch.object(sys, "executable", r"C:\Portable W-MIDI\W-MIDI.exe"),
            ):
                self.assertEqual(
                    [r"C:\Portable W-MIDI\W-MIDI.exe", "--bridge-cli"],
                    runtime.bridge_command_prefix(),
                )
        finally:
            if original is None:
                runtime.__dict__.pop("__compiled__", None)
            else:
                runtime.__dict__["__compiled__"] = original

    def test_bridge_prefix_uses_argv_exe_when_nuitka_executable_is_missing(self) -> None:
        original = runtime.__dict__.get("__compiled__")
        runtime.__dict__["__compiled__"] = object()
        try:
            with (
                patch.object(sys, "frozen", False, create=True),
                patch.object(sys, "executable", r"C:\Missing Python\python.exe"),
                patch.object(sys, "argv", [r"C:\Portable W-MIDI\W-MIDI.exe"]),
                patch.object(Path, "is_file", lambda path: str(path) == r"C:\Portable W-MIDI\W-MIDI.exe"),
            ):
                self.assertEqual(
                    [r"C:\Portable W-MIDI\W-MIDI.exe", "--bridge-cli"],
                    runtime.bridge_command_prefix(),
                )
        finally:
            if original is None:
                runtime.__dict__.pop("__compiled__", None)
            else:
                runtime.__dict__["__compiled__"] = original

    def test_bridge_prefix_uses_python_module_during_source_development(self) -> None:
        with patch.object(sys, "frozen", False, create=True):
            self.assertEqual(
                [sys.executable, "-m", "midi_wled_bridge.cli"],
                runtime.bridge_command_prefix(),
            )


if __name__ == "__main__":
    unittest.main()
