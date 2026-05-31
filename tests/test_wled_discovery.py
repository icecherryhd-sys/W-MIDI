import unittest

from midi_wled_bridge.discovery import WledDevice, discover_wled_devices, parse_wled_info


class WledDiscoveryTests(unittest.TestCase):
    def test_parse_wled_info_uses_name_from_json_info(self) -> None:
        device = parse_wled_info("192.168.1.42", {"name": "Desk LEDs", "ver": "0.14.0"})

        self.assertEqual(WledDevice(name="Desk LEDs", ip="192.168.1.42"), device)

    def test_parse_wled_info_rejects_non_wled_payloads(self) -> None:
        self.assertIsNone(parse_wled_info("192.168.1.50", {"name": "Printer"}))

    def test_discover_wled_devices_sorts_by_ip_and_skips_invalid_hosts(self) -> None:
        payloads = {
            "192.168.1.30": {"name": "Stage Right", "ver": "0.14.0"},
            "192.168.1.10": {"name": "Stage Left", "brand": "WLED"},
            "192.168.1.20": None,
        }

        def fake_fetch(ip: str, timeout: float) -> dict[str, object] | None:
            return payloads[ip]

        devices = discover_wled_devices(
            candidate_ips=payloads.keys(),
            fetch_json=fake_fetch,
            timeout=0.01,
            max_workers=2,
        )

        self.assertEqual(
            [
                WledDevice(name="Stage Left", ip="192.168.1.10"),
                WledDevice(name="Stage Right", ip="192.168.1.30"),
            ],
            devices,
        )


if __name__ == "__main__":
    unittest.main()
