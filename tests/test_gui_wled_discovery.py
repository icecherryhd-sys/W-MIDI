import unittest
from pathlib import Path


class GuiWledDiscoveryTests(unittest.TestCase):
    def test_gui_exposes_wled_discovery_control(self) -> None:
        source = Path("midi_wled_bridge/gui.py").read_text(encoding="utf-8")

        self.assertIn("Find WLED", source)
        self.assertIn("_find_wled_clicked", source)
        self.assertIn("_run_wled_discovery", source)
        self.assertIn("discover_wled_devices", source)


if __name__ == "__main__":
    unittest.main()
