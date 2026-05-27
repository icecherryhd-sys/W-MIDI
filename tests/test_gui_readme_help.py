import unittest
from unittest.mock import patch

from midi_wled_bridge import gui


class GuiReadmeHelpTests(unittest.TestCase):
    def test_open_readme_file_launches_english_user_readme_by_default(self) -> None:
        with patch.object(gui.os, "startfile", create=True) as startfile:
            gui.open_readme_file()

        startfile.assert_called_once_with(gui.readme_txt_path())
        self.assertTrue(gui.readme_txt_path().endswith("README_EN.txt"))


if __name__ == "__main__":
    unittest.main()
