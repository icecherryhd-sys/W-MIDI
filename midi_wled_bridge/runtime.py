"""Runtime paths and commands shared by source and portable builds."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_root() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def bridge_command_prefix() -> list[str]:
    if is_frozen():
        return [sys.executable, "--bridge-cli"]
    return [sys.executable, "-m", "midi_wled_bridge.cli"]
