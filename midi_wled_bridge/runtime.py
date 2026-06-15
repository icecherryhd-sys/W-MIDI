"""Runtime paths and commands shared by source and portable builds."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False) or "__compiled__" in globals())


def app_root() -> Path:
    if is_frozen():
        executable_path = Path(sys.executable).resolve()
        parts = executable_path.parts
        if ".app" in executable_path.as_posix():
            for index, part in enumerate(parts):
                if part.endswith(".app"):
                    return Path(*parts[:index])
        return executable_path.parent
    return Path(__file__).resolve().parents[1]


def executable_path() -> str:
    candidates = [Path(sys.executable)]
    if sys.argv:
        candidates.append(Path(sys.argv[0]))
    candidates.append(app_root() / "W-MIDI.exe")

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def bridge_command_prefix() -> list[str]:
    if is_frozen():
        return [executable_path(), "--bridge-cli"]
    return [sys.executable, "-m", "midi_wled_bridge.cli"]
