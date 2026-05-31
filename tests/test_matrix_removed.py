import unittest
from contextlib import redirect_stderr
from io import StringIO

from midi_wled_bridge.cli import build_parser
from midi_wled_bridge.gui import DEFAULT_GUI_SETTINGS, build_subprocess_argv


class MatrixRemovalTests(unittest.TestCase):
    def test_gui_start_args_do_not_include_legacy_matrix_options(self) -> None:
        settings = dict(DEFAULT_GUI_SETTINGS)
        settings.update(
            {
                "midi_port": "loopMIDI",
                "matrix_width": "8",
                "matrix_height": "8",
                "serpentine": True,
            }
        )

        argv = build_subprocess_argv(settings)

        self.assertNotIn("--matrix-width", argv)
        self.assertNotIn("--matrix-height", argv)
        self.assertNotIn("--serpentine", argv)

    def test_cli_rejects_removed_matrix_options(self) -> None:
        parser = build_parser()

        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["--matrix-width", "8", "--matrix-height", "8"])


if __name__ == "__main__":
    unittest.main()
