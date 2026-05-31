#!/usr/bin/env python3
"""List and monitor MIDI input ports."""

from __future__ import annotations

import argparse
import sys
import time

import mido

from midi_wled_bridge.ports import get_input_port_names, resolve_port_name


def list_ports() -> list[str]:
    ports = get_input_port_names()
    if not ports:
        print("No MIDI input ports found.")
        return []
    print("Available MIDI input ports:")
    for idx, name in enumerate(ports, start=1):
        print(f"  {idx}. {name}")
    return ports


def main() -> int:
    parser = argparse.ArgumentParser(description="List and monitor MIDI input ports")
    parser.add_argument("--list-only", action="store_true", help="List ports and exit")
    parser.add_argument("--port", default="", help="Port name (substring allowed)")
    args = parser.parse_args()

    ports = list_ports()
    if args.list_only:
        return 0
    if not ports:
        return 1

    try:
        port_name = resolve_port_name(args.port)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print()
    print(f"Monitoring MIDI input on: {port_name}")
    print("Press Ctrl+C to stop.")
    print()

    start = time.time()
    try:
        with mido.open_input(port_name) as in_port:
            for msg in in_port:
                t = time.time() - start
                print(f"[{t:8.3f}s] {msg}")
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
