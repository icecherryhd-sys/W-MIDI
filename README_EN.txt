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


Important fields
----------------
MIDI input device:
The MIDI device or virtual MIDI port the software should listen to.

WLED controller IP:
The local network address of your WLED controller, for example
192.168.1.100.

UDP port:
The WLED realtime UDP port. The usual default is 21324.

Total LED count:
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
