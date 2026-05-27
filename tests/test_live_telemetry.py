import io
import time
import unittest
from contextlib import redirect_stdout

from midi_wled_bridge.bridge import Config, MidiToWledBridge
from midi_wled_bridge.gui import BridgeGuiApp


def make_config() -> Config:
    return Config(
        wled_ip="127.0.0.1",
        port=21324,
        midi_port="loopMIDI",
        led_count=8,
        base_note=36,
        color_mode="fixed",
        fixed_color=(1, 2, 3),
        velocity_palette={127: (255, 255, 255)},
        midi_channel=None,
        channel_bank_size=None,
        verbose=False,
        frame_interval_ms=5,
        midi_read_burst=64,
    )


class LiveTelemetryTests(unittest.TestCase):
    def test_bridge_emits_parseable_telemetry(self) -> None:
        bridge = MidiToWledBridge(make_config())
        try:
            bridge.telemetry_started_at = time.monotonic() - 1.1
            bridge.telemetry_last_emit = bridge.telemetry_started_at
            bridge.telemetry_frames = 3
            bridge.telemetry_midi_messages = 5

            output = io.StringIO()
            with redirect_stdout(output):
                bridge.emit_telemetry_if_needed(force=True)

            line = output.getvalue()
            self.assertIn("TELEMETRY", line)
            self.assertIn("fps=", line)
            self.assertIn("midi_per_s=", line)
            self.assertIn("udp_per_s=", line)
            self.assertIn("last_frame_ms=", line)
        finally:
            bridge.sock.close()

    def test_gui_updates_telemetry_labels_from_bridge_line(self) -> None:
        app = BridgeGuiApp()
        try:
            app._handle_bridge_output("TELEMETRY fps=60.0 midi_per_s=12.0 udp_per_s=60.0 last_frame_ms=4")

            self.assertEqual("60.0", app._telemetry_vars["fps"].get())
            self.assertEqual("12.0", app._telemetry_vars["midi"].get())
            self.assertEqual("60.0", app._telemetry_vars["udp"].get())
            self.assertEqual("4ms", app._telemetry_vars["last_frame"].get())
        finally:
            app.root.destroy()

    def test_verbose_midi_logging_is_throttled(self) -> None:
        config = make_config()
        config.verbose = True
        bridge = MidiToWledBridge(config)
        try:
            bridge.verbose_last_emit = time.monotonic()

            output = io.StringIO()
            with redirect_stdout(output):
                for index in range(20):
                    bridge._verbose_log(f"line {index}")

            self.assertEqual("", output.getvalue())
            self.assertEqual(20, bridge.verbose_suppressed)
        finally:
            bridge.sock.close()


if __name__ == "__main__":
    unittest.main()
