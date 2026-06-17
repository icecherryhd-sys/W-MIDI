import unittest
from unittest.mock import patch

from midi_wled_bridge import app_support
from midi_wled_bridge import gui


class GuiReadmeHelpTests(unittest.TestCase):
    def test_open_readme_file_launches_english_user_readme_on_windows(self) -> None:
        with (
            patch.object(gui.sys, "platform", "win32"),
            patch.object(gui.os, "startfile", create=True) as startfile,
        ):
            gui.open_readme_file()

        startfile.assert_called_once_with(gui.readme_txt_path())
        self.assertTrue(gui.readme_txt_path().endswith("README_EN.txt"))

    def test_open_readme_file_uses_macos_open_command(self) -> None:
        with (
            patch.object(app_support.sys, "platform", "darwin"),
            patch.object(app_support.subprocess, "run") as run,
        ):
            app_support.open_readme_file()

        run.assert_called_once_with(["open", app_support.readme_txt_path()], check=True)
        self.assertTrue(app_support.readme_txt_path().endswith("README_EN.txt"))


if __name__ == "__main__":
    unittest.main()
