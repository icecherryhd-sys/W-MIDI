#!/usr/bin/env python3
"""Core bridge: MIDI input → buffered RGB strip → WLED UDP DRGB."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import mido

from midi_wled_bridge.colors import hsv_to_rgb
from midi_wled_bridge.constants import (
    WLED_TIMEOUT_SECONDS,
    WLED_UDP_TIMEOUT_VALUE,
)


@dataclass
class Config:
    wled_ip: str
    port: int
    midi_port: str
    led_count: int
    base_note: int
    color_mode: str
    fixed_color: Tuple[int, int, int]
    velocity_palette: Dict[int, Tuple[int, int, int]]
    midi_channel: int | None
    channel_bank_size: int | None
    verbose: bool
    frame_interval_ms: int
    midi_read_burst: int


class MidiToWledBridge:
    def __init__(self, config: Config) -> None:
        self.cfg = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_update = 0.0
        self.leds: List[Tuple[int, int, int]] = [(0, 0, 0)] * self.cfg.led_count
        self.needs_update = True
        self.last_frame_time = 0.0
        self.telemetry_started_at = time.monotonic()
        self.telemetry_last_emit = self.telemetry_started_at
        self.telemetry_frames = 0
        self.telemetry_midi_messages = 0
        self.verbose_last_emit = self.telemetry_started_at
        self.verbose_suppressed = 0

    def run(self) -> None:
        print(f"Connecting MIDI input: {self.cfg.midi_port}")
        with mido.open_input(self.cfg.midi_port) as in_port:
            print(
                f"Streaming to WLED {self.cfg.wled_ip}:{self.cfg.port} "
                f"for {self.cfg.led_count} LEDs"
            )
            self.last_frame_time = time.monotonic()
            self.render_fixed_frame_rate(force=True)

            while True:
                processed = 0
                for message in in_port.iter_pending():
                    if self.handle_message(message):
                        self.telemetry_midi_messages += 1
                    processed += 1
                    if processed >= self.cfg.midi_read_burst:
                        break

                self.render_fixed_frame_rate()
                self.send_keepalive_if_needed()
                self.emit_telemetry_if_needed()

                if processed == 0:
                    time.sleep(0.001)

    def handle_message(self, message: mido.Message) -> bool:
        channel = getattr(message, "channel", None)
        if self.cfg.midi_channel is not None and channel != self.cfg.midi_channel - 1:
            return False

        if message.type == "note_on" and message.velocity > 0:
            self.set_note(message.note, message.velocity, channel)
        elif message.type in ("note_off", "note_on"):
            self.clear_note(message.note, channel)
        else:
            return False
        self.needs_update = True
        return True

    def note_to_index(self, note: int, channel: int | None = None) -> int | None:
        raw = note - self.cfg.base_note
        if raw < 0:
            return None
        idx = raw
        if self.cfg.channel_bank_size and channel is not None:
            if raw >= self.cfg.channel_bank_size:
                return None
            idx = channel * self.cfg.channel_bank_size + raw
        if idx < 0 or idx >= self.cfg.led_count:
            return None
        return idx

    def set_note(self, note: int, velocity: int, channel: int | None = None) -> None:
        idx = self.note_to_index(note, channel)
        if idx is None:
            if self.cfg.verbose:
                print(f"Skipping note {note}: outside LED range")
            return
        self.leds[idx] = self.color_for(note, velocity)
        self._verbose_log(f"note_on ch={self._display_channel(channel)} note={note} vel={velocity} -> led={idx} rgb={self.leds[idx]}")

    def clear_note(self, note: int, channel: int | None = None) -> None:
        idx = self.note_to_index(note, channel)
        if idx is None:
            return
        self.leds[idx] = (0, 0, 0)
        self._verbose_log(f"note_off ch={self._display_channel(channel)} note={note} -> led={idx}")

    def _display_channel(self, channel: int | None) -> str:
        if channel is None:
            return "-"
        return str(channel + 1)

    def _verbose_log(self, line: str) -> None:
        if not self.cfg.verbose:
            return
        now = time.monotonic()
        if now - self.verbose_last_emit >= 0.05:
            if self.verbose_suppressed:
                print(f"[verbose throttled] suppressed {self.verbose_suppressed} MIDI log lines", flush=True)
                self.verbose_suppressed = 0
            print(line, flush=True)
            self.verbose_last_emit = now
        else:
            self.verbose_suppressed += 1

    def color_for(self, note: int, velocity: int) -> Tuple[int, int, int]:
        mode = self.cfg.color_mode
        if mode == "fixed":
            return self.cfg.fixed_color
        if mode == "velocity_palette":
            if velocity in self.cfg.velocity_palette:
                return self.cfg.velocity_palette[velocity]
            nearest = min(
                self.cfg.velocity_palette.keys(),
                key=lambda defined_velocity: abs(defined_velocity - velocity),
            )
            return self.cfg.velocity_palette[nearest]
        if mode == "velocity_white":
            v = int((velocity / 127.0) * 255)
            return (v, v, v)
        if mode == "velocity_red":
            r = int((velocity / 127.0) * 255)
            return (r, 0, 0)
        if mode == "velocity_blue":
            b = int((velocity / 127.0) * 255)
            return (0, 0, b)
        if mode == "rainbow_note":
            return hsv_to_rgb(((note % 12) / 12.0), 1.0, velocity / 127.0)
        return self.cfg.fixed_color

    def render_fixed_frame_rate(self, force: bool = False) -> None:
        if not self.needs_update and not force:
            return

        now = time.monotonic()
        interval_s = max(0.0, self.cfg.frame_interval_ms / 1000.0)
        if force or (now - self.last_frame_time) >= interval_s:
            self.send_frame()
            self.last_frame_time = now
            self.needs_update = False

    def send_frame(self) -> None:
        payload = bytearray()
        payload.append(2)  # DRGB protocol
        payload.append(WLED_UDP_TIMEOUT_VALUE)
        for r, g, b in self.leds:
            payload.extend((r, g, b))

        self.sock.sendto(payload, (self.cfg.wled_ip, self.cfg.port))
        self.last_update = time.time()
        self.telemetry_frames += 1

    def send_keepalive_if_needed(self) -> None:
        if time.time() - self.last_update > WLED_TIMEOUT_SECONDS:
            self.send_frame()

    def emit_telemetry_if_needed(self, force: bool = False) -> None:
        now = time.monotonic()
        elapsed = now - self.telemetry_last_emit
        if not force and elapsed < 1.0:
            return
        if elapsed <= 0:
            elapsed = 1.0
        fps = self.telemetry_frames / elapsed
        midi_per_s = self.telemetry_midi_messages / elapsed
        last_frame_ms = int(max(0.0, (time.time() - self.last_update) * 1000.0)) if self.last_update else 0
        print(
            "TELEMETRY "
            f"fps={fps:.1f} "
            f"midi_per_s={midi_per_s:.1f} "
            f"udp_per_s={fps:.1f} "
            f"last_frame_ms={last_frame_ms}",
            flush=True,
        )
        self.telemetry_last_emit = now
        self.telemetry_frames = 0
        self.telemetry_midi_messages = 0
