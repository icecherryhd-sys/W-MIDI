import unittest
from pathlib import Path
import tomllib

from midi_wled_bridge import __version__
from midi_wled_bridge import gui
from midi_wled_bridge.qt_model import DEFAULT_BRIDGE_SETTINGS


ROOT = Path(__file__).resolve().parents[1]


class ReleaseBrandingTests(unittest.TestCase):
    def test_release_version_is_consistent(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual("1.2.0", __version__)
        self.assertEqual(__version__, metadata["project"]["version"])

    def test_public_app_name_is_w_midi(self) -> None:
        self.assertEqual("W-MIDI", gui.APP_NAME)

    def test_release_files_exist(self) -> None:
        expected_files = [
            "W-MIDI.exe",
            "pyproject.toml",
            "LICENSE.txt",
            "CHANGELOG.md",
            "RELEASE_CHECKLIST.md",
            "README.md",
            "README_EN.txt",
            "README.txt",
            "assets/windows/w-midi.ico",
            "scripts/windows/start_w_midi.bat",
            "packaging/windows/build_w_midi_launcher.bat",
            "packaging/windows/build_nuitka_release.ps1",
            "packaging/windows/build_release_archive.ps1",
        ]

        missing = [path for path in expected_files if not (ROOT / path).is_file()]

        self.assertEqual([], missing)

    def test_default_palette_is_included(self) -> None:
        palette_path = ROOT / str(DEFAULT_BRIDGE_SETTINGS["velocity_palette_file"])

        self.assertTrue(palette_path.is_file())

    def test_windows_launcher_build_embeds_icon(self) -> None:
        script = (ROOT / "packaging/windows/build_w_midi_launcher.bat").read_text(encoding="utf-8")

        self.assertIn("w-midi.ico", script)
        self.assertIn("/win32icon:", script)

    def test_portable_release_build_uses_pyinstaller_one_folder_layout(self) -> None:
        script = (ROOT / "packaging/windows/build_portable_release.ps1").read_text(encoding="utf-8")

        self.assertIn("--onedir", script)
        self.assertIn("--windowed", script)
        self.assertIn("--contents-directory", script)
        self.assertIn("_internal", script)
        self.assertIn("w-midi.ico", script)
        self.assertIn("midi_wled_bridge\\frozen_entry.py", script)
        self.assertIn(".runtime\\site-packages", script)
        self.assertIn('--hidden-import "rtmidi"', script)
        self.assertIn('--hidden-import "mido.backends.rtmidi"', script)
        self.assertIn('"palettes"', script)
        self.assertIn('"layouts"', script)

    def test_nuitka_release_build_uses_native_standalone_layout(self) -> None:
        script = (ROOT / "packaging/windows/build_nuitka_release.ps1").read_text(encoding="utf-8")

        self.assertIn("--standalone", script)
        self.assertIn("--windows-console-mode=disable", script)
        self.assertIn("--enable-plugin=pyside6", script)
        self.assertIn("--windows-icon-from-ico=", script)
        self.assertIn("--include-module=rtmidi", script)
        self.assertIn("--include-module=mido.backends.rtmidi", script)
        self.assertIn("--include-package=serial", script)
        self.assertIn("--output-filename=W-MIDI.exe", script)
        self.assertIn("$PythonExe", script)
        self.assertIn("midi_wled_bridge\\frozen_entry.py", script)
        self.assertIn('"palettes"', script)
        self.assertIn('"layouts"', script)
        self.assertIn('"assets"', script)

    def test_archive_build_prepares_portable_release_before_compressing(self) -> None:
        script = (ROOT / "packaging/windows/build_release_archive.ps1").read_text(encoding="utf-8")

        self.assertIn("build_nuitka_release.ps1", script)
        self.assertIn("-PythonExe", script)
        self.assertIn("Compress-Archive", script)

    def test_public_docs_describe_portable_release_without_python_install(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        checklist = (ROOT / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")

        self.assertIn("## Portable Windows Release", readme)
        self.assertIn("Keep `W-MIDI.exe` and its bundled files together", readme)
        self.assertIn("Nuitka", readme)
        self.assertNotIn("Install requirements with", checklist)
        self.assertIn("build_nuitka_release.ps1", checklist)

    def test_public_text_uses_w_midi_branding(self) -> None:
        public_files = [
            ROOT / "README.md",
            ROOT / "README_EN.txt",
            ROOT / "README.txt",
            ROOT / "tools/windows/GuiLauncher.cs",
            ROOT / "scripts/windows/start_wled_midi_bridge.bat",
            ROOT / "scripts/windows/start_gui.bat",
        ]

        offenders: list[str] = []
        old_names = (
            "MIDI " + "->" + " WLED Bridge",
            "MIDI to " + "WLED Bridge",
            "WLED MIDI " + "Bridge",
        )
        for path in public_files:
            text = path.read_text(encoding="utf-8")
            for old_name in old_names:
                if old_name in text:
                    offenders.append(f"{path.relative_to(ROOT)}: {old_name}")

        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
