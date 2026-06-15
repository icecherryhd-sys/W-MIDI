import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
USERMOD = ROOT / "firmware/wled-w-midi/usermods/W_MIDI_USB/usermod_w_midi_usb.h"
USERMOD_CPP = ROOT / "firmware/wled-w-midi/usermods/W_MIDI_USB/w_midi_usb.cpp"
LIBRARY_JSON = ROOT / "firmware/wled-w-midi/usermods/W_MIDI_USB/library.json"
PLATFORMIO = ROOT / "firmware/wled-w-midi/platformio_override.ini"


class WledUsermodSourceTests(unittest.TestCase):
    def test_usermod_uses_native_usb_midi_and_wled_strip_buffer(self) -> None:
        source = USERMOD.read_text(encoding="utf-8")

        self.assertIn("#include <USB.h>", source)
        self.assertIn('#include "esp32-hal-tinyusb.h"', source)
        self.assertIn("tinyusb_enable_interface(USB_INTERFACE_MIDI", source)
        self.assertIn("TUD_MIDI_DESCRIPTOR", source)
        self.assertIn("tud_midi_packet_read", source)
        self.assertIn("strip.setPixelColor", source)
        self.assertIn("strip.show()", source)
        self.assertNotIn("#include <FastLED", source)
        self.assertNotIn("#include <Adafruit_NeoPixel", source)
        self.assertNotIn("delay(", source)

    def test_usermod_defines_midi_mapping_timeout_and_config_hooks(self) -> None:
        source = USERMOD.read_text(encoding="utf-8")

        self.assertIn("noteToIndex", source)
        self.assertIn("handleNoteOn", source)
        self.assertIn("handleNoteOff", source)
        self.assertIn("usbTimeoutMs", source)
        self.assertIn("lastUsbMidiMs", source)
        self.assertIn("addToConfig", source)
        self.assertIn("readFromConfig", source)
        self.assertIn("USERMOD_ID_W_MIDI_USB", source)

    def test_platformio_override_targets_esp32_s3_and_enables_usermod(self) -> None:
        text = PLATFORMIO.read_text(encoding="utf-8")

        self.assertIn("default_envs = w_midi_esp32s3_usb", text)
        self.assertIn("extends = env:esp32s3_4M_qspi", text)
        self.assertIn("custom_usermods =", text)
        self.assertIn("W_MIDI_USB", text)
        self.assertIn("-D USERMOD_W_MIDI_USB", text)
        self.assertIn("-D ARDUINO_USB_MODE=0", text)
        self.assertIn("-D CONFIG_TINYUSB_MIDI_ENABLED=1", text)

    def test_usermod_is_a_platformio_library_and_self_registers(self) -> None:
        manifest = LIBRARY_JSON.read_text(encoding="utf-8")
        source = USERMOD_CPP.read_text(encoding="utf-8")

        self.assertIn('"name": "W_MIDI_USB"', manifest)
        self.assertIn('"libArchive": false', manifest)
        self.assertIn('#include "usermod_w_midi_usb.h"', source)
        self.assertIn("static WMidiUsbUsermod wMidiUsbUsermod", source)
        self.assertIn("REGISTER_USERMOD(wMidiUsbUsermod)", source)


if __name__ == "__main__":
    unittest.main()
