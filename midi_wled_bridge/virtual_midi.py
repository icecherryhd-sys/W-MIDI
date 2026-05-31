"""Temporary virtual MIDI ports backed by Tobias Erichsen's virtualMIDI driver."""

from __future__ import annotations

import ctypes
import socket
import sys
from dataclasses import dataclass
from typing import Callable

VIRTUAL_MIDI_DLL = "teVirtualMIDI.dll"
MAX_SYSEX_LENGTH = 65535

_CallbackFactory = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
VirtualMidiCallback = _CallbackFactory(
    None,
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint32,
    ctypes.c_void_p,
)


class VirtualMidiError(RuntimeError):
    """Raised when the installed virtualMIDI driver cannot create a port."""


@dataclass
class _VirtualMidiPort:
    name: str
    handle: int
    callback: object


def _default_dll_loader(name: str):
    if not sys.platform.startswith("win"):
        raise VirtualMidiError("Virtual MIDI ports are only available on Windows.")
    return ctypes.WinDLL(name, use_last_error=True)


class VirtualMidiPortManager:
    """Owns virtualMIDI SDK ports for one W-MIDI GUI session."""

    def __init__(
        self,
        forward_port: int,
        *,
        dll_loader: Callable[[str], object] = _default_dll_loader,
        socket_factory: Callable[..., socket.socket] = socket.socket,
    ) -> None:
        self.forward_port = forward_port
        try:
            self._dll = dll_loader(VIRTUAL_MIDI_DLL)
        except (OSError, VirtualMidiError) as exc:
            raise VirtualMidiError(
                "Could not load the virtualMIDI driver. Install loopMIDI first; "
                "the loopMIDI application does not need to be running."
            ) from exc
        self._sock = socket_factory(socket.AF_INET, socket.SOCK_DGRAM)
        self._ports: dict[str, _VirtualMidiPort] = {}
        self._configure_sdk()

    def _configure_sdk(self) -> None:
        create = self._dll.virtualMIDICreatePortEx2
        create.argtypes = [
            ctypes.c_wchar_p,
            VirtualMidiCallback,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        create.restype = ctypes.c_void_p
        close = self._dll.virtualMIDIClosePort
        close.argtypes = [ctypes.c_void_p]
        close.restype = ctypes.c_bool

    def port_names(self) -> tuple[str, ...]:
        return tuple(self._ports)

    def has_port(self, name: str) -> bool:
        return name in self._ports

    def create_port(self, name: str) -> str:
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("MIDI port name cannot be empty.")
        if clean_name in self._ports:
            raise ValueError(f"A MIDI port named '{clean_name}' already exists.")

        @VirtualMidiCallback
        def on_midi_data(_port, data, length, _instance) -> None:
            if data and length:
                payload = ctypes.string_at(data, length)
                self._sock.sendto(payload, ("127.0.0.1", self.forward_port))

        handle = self._dll.virtualMIDICreatePortEx2(
            clean_name,
            on_midi_data,
            None,
            MAX_SYSEX_LENGTH,
            0,
        )
        if not handle:
            raise VirtualMidiError(
                f"Could not create virtual MIDI port '{clean_name}'. "
                "Check that loopMIDI is installed."
            )
        self._ports[clean_name] = _VirtualMidiPort(clean_name, int(handle), on_midi_data)
        return clean_name

    def close_all(self) -> None:
        for port in tuple(self._ports.values()):
            self._dll.virtualMIDIClosePort(port.handle)
        self._ports.clear()
        self._sock.close()
