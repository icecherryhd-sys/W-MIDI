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

List MIDI ports:

```powershell
py -3 -m midi_wled_bridge.midi_tester --list-only
```

Start the bridge:

```powershell
py -3 -m midi_wled_bridge.cli --wled-ip 192.168.1.100 --midi-port "loopMIDI" --led-count 64 --base-note 36 --color-mode velocity_palette --velocity-palette-file "palettes/velocity_palette.txt"
```

Start the GUI without the launcher:

```powershell
py -3 -m midi_wled_bridge.gui
```

## GUI Features

- Configure WLED IP, WLED port, MIDI port, LED count, and base note.
- Listen to all MIDI channels or a single selected channel.
- Split larger LED installations into MIDI channel banks.
- Choose fixed colors, velocity palettes, white/red/blue velocity modes, or rainbow note mapping.
- Tune frame interval and MIDI processing burst for performance.
- Save settings to `config.json`.
- View and pop out the live bridge log.

## Mapping

W-MIDI uses linear note mapping:

```text
led_index = midi_note - base_note
```

For larger LED setups, set `channel_bank_size` or `--channel-bank-size`.
With a value of `100`, MIDI channel 1 maps to LEDs `0..99`, channel 2 maps to
`100..199`, channel 3 maps to `200..299`, and so on.

## Color Modes

- `fixed`
- `velocity_palette`
- `velocity_white`
- `velocity_red`
- `velocity_blue`
- `rainbow_note`

When `velocity_palette` is selected and a velocity is not defined exactly, the
nearest defined velocity in the palette is used.

## Building The Windows Launcher

From a Visual Studio Developer Command Prompt:

```powershell
packaging\windows\build_w_midi_launcher.bat
```

This creates `W-MIDI.exe` in the project root.
