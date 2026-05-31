# Portable Windows Release Design

## Goal

Ship W-MIDI v1.1.0 as a portable Windows folder that starts without a
separate Python installation or dependency installation.

## Release Layout

The GitHub ZIP contains one top-level `W-MIDI-v1.1.0/` folder. Its visible
contents stay focused on user-facing files:

```text
W-MIDI-v1.1.0/
  W-MIDI.exe
  _internal/
  palettes/
  layouts/
  assets/
  README.txt
  README_EN.txt
  README.md
  CHANGELOG.md
  LICENSE.txt
  config.example.json
  W-MIDI Tutorial Guide.pdf
```

`W-MIDI.exe` is a PyInstaller one-folder build. `_internal/` contains the
embedded Python runtime, PySide6, RtMidi dependencies, and other generated
application files. Users keep the whole extracted folder together.

`palettes/` and `layouts/` remain outside `_internal/` because users read,
edit, add, and share these files. Documentation and the example
configuration remain visible for the same reason.

## Runtime Behavior

The desktop app resolves its writable working directory from the folder
containing the distributed `W-MIDI.exe`. It reads visible palettes, layouts,
assets, and documentation from that folder and stores `config.json` there.

The bundled app launches bridge subprocesses through its own executable
instead of relying on a separately installed Python interpreter. The existing
CLI remains usable from source for development, but the public Windows ZIP
does not require Python.

The optional `Create New Midi Port` feature still requires the separately
installed loopMIDI driver. Missing loopMIDI support continues to produce the
existing user-facing error only when that optional feature is used.

## Build Flow

A Windows packaging script builds the one-folder PyInstaller distribution
with the W-MIDI icon and copies user-facing files into the final package
folder. The archive script compresses that prepared portable folder as
`release/W-MIDI-v1.1.0.zip`.

The previous small C# launcher is no longer the public release executable
because it depends on a system Python installation. It may remain in the
repository only if it still serves source-development workflows.

## Documentation

The public README files and release checklist describe the portable ZIP:

1. Extract the complete folder.
2. Keep `W-MIDI.exe` and `_internal/` together.
3. Start `W-MIDI.exe`.

Python installation steps are removed from the normal user path. Development
instructions may still explain how to run the project from source.

## Verification

Automated tests confirm that:

- The portable packaging script exists and invokes PyInstaller in one-folder
  windowed mode.
- The build configuration includes the icon and required visible data files.
- Documentation no longer presents Python installation as a normal release
  prerequisite.

The release smoke test builds the folder and ZIP, starts the exact
`release/W-MIDI-v1.1.0/W-MIDI.exe`, confirms that it remains running long
enough for the GUI to initialize, and then closes it.
