"""Velocity palette parsing and loading."""

from __future__ import annotations

import argparse
from typing import Dict, List, Tuple


def parse_rgb(value: str) -> Tuple[int, int, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("RGB must be 'R,G,B'.")
    try:
        rgb = tuple(int(p.strip()) for p in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("RGB values must be integers.") from exc
    if any(channel < 0 or channel > 255 for channel in rgb):
        raise argparse.ArgumentTypeError("RGB values must be between 0 and 255.")
    return rgb  # type: ignore[return-value]


def parse_velocity_palette(value: str) -> Dict[int, Tuple[int, int, int]]:
    """Parse 'vel:R,G,B;vel:R,G,B' into a dict."""
    if not value.strip():
        raise argparse.ArgumentTypeError("Velocity palette cannot be empty.")

    mapping: Dict[int, Tuple[int, int, int]] = {}
    entries = [entry.strip() for entry in value.split(";") if entry.strip()]
    if not entries:
        raise argparse.ArgumentTypeError("Velocity palette has no valid entries.")

    for entry in entries:
        if ":" not in entry:
            raise argparse.ArgumentTypeError(
                f"Invalid palette entry '{entry}'. Use velocity:R,G,B."
            )
        velocity_text, rgb_text = entry.split(":", 1)
        try:
            velocity = int(velocity_text.strip())
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"Invalid velocity '{velocity_text}' in '{entry}'."
            ) from exc
        if velocity < 1 or velocity > 127:
            raise argparse.ArgumentTypeError(f"Velocity must be 1..127, got {velocity}.")
        mapping[velocity] = parse_rgb(rgb_text.strip())

    return mapping


def load_velocity_palette_file(path: str) -> Dict[int, Tuple[int, int, int]]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read()
    except OSError as exc:
        raise RuntimeError(f"Could not read palette file '{path}': {exc}") from exc

    cleaned_parts: List[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#", 1)[0].strip()
        if line:
            cleaned_parts.append(line)

    normalized = ";".join(cleaned_parts).replace("\n", ";")
    try:
        return parse_velocity_palette(normalized)
    except argparse.ArgumentTypeError as exc:
        raise RuntimeError(f"Invalid velocity palette in '{path}': {exc}") from exc


def default_builtin_palette() -> Dict[int, Tuple[int, int, int]]:
    return parse_velocity_palette(
        "1:0,0,40;32:0,120,255;64:255,140,0;96:255,0,90;127:255,255,255"
    )
