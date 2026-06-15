import ctypes
import unittest

from midi_wled_bridge.virtual_midi import VirtualMidiPortManager, virtual_midi_driver_available


class FakeFunction:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls: list[tuple[object, ...]] = []
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        self.calls.append(args)
        return self.result


class FakeDll:
    def __init__(self) -> None:
        self.virtualMIDICreatePortEx2 = FakeFunction(1234)
        self.virtualMIDIClosePort = FakeFunction(True)


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[tuple[bytes, tuple[str, int]]] = []
        self.closed = False

    def sendto(self, payload: bytes, address: tuple[str, int]) -> None:
        self.sent.append((payload, address))

    def close(self) -> None:
        self.closed = True


class VirtualMidiPortManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dll = FakeDll()
        self.sock = FakeSocket()
        self.manager = VirtualMidiPortManager(
            forward_port=32001,
            dll_loader=lambda _: self.dll,
            socket_factory=lambda *_: self.sock,
        )

    def test_create_port_forwards_callback_bytes_to_loopback(self) -> None:
        self.manager.create_port("W-MIDI")
        callback = self.dll.virtualMIDICreatePortEx2.calls[0][1]
        payload = (ctypes.c_ubyte * 3)(0x90, 60, 127)

        callback(1234, payload, 3, 0)

        self.assertEqual([(b"\x90\x3c\x7f", ("127.0.0.1", 32001))], self.sock.sent)
        self.assertEqual(("W-MIDI",), self.manager.port_names())

    def test_create_port_rejects_blank_and_duplicate_names(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            self.manager.create_port("  ")

        self.manager.create_port("W-MIDI")

        with self.assertRaisesRegex(ValueError, "already exists"):
            self.manager.create_port("W-MIDI")

    def test_close_all_closes_sdk_ports_and_socket(self) -> None:
        self.manager.create_port("W-MIDI")
        self.manager.create_port("W-MIDI Piano")

        self.manager.close_all()

        self.assertEqual([(1234,), (1234,)], self.dll.virtualMIDIClosePort.calls)
        self.assertTrue(self.sock.closed)
        self.assertEqual((), self.manager.port_names())

    def test_driver_available_reports_missing_virtualmidi_dll(self) -> None:
        available, message = virtual_midi_driver_available(
            dll_loader=lambda _name: (_ for _ in ()).throw(OSError("missing"))
        )

        self.assertFalse(available)
        self.assertIn("Install loopMIDI", message)

    def test_driver_available_accepts_loadable_virtualmidi_dll(self) -> None:
        available, message = virtual_midi_driver_available(dll_loader=lambda _name: self.dll)

        self.assertTrue(available)
        self.assertEqual("", message)


if __name__ == "__main__":
    unittest.main()
