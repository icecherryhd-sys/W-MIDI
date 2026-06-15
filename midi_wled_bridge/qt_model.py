"""Persistent multi-bridge workspace model for the Qt desktop app."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BRIDGE_SETTINGS: dict[str, object] = {
    "wled_ip": "192.168.1.100",
    "wled_port": 21324,
    "output_mode": "udp",
    "midi_port": "loopMIDI",
    "led_count": 64,
    "base_note": 36,
    "midi_channel": "All",
    "channel_bank_size": "",
    "frame_interval_ms": 5,
    "midi_read_burst": 64,
    "color_mode": "velocity_palette",
    "fixed_color": "0,120,255",
    "velocity_palette_file": "palettes/Default",
    "scale_velocity_palette_to_full": False,
    "led_layout_positions": [],
    "verbose": False,
    "serial_port": "",
    "serial_port_vid": "",
    "serial_port_pid": "",
    "serial_port_serial_number": "",
    "serial_baudrate": 115200,
    "serial_fps": 60,
    "serial_auto_reconnect": True,
    "serial_blackout_on_disconnect": True,
    "serial_start_delay_ms": 1500,
}


def _merged_settings(raw: dict[str, object] | None = None) -> dict[str, object]:
    settings = dict(DEFAULT_BRIDGE_SETTINGS)
    if raw:
        for key in settings:
            if key in raw:
                settings[key] = raw[key]
    return settings


@dataclass
class BridgeInstance:
    id: str
    name: str
    settings: dict[str, object] = field(default_factory=_merged_settings)
    running: bool = False
    log_lines: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, number: int) -> "BridgeInstance":
        return cls(id=uuid.uuid4().hex, name=f"Bridge {number}")

    @classmethod
    def from_dict(cls, raw: dict[str, object], number: int) -> "BridgeInstance":
        return cls(
            id=str(raw.get("id") or uuid.uuid4().hex),
            name=str(raw.get("name") or f"Bridge {number}"),
            settings=_merged_settings(raw.get("settings") if isinstance(raw.get("settings"), dict) else {}),
            running=False,
        )

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "name": self.name, "settings": dict(self.settings)}


@dataclass
class BridgeWorkspace:
    instances: list[BridgeInstance]
    selected_instance_id: str

    @classmethod
    def default(cls) -> "BridgeWorkspace":
        instance = BridgeInstance.create(1)
        return cls([instance], instance.id)

    @classmethod
    def load(cls, path: Path) -> "BridgeWorkspace":
        if not path.is_file():
            return cls.default()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls.default()
        if not isinstance(raw, dict):
            return cls.default()

        raw_instances = raw.get("instances")
        if isinstance(raw_instances, list) and raw_instances:
            instances = [
                BridgeInstance.from_dict(item, index)
                for index, item in enumerate(raw_instances, start=1)
                if isinstance(item, dict)
            ]
            if instances:
                selected = str(raw.get("selected_instance_id") or instances[0].id)
                if selected not in {item.id for item in instances}:
                    selected = instances[0].id
                return cls(instances, selected)

        legacy = BridgeInstance.create(1)
        legacy.settings = _merged_settings(raw)
        return cls([legacy], legacy.id)

    def add_instance(self) -> BridgeInstance:
        instance = BridgeInstance.create(len(self.instances) + 1)
        self.instances.append(instance)
        self.selected_instance_id = instance.id
        return instance

    def remove_selected_instance(self) -> bool:
        if len(self.instances) <= 1:
            return False
        selected_index = next(
            (index for index, item in enumerate(self.instances) if item.id == self.selected_instance_id),
            0,
        )
        self.instances.pop(selected_index)
        next_index = min(selected_index, len(self.instances) - 1)
        self.selected_instance_id = self.instances[next_index].id
        return True

    def selected(self) -> BridgeInstance:
        for instance in self.instances:
            if instance.id == self.selected_instance_id:
                return instance
        self.selected_instance_id = self.instances[0].id
        return self.instances[0]

    def save(self, path: Path) -> None:
        payload = {
            "version": 2,
            "selected_instance_id": self.selected_instance_id,
            "instances": [instance.to_dict() for instance in self.instances],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
