import unittest

from midi_wled_bridge.adalight import build_adalight_frame


class AdalightFrameTests(unittest.TestCase):
    def test_header_for_32_leds_uses_led_count_minus_one_and_checksum(self) -> None:
        frame = build_adalight_frame([(0, 0, 0)] * 32)

        self.assertEqual(b"Ada", frame[:3])
        self.assertEqual(0, frame[3])
        self.assertEqual(31, frame[4])
        self.assertEqual(0 ^ 31 ^ 0x55, frame[5])
        self.assertEqual(102, len(frame))

    def test_header_supports_multiple_led_counts(self) -> None:
        for led_count in (1, 32, 255, 256, 300):
            with self.subTest(led_count=led_count):
                frame = build_adalight_frame([(0, 0, 0)] * led_count)
                encoded_count = led_count - 1
                high = (encoded_count >> 8) & 0xFF
                low = encoded_count & 0xFF

                self.assertEqual(high, frame[3])
                self.assertEqual(low, frame[4])
                self.assertEqual(high ^ low ^ 0x55, frame[5])
                self.assertEqual(6 + led_count * 3, len(frame))

    def test_payload_preserves_rgb_order_and_led_order(self) -> None:
        frame = build_adalight_frame(
            [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (1, 2, 3),
            ]
        )

        self.assertEqual(bytes([255, 0, 0, 0, 255, 0, 0, 0, 255, 1, 2, 3]), frame[6:])

    def test_payload_clamps_invalid_color_values(self) -> None:
        frame = build_adalight_frame([(-5, 128.8, 999)])

        self.assertEqual(bytes([0, 128, 255]), frame[6:])

    def test_empty_frame_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_adalight_frame([])


if __name__ == "__main__":
    unittest.main()
