import unittest

import mido

from midi_wled_bridge.bridge import Config, MidiToWledBridge


def make_config(**overrides: object) -> Config:
    data = {
        "wled_ip": "127.0.0.1",
        "port": 21324,
        "midi_port": "loopMIDI",
        "led_count": 200,
        "base_note": 36,
        "color_mode": "fixed",
        "fixed_color": (1, 2, 3),
        "velocity_palette": {127: (255, 255, 255)},
        "midi_channel": None,
        "channel_bank_size": None,
        "verbose": False,
        "frame_interval_ms": 5,
        "midi_read_burst": 64,
    }
    data.update(overrides)
    return Config(**data)


class MidiChannelMappingTests(unittest.TestCase):
    def test_channel_bank_maps_second_channel_after_first_bank(self) -> None:
        bridge = MidiToWledBridge(make_config(channel_bank_size=100))
        try:
            self.assertEqual(0, bridge.note_to_index(36, channel=0))
            self.assertEqual(99, bridge.note_to_index(135, channel=0))
            self.assertEqual(100, bridge.note_to_index(36, channel=1))
            self.assertEqual(199, bridge.note_to_index(135, channel=1))
            self.assertIsNone(bridge.note_to_index(136, channel=1))
        finally:
            bridge.sock.close()

    def test_single_channel_filter_ignores_other_channels(self) -> None:
        bridge = MidiToWledBridge(make_config(midi_channel=2, channel_bank_size=100))
        try:
            bridge.handle_message(mido.Message("note_on", note=36, velocity=127, channel=0))
            bridge.handle_message(mido.Message("note_on", note=36, velocity=127, channel=1))

            self.assertEqual((0, 0, 0), bridge.leds[0])
            self.assertEqual((1, 2, 3), bridge.leds[100])
        finally:
            bridge.sock.close()


if __name__ == "__main__":
    unittest.main()
