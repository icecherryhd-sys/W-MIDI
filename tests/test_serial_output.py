import unittest

from midi_wled_bridge.serial_output import (
    SerialFrameWriter,
    SerialPortInfo,
    build_serial_test_frame,
    describe_serial_error,
    describe_serial_port,
)


class FakeSerial:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, payload: bytes) -> int:
        self.writes.append(bytes(payload))
        return len(payload)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True


class SerialFrameWriterTests(unittest.TestCase):
    def test_coalesces_many_fast_changes_to_latest_pending_frame(self) -> None:
        serial = FakeSerial()
        writer = SerialFrameWriter(serial, max_pending_frames=1)
        writer.writing = True

        writer.send_or_queue([(1, 0, 0)])
        writer.send_or_queue([(2, 0, 0)])
        writer.send_or_queue([(3, 0, 0)])

        self.assertEqual(1, writer.pending_count)

        writer.writing = False
        writer.flush_pending()

        self.assertEqual(1, len(serial.writes))
        self.assertEqual(bytes([3, 0, 0]), serial.writes[0][6:])
        self.assertEqual(0, writer.pending_count)

    def test_send_black_frame_writes_zero_payload_for_configured_leds(self) -> None:
        serial = FakeSerial()
        writer = SerialFrameWriter(serial)

        writer.send_black_frame(3)

        self.assertEqual(bytes([0, 0, 0, 0, 0, 0, 0, 0, 0]), serial.writes[0][6:])

    def test_build_serial_test_frame_sends_visible_low_power_green(self) -> None:
        frame = build_serial_test_frame(2)

        self.assertEqual(b"Ada", frame[:3])
        self.assertEqual(bytes([0, 160, 0, 0, 160, 0]), frame[6:])


class SerialPortDescriptionTests(unittest.TestCase):
    def test_describe_serial_port_includes_usb_metadata_when_available(self) -> None:
        info = SerialPortInfo(
            device="COM4",
            manufacturer="Silicon Labs",
            product="CP210x USB to UART Bridge",
            vid=0x10C4,
            pid=0xEA60,
            serial_number="ABC123",
        )

        self.assertEqual(
            "COM4 - Silicon Labs - CP210x USB to UART Bridge - VID:PID 10C4:EA60 - SN ABC123",
            describe_serial_port(info),
        )

    def test_describe_serial_error_explains_permission_denied(self) -> None:
        error = PermissionError(13, "Access denied", "COM4")

        self.assertEqual(
            "COM4 is already in use or Windows denied access. Stop the bridge, close Serial Monitor/Arduino IDE, or unplug/replug the ESP32, then try again.",
            describe_serial_error("COM4", error),
        )


if __name__ == "__main__":
    unittest.main()
