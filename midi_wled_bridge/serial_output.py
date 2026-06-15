"""Serial WLED output helpers using the Adalight protocol."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

from midi_wled_bridge.adalight import RgbColor, build_adalight_frame


@dataclass(frozen=True)
class SerialPortInfo:
    device: str
    manufacturer: str | None = None
    product: str | None = None
    vid: int | None = None
    pid: int | None = None
    serial_number: str | None = None


def describe_serial_port(info: SerialPortInfo) -> str:
    parts = [info.device]
    for value in (info.manufacturer, info.product):
        if value:
            parts.append(value)
    if info.vid is not None and info.pid is not None:
        parts.append(f"VID:PID {info.vid:04X}:{info.pid:04X}")
    if info.serial_number:
        parts.append(f"SN {info.serial_number}")
    return " - ".join(parts)


def describe_serial_error(port: str, error: BaseException) -> str:
    if isinstance(error, PermissionError):
        return (
            f"{port} is already in use or Windows denied access. Stop the bridge, "
            "close Serial Monitor/Arduino IDE, or unplug/replug the ESP32, then try again."
        )
    return f"{port}: {error}"


def build_serial_test_frame(led_count: int) -> bytes:
    return build_adalight_frame([(0, 160, 0)] * max(1, led_count))


def list_serial_ports() -> list[SerialPortInfo]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []

    return [
        SerialPortInfo(
            device=str(port.device),
            manufacturer=getattr(port, "manufacturer", None),
            product=getattr(port, "product", None),
            vid=getattr(port, "vid", None),
            pid=getattr(port, "pid", None),
            serial_number=getattr(port, "serial_number", None),
        )
        for port in list_ports.comports()
    ]


class SerialFrameWriter:
    def __init__(self, serial_port: Any, max_pending_frames: int = 1) -> None:
        self.serial_port = serial_port
        self.max_pending_frames = max(1, max_pending_frames)
        self.pending_frame: bytes | None = None
        self.writing = False

    @property
    def pending_count(self) -> int:
        return 1 if self.pending_frame is not None else 0

    def send_or_queue(self, rgb_frame: Iterable[RgbColor], *, force: bool = False) -> None:
        payload = build_adalight_frame(rgb_frame)
        if self.writing and not force:
            self.pending_frame = payload
            return
        self._write(payload)

    def flush_pending(self) -> None:
        if self.pending_frame is None or self.writing:
            return
        payload = self.pending_frame
        self.pending_frame = None
        self._write(payload)

    def send_black_frame(self, led_count: int) -> None:
        self._write(build_adalight_frame([(0, 0, 0)] * led_count))

    def _write(self, payload: bytes) -> None:
        self.writing = True
        try:
            written = self.serial_port.write(payload)
            if written is not None and written != len(payload):
                raise OSError(f"Serial write incomplete: {written}/{len(payload)} bytes")
            flush = getattr(self.serial_port, "flush", None)
            if callable(flush):
                flush()
        finally:
            self.writing = False


class SerialWledTransport:
    def __init__(
        self,
        *,
        port: str,
        baudrate: int = 115200,
        start_delay_ms: int = 1500,
        auto_reconnect: bool = True,
        serial_factory: Any | None = None,
        log: Any = print,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.start_delay_ms = max(0, start_delay_ms)
        self.auto_reconnect = auto_reconnect
        self._serial_factory = serial_factory
        self._log = log
        self._serial: Any | None = None
        self._writer: SerialFrameWriter | None = None
        self.state = "disconnected"
        self.last_error = ""
        self._retry_delay = 1.0
        self._next_retry_at = 0.0
        self.frames_sent = 0
        self.bytes_sent = 0

    def connect(self, current_frame: Iterable[RgbColor] | None = None) -> bool:
        if not self.port:
            self._set_error("No serial port selected.")
            return False
        self.state = "connecting"
        try:
            serial_port = self._open_serial()
            self._serial = serial_port
            self._writer = SerialFrameWriter(serial_port)
            self._configure_control_lines(serial_port)
            if self.start_delay_ms:
                time.sleep(self.start_delay_ms / 1000.0)
            self.state = "connected"
            self.last_error = ""
            self._retry_delay = 1.0
            self._log(
                f"Serial port opened: {self.port} baud={self.baudrate} "
                f"start_delay_ms={self.start_delay_ms}"
            )
            if current_frame is not None:
                self.send_frame(current_frame, force=True)
            return True
        except Exception as exc:  # pylint: disable=broad-except
            self._set_error(str(exc))
            self._schedule_reconnect()
            return False

    def _open_serial(self) -> Any:
        if self._serial_factory is not None:
            return self._serial_factory(self.port, self.baudrate)
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError("pyserial is required for USB / Serial output.") from exc
        return serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0,
            write_timeout=0.25,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False,
        )

    def _configure_control_lines(self, serial_port: Any) -> None:
        for name in ("setDTR", "setRTS"):
            method = getattr(serial_port, name, None)
            if callable(method):
                try:
                    method(False)
                except Exception:
                    pass

    def send_frame(self, rgb_frame: Iterable[RgbColor], *, force: bool = False) -> bool:
        if self.state != "connected" or self._writer is None:
            self._maybe_reconnect(rgb_frame)
            return False
        try:
            payload = build_adalight_frame(rgb_frame)
            self._writer.send_or_queue(rgb_frame, force=force)
            self._writer.flush_pending()
            self.frames_sent += 1
            self.bytes_sent += len(payload)
            return True
        except Exception as exc:  # pylint: disable=broad-except
            self._set_error(str(exc))
            self.close()
            self._schedule_reconnect()
            return False

    def send_black_frame(self, led_count: int) -> None:
        if self.state == "connected" and self._writer is not None:
            self._writer.send_black_frame(led_count)

    def close(self) -> None:
        serial_port = self._serial
        self._serial = None
        self._writer = None
        if serial_port is not None:
            try:
                serial_port.close()
            finally:
                self._log(f"Serial port closed: {self.port}")
        if self.state != "error":
            self.state = "disconnected"

    def _set_error(self, message: str) -> None:
        self.last_error = message
        self.state = "error"
        self._log(f"Serial error on {self.port or '<none>'}: {message}")

    def _schedule_reconnect(self) -> None:
        if not self.auto_reconnect:
            return
        self.state = "reconnecting"
        self._next_retry_at = time.monotonic() + self._retry_delay
        self._log(f"Serial reconnect scheduled in {self._retry_delay:.0f}s")
        self._retry_delay = min(5.0, self._retry_delay * 2.0)

    def _maybe_reconnect(self, current_frame: Iterable[RgbColor]) -> None:
        if self.state != "reconnecting" or not self.auto_reconnect:
            return
        if time.monotonic() < self._next_retry_at:
            return
        self.connect(current_frame)
