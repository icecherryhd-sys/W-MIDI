"""MIDI input port discovery."""

from __future__ import annotations

import mido


def get_input_port_names() -> list[str]:
    return list(mido.get_input_names())


def print_port_list() -> None:
    names = get_input_port_names()
    if not names:
        print("No MIDI input ports found.")
        return
    print("Available MIDI input ports:")
    for idx, name in enumerate(names, start=1):
        print(f"  {idx}. {name}")


def resolve_port_name(requested: str) -> str:
    ports = get_input_port_names()
    if not ports:
        raise RuntimeError("No MIDI input ports available.")
    if not requested:
        return ports[0]

    exact = [p for p in ports if p == requested]
    if exact:
        return exact[0]

    matches = [p for p in ports if requested.lower() in p.lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise RuntimeError(
            f"Multiple MIDI ports match '{requested}': {matches}. "
            "Please provide a more specific name."
        )
    raise RuntimeError(f"No MIDI input port matches '{requested}'. Available: {ports}")
