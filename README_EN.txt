W-MIDI v1.1.0
==============

Short summary
-------------
W-MIDI connects MIDI input to WLED realtime UDP lighting. It supports multiple
independent bridges, virtual MIDI ports, palette preview and scaling, realtime
LED visualization, and custom 2D LED layouts.


Quick start
-----------
1. Extract the complete ZIP archive.
2. Keep W-MIDI.exe and the _internal folder together in the extracted folder.
3. Start W-MIDI.exe.
4. Select a MIDI input.
5. Enter the WLED IP or use "Find WLED".
6. Keep UDP port 21324 unless your WLED setup uses another port.
7. Set LED count, start note, and optional LEDs per channel.
8. Select a palette and click "Start Bridge".

Use "Test Connection" to check the controller and "Save Config" to store your
workspace.


Multiple bridges
----------------
The numbered circles on the left represent bridge instances. Use "+" to add
and "-" to remove an instance. Each bridge has independent MIDI, WLED,
palette, layout, and log settings. Running bridges continue uninterrupted
while you switch tabs.


Virtual MIDI ports
------------------
Install loopMIDI once so its virtualMIDI driver is available. The loopMIDI
application itself does not need to be open. Click "Create New Midi Port",
enter a name, and choose "Add". Ports created by W-MIDI are temporary and
disappear when W-MIDI closes.


Color engine
------------
Select a palette from the dropdown. W-MIDI supports palette files using
"velocity:R,G,B" entries and Launchpad-style "0, R G B;" lines.

The preview displays all 128 velocity colors. Use the sun button to scale
Launchpad-style 0..63 RGB values to 0..255 for the selected bridge. Use the
moon button to restore the original palette values. Scaling is applied only
inside W-MIDI; the palette file is never modified.


LED preview and layout editor
-----------------------------
The LED/MIDI Mapping card shows the exact realtime colors sent to WLED. The
number of preview squares follows "Total LED Count".

Click "POP OUT" for a larger live preview. Click "EDIT LAYOUT" to visually
position LEDs on a 2D canvas. You can drag individual LEDs, drag a selection
rectangle for multiple LEDs, move selected LEDs together, and rotate the
selection. Use "RESET LAYOUT" to restore the automatic grid. Layouts can be
saved as JSON and imported again.


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
