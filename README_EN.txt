W-MIDI v1.2.0


Important fields
----------------
MIDI input:
The MIDI device or virtual MIDI port W-MIDI listens to.

WLED IP:
The local network address of the WLED controller, for example 192.168.1.100.

UDP port:
The WLED realtime UDP port. The usual default is 21324.

Total LED count:
The number of LEDs controlled by the selected bridge.

Start note:
The MIDI note that maps to LED 0.

Listen channel:
"All" reacts to every MIDI channel. You can also choose one channel.

LEDs per channel:
Optional bank size for larger multi-channel setups.

Palette file:
The selected velocity palette. The default is palettes/Default.


Troubleshooting
---------------
If LEDs do not react:
- Check the WLED IP.
- Make sure the PC and WLED are on the same network.
- Check the selected MIDI input and start note.
- Make sure WLED accepts UDP realtime data.
- Use "Reload Ports" after connecting a new MIDI device.

The question mark at the top right opens this file. The German version is
available as README.txt.
