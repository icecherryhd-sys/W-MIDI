"""Per-instance bridge subprocess management for the Qt desktop app."""

from __future__ import annotations

import subprocess
import threading
from collections.abc import Callable
from typing import Any

from midi_wled_bridge.qt_model import BridgeInstance


class BridgeProcessController:
    def __init__(
        self,
        *,
        popen_factory: Callable[..., Any] = subprocess.Popen,
        argv_builder: Callable[[dict[str, object]], list[str]],
        output_callback: Callable[[BridgeInstance, str], None] | None = None,
    ) -> None:
        self._popen_factory = popen_factory
        self._argv_builder = argv_builder
        self._output_callback = output_callback
        self._processes: dict[str, Any] = {}
        self._instances: dict[str, BridgeInstance] = {}

    def is_running(self, instance: BridgeInstance) -> bool:
        process = self._processes.get(instance.id)
        return process is not None and process.poll() is None

    def start(self, instance: BridgeInstance) -> Any:
        if self.is_running(instance):
            return self._processes[instance.id]
        process = self._popen_factory(self._argv_builder(instance.settings))
        self._processes[instance.id] = process
        self._instances[instance.id] = instance
        instance.running = True
        if self._output_callback is not None and getattr(process, "stdout", None) is not None:
            threading.Thread(
                target=self._read_output,
                args=(instance, process),
                daemon=True,
            ).start()
        return process

    def _read_output(self, instance: BridgeInstance, process: Any) -> None:
        for chunk in iter(process.stdout.readline, ""):
            line = chunk.rstrip()
            if line and self._output_callback is not None:
                self._output_callback(instance, line)
        process.stdout.close()

    def stop(self, instance: BridgeInstance) -> None:
        process = self._processes.pop(instance.id, None)
        if process is not None and process.poll() is None:
            process.terminate()
        instance.running = False

    def shutdown(self) -> None:
        for instance in tuple(self._instances.values()):
            self.stop(instance)
        self._instances.clear()
