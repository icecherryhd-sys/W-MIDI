import unittest
from io import StringIO
from threading import Event

from midi_wled_bridge.qt_controller import BridgeProcessController
from midi_wled_bridge.qt_model import BridgeWorkspace


class FakeProcess:
    def __init__(self, argv, output: str = "") -> None:
        self.argv = argv
        self.terminated = False
        self.stdout = StringIO(output)

    def poll(self):
        return None if not self.terminated else 0

    def terminate(self) -> None:
        self.terminated = True


class QtControllerTests(unittest.TestCase):
    def test_start_and_stop_are_independent_per_instance(self) -> None:
        workspace = BridgeWorkspace.default()
        second = workspace.add_instance()
        processes: list[FakeProcess] = []

        def popen(argv, **_kwargs):
            process = FakeProcess(argv)
            processes.append(process)
            return process

        controller = BridgeProcessController(popen_factory=popen, argv_builder=lambda settings: ["bridge", str(settings["wled_ip"])])
        first = workspace.instances[0]

        controller.start(first)
        controller.start(second)
        controller.stop(first)

        self.assertTrue(processes[0].terminated)
        self.assertFalse(processes[1].terminated)
        self.assertFalse(first.running)
        self.assertTrue(second.running)

    def test_shutdown_stops_all_running_instances(self) -> None:
        workspace = BridgeWorkspace.default()
        workspace.add_instance()
        processes: list[FakeProcess] = []

        def popen(argv, **_kwargs):
            process = FakeProcess(argv)
            processes.append(process)
            return process

        controller = BridgeProcessController(popen_factory=popen, argv_builder=lambda _settings: ["bridge"])
        for instance in workspace.instances:
            controller.start(instance)

        controller.shutdown()

        self.assertEqual([True, True], [process.terminated for process in processes])
        self.assertEqual([False, False], [instance.running for instance in workspace.instances])

    def test_start_forwards_process_output_to_instance_callback(self) -> None:
        workspace = BridgeWorkspace.default()
        received: list[tuple[str, str]] = []
        ready = Event()

        def on_output(instance, line: str) -> None:
            received.append((instance.id, line))
            ready.set()

        controller = BridgeProcessController(
            popen_factory=lambda argv, **_kwargs: FakeProcess(argv, "TELEMETRY fps=60.0\n"),
            argv_builder=lambda _settings: ["bridge"],
            output_callback=on_output,
        )

        controller.start(workspace.instances[0])

        self.assertTrue(ready.wait(1.0))
        self.assertEqual([(workspace.instances[0].id, "TELEMETRY fps=60.0")], received)


if __name__ == "__main__":
    unittest.main()
