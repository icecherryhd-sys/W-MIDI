<<<<<<< HEAD
<img width="2172" height="724" alt="57b1a061-0ca8-47c4-9cc5-b47049c074a8" src="https://github.com/user-attachments/assets/6b07035a-1ff7-42a7-90f0-e402aaf6f6ae" />
=======
# W-MIDI
>>>>>>> 9c97074 (feat: prepare W-MIDI v1.2.0 release builds)


# W-MIDI

W-MIDI connects MIDI input to WLED realtime UDP lighting. The `v1.2.0`
desktop app supports multiple independent bridges, virtual MIDI ports, palette
preview and scaling, realtime LED visualization, and custom 2D LED layouts.

## Portable Windows Release

1. Download and extract the complete `W-MIDI-v1.2.0.zip` archive.
2. Keep `W-MIDI.exe` and its bundled files together in the extracted folder.
3. Start `W-MIDI.exe`.

The Windows release is compiled with Nuitka. Python and the application
dependencies are bundled, so users do not need to install Python.

## Quick Start

1. Select a MIDI input.
2. Choose Wireless or Wired setup.
3. For Wireless, enter the WLED IP or use `Find WLED`.
4. Keep UDP port `21324` unless your WLED setup uses another port.
5. For Wired USB / Serial, choose the COM port and baudrate.
6. Set LED count, start note, and optional LEDs per channel.
7. Select a palette and start the bridge.

Use `Test Connection` to check controllers and `Save Config` to store the
workspace in `config.json`.

## USB / Serial WLED Mode

W-MIDI can send the same final RGB LED framebuffer over USB serial using the
standard WLED Adalight protocol. This works with ordinary ESP32-WROOM and
ESP32 DevKit boards running standard WLED; no WLED usermod, fork, or custom
firmware is required.

### Requirements

- Standard WLED with Adalight serial support enabled in the build.
- An ESP32 board connected by USB through its normal USB-to-UART chip.
- A matching baudrate in W-MIDI and WLED Sync Interfaces / Serial.
- `pyserial` installed when running from source.

### WLED Setup

1. Install normal WLED on the ESP32.
2. Configure LED type, data pin, and LED count in WLED.
3. Open WLED Sync Interfaces / Serial.
4. Set the same baudrate you will use in W-MIDI.
5. Confirm Adalight support is not disabled in your WLED build.

For a 32 LED strip, W-MIDI sends each frame as a 6 byte `Ada` header followed
by 96 RGB bytes, for 102 bytes total.

### W-MIDI Setup

1. Connect the ESP32 by USB.
2. Start W-MIDI.
3. Click `Wired Setup`.
4. Click `Find COM Ports`.
5. Choose the COM port, for example `COM4`.
6. Choose a baudrate: `115200`, `230400`, `460800`, or `921600`.
7. Keep `SERIAL FPS` at `60` unless you need another rate.
8. Keep auto reconnect enabled unless it interferes with your setup.
9. Start the bridge and play MIDI notes.

W-MIDI never blindly opens the first COM port. Pick the intended controller,
especially on systems with MIDI gear, Arduino boards, UPS devices, or other
serial hardware connected.

### Behavior

- Note On, velocity color, mapping, and Note Off use the same logic as UDP.
- MIDI events update one shared LED framebuffer.
- The frame scheduler sends the newest complete state, capped by the selected
  frame rate, so fast MIDI bursts do not create an ever-growing serial queue.
- Manual stop sends one black frame by default, then closes the port.
- During Serial Realtime, WLED effects may be temporarily overridden. WLED
  should return to its normal behavior after realtime serial input stops,
  depending on the WLED version and configuration.

### Power Notes

USB can power an ESP32 board, but many LEDs or high brightness need a proper
separate 5 V supply. Connect ESP32 ground and LED power-supply ground
together. Do not route large LED current through small ESP32 board traces.

### Troubleshooting

- No COM port visible: install the board USB driver, try another cable, then
  click `Find COM Ports`.
- Port already busy: close Serial Monitor, flashing tools, Arduino IDE, or any
  other program using the COM port.
- Wrong baudrate: set the same baudrate in WLED and W-MIDI. `115200` is the
  safest default.
- ESP resets when connecting: many USB-to-UART boards toggle reset lines when
  opened. W-MIDI waits briefly before sending frames.
- LEDs do not react: verify WLED LED count, data pin, Adalight support, output
  mode, and selected COM port.
- Wrong colors: confirm RGB LED type/order in WLED.
- Wrong LED order: adjust WLED strip setup or W-MIDI note mapping/layout.
- Only part of the strip reacts: check that WLED and W-MIDI use the same LED
  count.
- Connection drops: try a shorter USB cable, lower baudrate, and disable USB
  power saving.
- WLED effects run instead of Serial Realtime: check Sync Interfaces / Serial
  settings and make sure W-MIDI is connected.
- WLAN works but Serial does not: check COM port, baudrate, USB driver, and
  WLED Adalight support.
- Serial works but UDP does not: check WLED IP address, UDP port `21324`, and
  network/firewall settings.

## Features

### Multiple Bridges

- Use the numbered circles on the left to switch between bridge instances.
- Use `+` to add and `-` to remove an instance.
- Each bridge keeps independent MIDI, WLED, palette, layout, and log settings.
- Running bridges continue uninterrupted while another tab is selected.

### Virtual MIDI Ports

Install [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) once
so the virtualMIDI driver is available. The loopMIDI app itself does not need
to be open. Click `Create New Midi Port`, enter a name, and choose `Add`.
Ports created by W-MIDI are temporary and disappear when W-MIDI closes.

### Color Engine

- Choose a palette from the `palettes/` dropdown.
- W-MIDI supports `velocity:R,G,B` files and Launchpad-style
  `0, R G B;` files.
- The 128-color preview shows the currently selected palette.
- The sun button scales Launchpad-style `0..63` RGB values to `0..255` for the
  selected bridge. The moon button restores the original values.
- Scaling is applied only at runtime. Palette files are never modified.

### LED Preview And Layout Editor

- The LED/MIDI Mapping card mirrors the exact realtime colors sent to WLED.
- The number of preview squares follows `Total LED Count`.
- Click `Edit Custom Led Layout` to drag LEDs into a custom 2D arrangement.
- Drag a selection rectangle to select several LEDs, then move or rotate them
  together.
- Layouts can be reset, saved as JSON, and imported again.
- Custom layouts are stored independently for each bridge.

### Mapping

The base mapping is:

```text
led_index = midi_note - base_note
```

For larger setups, `LEDs per channel` assigns a separate LED bank to every
MIDI channel.

## Included Palettes And Layouts

The release includes palettes in `palettes/` and reusable JSON examples in
`layouts/`. The default palette is `palettes/Default`.

## Source Development

Install Python 3.10 or newer and the dependencies:

```powershell
py -3 -m pip install -r requirements.txt
```

### Command Line
<<<<<<< HEAD
=======


### V1.0.0
<img width="2172" height="724" alt="57b1a061-0ca8-47c4-9cc5-b47049c074a8" src="https://github.com/user-attachments/assets/ad983976-eff4-42af-be9e-16cba4d5058e" />


This is all based on an ESP32 running WLED, for further help see any tutorial on YouTube, for example: https://www.youtube.com/watch?v=exAWzMfmwQ8&t=375s

# W-MIDI

W-MIDI translates MIDI input into WLED realtime UDP lighting frames. It is built
for live LED control from a MIDI keyboard, controller, DAW, or virtual MIDI
port.

The desktop app is the recommended way to use W-MIDI. Command-line entry points
are still included for testing, automation, and advanced setups.

## Transparency

I'm no Pro Coder or anything, everything here was made using Codex (ChatGPT).

## Example use Case:

Full Example and Setup Tutorial: [W-MIDI Tutorial Guide.pdf](https://github.com/user-attachments/files/28325907/W-MIDI.Tutorial.Guide.pdf)

Side Note: Stop the Bridge before making any changes and save before starting again.

## Release Layout

```text
W-MIDI/
|-- W-MIDI.exe
|-- README.md
|-- README_EN.txt
|-- README.txt
|-- LICENSE.txt
|-- CHANGELOG.md
|-- RELEASE_CHECKLIST.md
|-- config.example.json
|-- requirements.txt
|-- pyproject.toml
|-- midi_wled_bridge/
|   |-- bridge.py
|   |-- cli.py
|   |-- gui.py
|   |-- midi_tester.py
|   |-- palette.py
|   |-- ports.py
|   `-- ...
|-- palettes/
|   `-- velocity_palette.txt
|-- scripts/
|   `-- windows/
|      |-- start_w_midi.bat
|      |-- start_gui.bat
|      |-- start_wled_midi_bridge.bat
|      |-- midi_input_tester.bat
|      `-- test_wled_udp.bat
|-- packaging/
|   `-- windows/
|      `-- build_w_midi_launcher.bat
|-- tools/
|   `-- windows/
|      `-- GuiLauncher.cs
`-- tests/
```

## Installation

```powershell
cd "C:\YOURLOCALSAVE\W-MIDI-1.0.0"
py -3 -m pip install -r requirements.txt
```

## Quick Start

1. Start `W-MIDI.exe`.
2. Select the MIDI input device.
3. Enter the WLED controller IP address.
4. Keep the UDP port at `21324` unless your WLED setup uses a custom port.
5. Set LED count and base note.
6. Click `Start Bridge`.

The `?` icon in the app opens `README_EN.txt`.

## Command-Line Use
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7
=======
>>>>>>> 9c97074 (feat: prepare W-MIDI v1.2.0 release builds)

List MIDI ports:

```powershell
py -3 -m midi_wled_bridge.midi_tester --list-only
```

Start the desktop app without the launcher:

```powershell
py -3 -m midi_wled_bridge.qt_gui
```

The CLI is still available for advanced setups:

```powershell
py -3 -m midi_wled_bridge.cli --help
```

## Build And Verify

```powershell
py -3.12 -m pip install -r requirements.txt nuitka
py -3 -m unittest discover -s tests
py -3 -m compileall -q midi_wled_bridge tests
powershell -ExecutionPolicy Bypass -File packaging\windows\build_release_archive.ps1
```

The archive is written to `release/W-MIDI-v1.2.0.zip`. See
`RELEASE_CHECKLIST.md` before publishing it on GitHub.
