import argparse
import unittest

from midi_wled_bridge.cli import build_config, build_parser, validate_args


class SerialCliTests(unittest.TestCase):
    def test_parser_accepts_serial_output_settings(self) -> None:
        args = build_parser().parse_args(
            [
                "--output-mode",
                "serial",
                "--serial-port",
                "COM4",
                "--serial-baudrate",
                "921600",
                "--serial-fps",
                "90",
                "--no-serial-auto-reconnect",
                "--serial-leave-on-disconnect",
            ]
        )

        self.assertEqual("serial", args.output_mode)
        self.assertEqual("COM4", args.serial_port)
        self.assertEqual(921600, args.serial_baudrate)
        self.assertEqual(90, args.serial_fps)
        self.assertFalse(args.serial_auto_reconnect)
        self.assertFalse(args.serial_blackout_on_disconnect)

    def test_build_config_keeps_serial_settings_without_resolving_midi_for_validation(self) -> None:
        args = argparse.Namespace(
            wled_ip="127.0.0.1",
            port=21324,
            midi_port="Fake Port",
            led_count=32,
            base_note=36,
            color_mode="fixed",
            fixed_color=(1, 2, 3),
            velocity_palette={127: (255, 255, 255)},
            velocity_palette_file="",
            scale_velocity_palette_to_full=False,
            midi_channel=None,
            channel_bank_size=None,
            verbose=False,
            frame_interval_ms=5,
            midi_read_burst=64,
            virtual_midi_udp_port=12000,
            emit_led_frames=False,
            output_mode="serial",
            serial_port="COM4",
            serial_baudrate=460800,
            serial_fps=30,
            serial_auto_reconnect=False,
            serial_blackout_on_disconnect=False,
            serial_start_delay_ms=1500,
        )

        config = build_config(args)

        self.assertEqual("serial", config.output_mode)
        self.assertEqual("COM4", config.serial_port)
        self.assertEqual(460800, config.serial_baudrate)
        self.assertEqual(30, config.serial_fps)
        self.assertFalse(config.serial_auto_reconnect)
        self.assertFalse(config.serial_blackout_on_disconnect)
        self.assertEqual(1500, config.serial_start_delay_ms)

    def test_validate_args_rejects_serial_mode_without_port(self) -> None:
        args = build_parser().parse_args(["--output-mode", "serial", "--serial-port", ""])

        self.assertEqual(2, validate_args(args))

    def test_parser_rejects_combined_udp_and_serial_output(self) -> None:
        with self.assertRaises(SystemExit):
            build_parser().parse_args(["--output-mode", "both"])


if __name__ == "__main__":
    unittest.main()
