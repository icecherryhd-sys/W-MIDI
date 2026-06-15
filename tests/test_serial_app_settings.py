import unittest

from midi_wled_bridge.app_support import build_subprocess_argv
from midi_wled_bridge.qt_model import DEFAULT_BRIDGE_SETTINGS


class SerialAppSettingsTests(unittest.TestCase):
    def test_qt_subprocess_args_include_serial_settings_when_selected(self) -> None:
        settings = dict(DEFAULT_BRIDGE_SETTINGS)
        settings.update(
            {
                "output_mode": "serial",
                "serial_port": "COM4",
                "serial_baudrate": 921600,
                "serial_fps": 90,
                "serial_auto_reconnect": False,
                "serial_blackout_on_disconnect": False,
            }
        )

        argv = build_subprocess_argv(settings)

        self.assertIn("--output-mode", argv)
        self.assertIn("serial", argv)
        self.assertIn("--serial-port", argv)
        self.assertIn("COM4", argv)
        self.assertIn("--serial-baudrate", argv)
        self.assertIn("921600", argv)
        self.assertIn("--serial-fps", argv)
        self.assertIn("90", argv)
        self.assertIn("--no-serial-auto-reconnect", argv)
        self.assertIn("--serial-leave-on-disconnect", argv)

    def test_qt_subprocess_args_do_not_require_serial_port_for_udp_mode(self) -> None:
        settings = dict(DEFAULT_BRIDGE_SETTINGS)

        argv = build_subprocess_argv(settings)

        self.assertIn("--output-mode", argv)
        self.assertIn("udp", argv)
        self.assertNotIn("--serial-port", argv)

    def test_qt_subprocess_args_normalize_combined_output_mode_to_udp(self) -> None:
        settings = dict(DEFAULT_BRIDGE_SETTINGS)
        settings.update({"output_mode": "both", "serial_port": "COM4"})

        argv = build_subprocess_argv(settings)

        output_mode_index = argv.index("--output-mode") + 1
        self.assertEqual("udp", argv[output_mode_index])
        self.assertNotIn("--serial-port", argv)


if __name__ == "__main__":
    unittest.main()
