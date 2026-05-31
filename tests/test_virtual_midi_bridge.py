import socket
import unittest

import mido

from midi_wled_bridge.bridge import read_virtual_midi_messages


class VirtualMidiBridgeTests(unittest.TestCase):
    def test_reads_midi_messages_from_loopback_udp(self) -> None:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind(("127.0.0.1", 0))
        receiver.setblocking(False)
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sender.sendto(b"\x90\x3c\x7f", receiver.getsockname())

            messages = read_virtual_midi_messages(receiver, mido.Parser(), 64)

            self.assertEqual([mido.Message("note_on", note=60, velocity=127)], messages)
        finally:
            sender.close()
            receiver.close()


if __name__ == "__main__":
    unittest.main()
