import unittest
from pathlib import Path


class GuiRuntimeSectionTests(unittest.TestCase):
    def test_runtime_section_has_no_fake_latency_metric(self) -> None:
        source = Path("midi_wled_bridge/gui.py").read_text(encoding="utf-8")

        self.assertNotIn("LATENCY", source)
        self.assertNotIn("def _metric", source)


if __name__ == "__main__":
    unittest.main()
