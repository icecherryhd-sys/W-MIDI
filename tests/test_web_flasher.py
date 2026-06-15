import json
import tempfile
import unittest
from pathlib import Path

from tools.firmware.prepare_web_flasher import build_manifest, prepare_web_flasher


ROOT = Path(__file__).resolve().parents[1]


class WebFlasherTests(unittest.TestCase):
    def test_installer_page_uses_esp_web_tools(self):
        html = (ROOT / "web-flasher" / "index.html").read_text(encoding="utf-8")
        self.assertIn("W-MIDI USB Installer", html)
        self.assertIn("https://unpkg.com/esp-web-tools@10/dist/web/install-button.js?module", html)
        self.assertIn('<esp-web-install-button manifest="manifest.json">', html)
        self.assertIn("ESP32-S3 auswählen und installieren", html)

    def test_manifest_targets_esp32s3_merged_binary(self):
        manifest = json.loads((ROOT / "web-flasher" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "W-MIDI USB Underlight")
        self.assertTrue(manifest["new_install_prompt_erase"])
        self.assertEqual(manifest["new_install_improv_wait_time"], 0)
        self.assertEqual(manifest["builds"][0]["chipFamily"], "ESP32-S3")
        self.assertEqual(
            manifest["builds"][0]["parts"],
            [{"path": "firmware/w-midi-usb-esp32s3-merged.bin", "offset": 0}],
        )

    def test_manifest_builder_matches_static_manifest_shape(self):
        manifest = build_manifest(version="1.2.3")
        self.assertEqual(manifest["version"], "1.2.3")
        self.assertEqual(manifest["builds"][0]["chipFamily"], "ESP32-S3")
        self.assertEqual(manifest["builds"][0]["parts"][0]["offset"], 0)

    def test_prepare_web_flasher_copies_binary_and_updates_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "merged.bin"
            source.write_bytes(b"fake firmware")

            target = prepare_web_flasher(source, tmp_path / "site", version="9.9.9")

            self.assertEqual(target.read_bytes(), b"fake firmware")
            manifest = json.loads((tmp_path / "site" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], "9.9.9")
            self.assertEqual(manifest["builds"][0]["parts"][0]["path"], "firmware/w-midi-usb-esp32s3-merged.bin")

    def test_prepare_web_flasher_rejects_empty_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "empty.bin"
            source.write_bytes(b"")
            with self.assertRaises(ValueError):
                prepare_web_flasher(source, Path(tmp) / "site")


if __name__ == "__main__":
    unittest.main()
