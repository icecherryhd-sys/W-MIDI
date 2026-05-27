import unittest
from pathlib import Path

from midi_wled_bridge import gui


ROOT = Path(__file__).resolve().parents[1]


class ReleaseBrandingTests(unittest.TestCase):
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
        ]

        missing = [path for path in expected_files if not (ROOT / path).is_file()]

        self.assertEqual([], missing)

    def test_windows_launcher_build_embeds_icon(self) -> None:
        script = (ROOT / "packaging/windows/build_w_midi_launcher.bat").read_text(encoding="utf-8")

        self.assertIn("w-midi.ico", script)
        self.assertIn("/win32icon:", script)

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
