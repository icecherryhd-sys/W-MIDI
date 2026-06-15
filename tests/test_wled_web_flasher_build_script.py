import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from tools.firmware import build_wled_web_flasher as builder


class WledWebFlasherBuildScriptTests(unittest.TestCase):
    def test_default_wled_root_points_to_nested_github_source(self):
        self.assertEqual(
            builder.DEFAULT_WLED_ROOT,
            Path(__file__).resolve().parents[1] / "firmware" / "WLED-main" / "WLED-main",
        )

    def test_platformio_command_prefers_pio(self):
        with patch("shutil.which", side_effect=lambda name: "C:/pio.exe" if name == "pio" else None):
            self.assertEqual(builder.find_platformio_command(), ["pio"])

    def test_platformio_command_falls_back_to_python_module(self):
        with patch("shutil.which", return_value=None):
            self.assertEqual(builder.find_platformio_command()[-2:], ["-m", "platformio"])

    def test_merge_command_uses_esp32s3_and_zero_offset_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(builder, "find_file") as find_file, patch.object(
            builder, "_candidate_esptool_commands"
        ) as commands, patch("subprocess.run") as run:
            find_file.side_effect = lambda name, roots: Path(tmp) / name
            commands.return_value = [["esptool"]]
            output_path = Path(tmp) / "merged.bin"

            output = builder.merge_firmware(Path(tmp), "w_midi_esp32s3_usb", output_path)

            self.assertEqual(output, output_path)
            args = run.call_args.args[0]
            self.assertIn("esp32s3", args)
            self.assertIn("merge_bin", args)
            self.assertIn("0x0000", args)
            self.assertIn("0x10000", args)


if __name__ == "__main__":
    unittest.main()
