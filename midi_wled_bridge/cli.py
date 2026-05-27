#!/usr/bin/env python3
"""Command-line entry for the MIDI → WLED bridge."""

from __future__ import annotations

import argparse
import os
import sys

from midi_wled_bridge.bridge import Config, MidiToWledBridge
from midi_wled_bridge.constants import (
    DEFAULT_FRAME_INTERVAL_MS,
    DEFAULT_MIDI_READ_BURST,
    WLED_REALTIME_PORT,
)
from midi_wled_bridge.palette import (
    default_builtin_palette,
    load_velocity_palette_file,
    parse_rgb,
    parse_velocity_palette,
)
from midi_wled_bridge.ports import print_port_list, resolve_port_name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MIDI to WLED UDP bridge")
    parser.add_argument("--list-ports", action="store_true", help="List MIDI input ports and exit")
    parser.add_argument("--wled-ip", default="127.0.0.1", help="WLED IP address")
    parser.add_argument("--port", type=int, default=WLED_REALTIME_PORT, help="WLED UDP port")
    parser.add_argument("--midi-port", default="", help="MIDI input port name (substring allowed)")
    parser.add_argument("--led-count", type=int, default=64, help="Number of LEDs")
    parser.add_argument("--base-note", type=int, default=36, help="Lowest MIDI note mapped to LED 0")
    parser.add_argument(
        "--midi-channel",
        type=int,
        default=None,
        help="Optional MIDI channel to listen to, 1..16. Omit to listen to all channels.",
    )
    parser.add_argument(
        "--channel-bank-size",
        type=int,
        default=None,
        help="Optional LEDs per MIDI channel. Example: 100 maps channel 1 to LEDs 0..99 and channel 2 to 100..199.",
    )
    parser.add_argument(
        "--frame-interval-ms",
        type=int,
        default=DEFAULT_FRAME_INTERVAL_MS,
        help="Minimum milliseconds between UDP frames (limits frame rate). Use 0 for no limit.",
    )
    parser.add_argument(
        "--midi-read-burst",
        type=int,
        default=DEFAULT_MIDI_READ_BURST,
        help="Max MIDI messages to process per loop iteration.",
    )
    parser.add_argument(
        "--color-mode",
        choices=[
            "velocity_white",
            "velocity_red",
            "velocity_blue",
            "rainbow_note",
            "fixed",
            "velocity_palette",
        ],
        default="fixed",
        help="Color mapping mode",
    )
    parser.add_argument(
        "--fixed-color",
        type=parse_rgb,
        default=(0, 120, 255),
        help="Used with --color-mode fixed, format R,G,B",
    )
    parser.add_argument(
        "--velocity-palette",
        type=parse_velocity_palette,
        default=default_builtin_palette(),
        help="Used with --color-mode velocity_palette. Format: vel:R,G,B;vel:R,G,B",
    )
    parser.add_argument(
        "--velocity-palette-file",
        default="",
        help="Optional palette text file. Overrides --velocity-palette when set.",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose MIDI and mapping logs")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def build_config(args: argparse.Namespace) -> Config:
    midi_port = resolve_port_name(args.midi_port)
    velocity_palette = args.velocity_palette
    if args.velocity_palette_file:
        palette_path = os.path.abspath(args.velocity_palette_file)
        velocity_palette = load_velocity_palette_file(palette_path)
        if args.verbose:
            print(
                f"Loaded velocity palette from {palette_path} "
                f"({len(velocity_palette)} entries)"
            )
    return Config(
        wled_ip=args.wled_ip,
        port=args.port,
        midi_port=midi_port,
        led_count=args.led_count,
        base_note=args.base_note,
        color_mode=args.color_mode,
        fixed_color=args.fixed_color,
        velocity_palette=velocity_palette,
        midi_channel=args.midi_channel,
        channel_bank_size=args.channel_bank_size,
        verbose=args.verbose,
        frame_interval_ms=args.frame_interval_ms,
        midi_read_burst=args.midi_read_burst,
    )


def validate_args(args: argparse.Namespace) -> int | None:
    if args.led_count <= 0:
        print("--led-count must be > 0", file=sys.stderr)
        return 2
    if args.midi_channel is not None and not 1 <= args.midi_channel <= 16:
        print("--midi-channel must be 1..16", file=sys.stderr)
        return 2
    if args.channel_bank_size is not None and args.channel_bank_size <= 0:
        print("--channel-bank-size must be > 0", file=sys.stderr)
        return 2
    if args.frame_interval_ms < 0:
        print("--frame-interval-ms must be >= 0", file=sys.stderr)
        return 2
    if args.midi_read_burst <= 0:
        print("--midi-read-burst must be > 0", file=sys.stderr)
        return 2
    return None


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list_ports:
        print_port_list()
        return 0

    err = validate_args(args)
    if err is not None:
        return err

    try:
        config = build_config(args)
        bridge = MidiToWledBridge(config)
        bridge.run()
        return 0
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
