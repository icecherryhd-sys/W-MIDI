# W-MIDI

![W-MIDI GitHub banner](assets/github/w-midi-github-banner.png)

W-MIDI connects MIDI input to WLED realtime UDP lighting. The `v1.1.0`
desktop app supports multiple independent bridges, virtual MIDI ports, palette
preview and scaling, realtime LED visualization, and custom 2D LED layouts.

## Portable Windows Release

1. Download and extract the complete `W-MIDI-v1.1.0.zip` archive.
2. Keep `W-MIDI.exe` and `_internal/` together in the extracted folder.
3. Start `W-MIDI.exe`.

Python and the application dependencies are bundled with the Windows release.

## Quick Start

1. Select a MIDI input.
2. Enter the WLED IP or use `Find WLED`.
3. Keep UDP port `21324` unless your WLED setup uses another port.
4. Set LED count, start note, and optional LEDs per channel.
5. Select a palette and start the bridge.

Use `Test Connection` to check the controller and `Save Config` to store the
workspace in `config.json`.

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
- Click `POP OUT` to open a larger live preview.
- Use `EDIT LAYOUT` to drag LEDs into a custom 2D arrangement.
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
py -3 -m unittest discover -s tests
py -3 -m compileall -q midi_wled_bridge tests
powershell -ExecutionPolicy Bypass -File packaging\windows\build_release_archive.ps1
```

The archive is written to `release/W-MIDI-v1.1.0.zip`. See
`RELEASE_CHECKLIST.md` before publishing it on GitHub.
