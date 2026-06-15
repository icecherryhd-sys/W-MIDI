"""Adalight frame encoding for standard WLED serial realtime input."""

from __future__ import annotations

from collections.abc import Iterable

RgbColor = tuple[int | float, int | float, int | float]


def _clamp_byte(value: int | float) -> int:
    return max(0, min(255, int(value)))


def build_adalight_frame(rgb_frame: Iterable[RgbColor]) -> bytes:
    colors = list(rgb_frame)
    if not colors:
        raise ValueError("Adalight frames require at least one LED.")
    if len(colors) > 65536:
        raise ValueError("Adalight supports at most 65536 LEDs in one frame.")

    encoded_count = len(colors) - 1
    high = (encoded_count >> 8) & 0xFF
    low = encoded_count & 0xFF
    payload = bytearray((ord("A"), ord("d"), ord("a"), high, low, high ^ low ^ 0x55))
    for red, green, blue in colors:
        payload.extend((_clamp_byte(red), _clamp_byte(green), _clamp_byte(blue)))
    return bytes(payload)
