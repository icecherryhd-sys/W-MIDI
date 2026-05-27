import unittest

from midi_wled_bridge.gui import BridgeGuiApp
from midi_wled_bridge import gui


class GuiLogPopoutTests(unittest.TestCase):
    def test_log_popout_receives_new_log_lines(self) -> None:
        app = BridgeGuiApp()
        try:
            app._open_log_popout()
            app._append_log_line("popout test line")

            text = app._popout_log.get("1.0", "end")

            self.assertIn("popout test line", text)
        finally:
            app.root.destroy()

    def test_collapsed_log_preview_shortens_long_lines(self) -> None:
        app = BridgeGuiApp()
        try:
            long_line = "$ " + "x" * 400

            app._append_log_line(long_line)

            self.assertLessEqual(len(app._last_log_line.get()), 140)
            self.assertIn(long_line, app._log.get("1.0", "end"))
        finally:
            app.root.destroy()

    def test_embedded_log_is_capped(self) -> None:
        app = BridgeGuiApp()
        try:
            for index in range(gui.LOG_VISIBLE_MAX_LINES + 25):
                app._append_log_line(f"line {index}")

            self.assertEqual(gui.LOG_VISIBLE_MAX_LINES, app._visible_log_lines)
            self.assertNotIn("line 0", app._log.get("1.0", "end"))
        finally:
            app.root.destroy()

    def test_log_queue_poll_processes_bounded_batch(self) -> None:
        app = BridgeGuiApp()
        try:
            for index in range(gui.LOG_QUEUE_LINES_PER_TICK + 10):
                app._log_queue.put(f"queued {index}")

            app._poll_log_queue()

            self.assertEqual(10, app._log_queue.qsize())
        finally:
            app.root.destroy()


if __name__ == "__main__":
    unittest.main()
