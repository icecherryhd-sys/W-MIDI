"""Shared desktop helpers without GUI toolkit dependencies."""

from __future__ import annotations

import os
import socket

from midi_wled_bridge.runtime import app_root, bridge_command_prefix

REPO_ROOT = str(app_root())
README_TXT_FILENAME = "README_EN.txt"
APP_ICON_FILENAME = os.path.join("assets", "windows", "w-midi.ico")


def readme_txt_path() -> str:
    return os.path.join(REPO_ROOT, README_TXT_FILENAME)


def app_icon_path() -> str:
    return os.path.join(REPO_ROOT, APP_ICON_FILENAME)


def open_readme_file() -> None:
    os.startfile(readme_txt_path())


def find_available_loopback_udp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def build_subprocess_argv(settings: dict[str, object]) -> list[str]:
    argv = [
        *bridge_command_prefix(),
        "--wled-ip",
        str(settings["wled_ip"]).strip(),
        "--port",
        str(int(settings["wled_port"])),
        "--midi-port",
        str(settings["midi_port"]).strip(),
        "--led-count",
        str(int(settings["led_count"])),
        "--base-note",
        str(int(settings["base_note"])),
        "--frame-interval-ms",
        str(int(settings["frame_interval_ms"])),
        "--midi-read-burst",
        str(int(settings["midi_read_burst"])),
        "--color-mode",
        str(settings["color_mode"]),
        "--fixed-color",
        str(settings["fixed_color"]).strip(),
    ]

    midi_channel = str(settings.get("midi_channel") or "All").strip()
    if midi_channel and midi_channel.lower() != "all":
        argv.extend(["--midi-channel", str(int(midi_channel))])

    channel_bank_size = str(settings.get("channel_bank_size") or "").strip()
    if channel_bank_size:
        argv.extend(["--channel-bank-size", str(int(channel_bank_size))])

    palette_file = str(settings.get("velocity_palette_file") or "").strip()
    if str(settings["color_mode"]) == "velocity_palette" and palette_file:
        abs_palette = palette_file if os.path.isabs(palette_file) else os.path.abspath(os.path.join(REPO_ROOT, palette_file))
        argv.extend(["--velocity-palette-file", abs_palette])

    if settings.get("scale_velocity_palette_to_full"):
        argv.append("--scale-velocity-palette-to-full")

    argv.append("--emit-led-frames")

    if settings.get("verbose"):
        argv.append("--verbose")
    virtual_midi_udp_port = settings.get("virtual_midi_udp_port")
    if virtual_midi_udp_port:
        argv.extend(["--virtual-midi-udp-port", str(int(virtual_midi_udp_port))])
    return argv
