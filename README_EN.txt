<<<<<<< HEAD
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
=======
W-MIDI
======

Short summary
-------------
W-MIDI connects a MIDI input device to a WLED controller. Incoming MIDI notes
and controller messages are translated into UDP lighting data so your WLED LEDs
can react directly to your MIDI performance.


Starting the app
----------------
1. Start the application with W-MIDI.exe.
2. Select your MIDI input device.
3. Enter the IP address of your WLED controller.
4. Keep the UDP port at 21324 unless you changed it in WLED.
5. Set the LED count and start note for your setup.
6. Click "Start Bridge".

Use "Stop Bridge" to stop the active connection.
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7


Important fields
----------------
<<<<<<< HEAD
MIDI input:
The MIDI device or virtual MIDI port W-MIDI listens to.

WLED IP:
The local network address of the WLED controller, for example 192.168.1.100.
=======
MIDI input device:
The MIDI device or virtual MIDI port the software should listen to.

WLED controller IP:
The local network address of your WLED controller, for example
192.168.1.100.
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7

UDP port:
The WLED realtime UDP port. The usual default is 21324.

Total LED count:
<<<<<<< HEAD
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
=======
The number of LEDs the software should control.

Start note (base):
The MIDI note that maps to LED 0. Higher notes move forward along the LED
strip.

Listen channel:
"All" reacts to every MIDI channel. You can also select one channel from
1 to 16.

LEDs per channel:
Optional setting for larger installations. It lets each MIDI channel control
its own LED range.

Mapping mode:
Controls how colors are generated. For a first setup, "velocity_palette" is a
good choice because note velocity controls the color.

Velocity palette file:
The palette file used by "velocity_palette". The default is
palettes/velocity_palette.txt.

Frame interval (ms):
Limits how quickly new lighting frames are sent. 5 ms is fast; 10 ms may be
more stable on busy or unreliable networks.

MIDI read burst:
Controls how many MIDI messages are processed in one loop. The default is
suitable for normal use.

Verbose output in log:
Writes more details to the log. This is useful for troubleshooting, but it is
usually best left off during live use.


Typical workflow
----------------
1. Turn on the WLED controller and make sure it is on the same network as the
   PC.
2. Connect your MIDI device or start your virtual MIDI port.
3. Open W-MIDI.exe.
4. Set the WLED IP address and MIDI device.
5. Use "Test Connection" to check whether the controller can be reached.
6. Click "Start Bridge".
7. Play MIDI notes and watch the LEDs react.
8. Save your setup with "Save Config" if you want to reuse it next time.


Log and troubleshooting
-----------------------
The Bridge Log is shown at the bottom of the window. It displays status
messages and warnings when something needs attention.

"Pop Out" opens the log in its own window.
"Clear Log" clears the visible log text.

If the LEDs do not react:
- Check the WLED IP address.
- Make sure the PC and WLED controller are on the same network.
- Check that the correct MIDI device is selected.
- Check that the start note matches the notes you are playing.
- Make sure WLED accepts UDP realtime data.


Saving settings
---------------
"Save Config" stores your current settings in config.json.
They are loaded automatically the next time you start the app.


Opening help
------------
The question mark in the top right corner of the app opens this README_EN.txt
file.

The German version is available as README.txt.
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7
