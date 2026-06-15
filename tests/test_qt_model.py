import json
import tempfile
import unittest
from pathlib import Path

from midi_wled_bridge.qt_model import BridgeWorkspace


class QtModelTests(unittest.TestCase):
    def test_load_migrates_legacy_single_bridge_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps({"wled_ip": "192.168.1.42", "midi_port": "Piano"}),
                encoding="utf-8",
            )

            workspace = BridgeWorkspace.load(path)

            self.assertEqual(1, len(workspace.instances))
            self.assertEqual("192.168.1.42", workspace.instances[0].settings["wled_ip"])
            self.assertEqual("Piano", workspace.instances[0].settings["midi_port"])
            self.assertFalse(workspace.instances[0].running)

    def test_default_settings_include_serial_output_options(self) -> None:
        workspace = BridgeWorkspace.default()
        settings = workspace.instances[0].settings

        self.assertEqual("udp", settings["output_mode"])
        self.assertEqual("", settings["serial_port"])
        self.assertEqual(115200, settings["serial_baudrate"])
        self.assertEqual(60, settings["serial_fps"])
        self.assertTrue(settings["serial_auto_reconnect"])
        self.assertTrue(settings["serial_blackout_on_disconnect"])

    def test_add_instance_selects_new_stopped_bridge(self) -> None:
        workspace = BridgeWorkspace.default()

        created = workspace.add_instance()

        self.assertEqual(2, len(workspace.instances))
        self.assertEqual(created.id, workspace.selected_instance_id)
        self.assertEqual("Bridge 2", created.name)
        self.assertFalse(created.running)

    def test_save_and_load_preserves_multiple_settings_but_not_running_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            workspace = BridgeWorkspace.default()
            workspace.instances[0].settings["wled_ip"] = "192.168.1.10"
            workspace.instances[0].running = True
            second = workspace.add_instance()
            second.settings["wled_ip"] = "192.168.1.11"
            second.settings["midi_port"] = "W-MIDI Piano"
            second.running = True

            workspace.save(path)
            loaded = BridgeWorkspace.load(path)

            self.assertEqual(["192.168.1.10", "192.168.1.11"], [item.settings["wled_ip"] for item in loaded.instances])
            self.assertEqual("W-MIDI Piano", loaded.instances[1].settings["midi_port"])
            self.assertEqual(second.id, loaded.selected_instance_id)
            self.assertEqual([False, False], [item.running for item in loaded.instances])

    def test_palette_brightness_mode_is_stored_independently_per_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            workspace = BridgeWorkspace.default()
            workspace.instances[0].settings["scale_velocity_palette_to_full"] = True
            second = workspace.add_instance()
            second.settings["scale_velocity_palette_to_full"] = False

            workspace.save(path)
            loaded = BridgeWorkspace.load(path)

            self.assertTrue(loaded.instances[0].settings["scale_velocity_palette_to_full"])
            self.assertFalse(loaded.instances[1].settings["scale_velocity_palette_to_full"])

    def test_custom_led_layout_is_stored_independently_per_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            workspace = BridgeWorkspace.default()
            workspace.instances[0].settings["led_layout_positions"] = [[0.1, 0.2], [0.8, 0.7]]
            second = workspace.add_instance()
            second.settings["led_layout_positions"] = [[0.5, 0.5]]

            workspace.save(path)
            loaded = BridgeWorkspace.load(path)

            self.assertEqual([[0.1, 0.2], [0.8, 0.7]], loaded.instances[0].settings["led_layout_positions"])
            self.assertEqual([[0.5, 0.5]], loaded.instances[1].settings["led_layout_positions"])

    def test_runtime_logs_are_independent_and_not_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            workspace = BridgeWorkspace.default()
            workspace.instances[0].log_lines.append("Bridge 1 started")
            second = workspace.add_instance()
            second.log_lines.append("Bridge 2 waiting")

            workspace.save(path)
            loaded = BridgeWorkspace.load(path)

            self.assertEqual(["Bridge 1 started"], workspace.instances[0].log_lines)
            self.assertEqual(["Bridge 2 waiting"], workspace.instances[1].log_lines)
            self.assertEqual([[], []], [item.log_lines for item in loaded.instances])

    def test_remove_selected_instance_keeps_at_least_one_bridge(self) -> None:
        workspace = BridgeWorkspace.default()
        first_id = workspace.instances[0].id
        second = workspace.add_instance()

        self.assertTrue(workspace.remove_selected_instance())
        self.assertEqual([first_id], [item.id for item in workspace.instances])
        self.assertEqual(first_id, workspace.selected_instance_id)
        self.assertFalse(workspace.remove_selected_instance())
        self.assertEqual(1, len(workspace.instances))


if __name__ == "__main__":
    unittest.main()
