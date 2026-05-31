# W-MIDI Release Checklist

Use this checklist before publishing a release archive or installer.

## Version

- Confirm `midi_wled_bridge/__init__.py` contains the intended version.
- Confirm `pyproject.toml` uses the same version.
- Update `CHANGELOG.md` with user-visible changes.

## Validation

- Run `py -3 -m unittest discover -s tests`.
<<<<<<< HEAD
- Run `py -3 -m compileall -q midi_wled_bridge tests`.
- Start the GUI with `py -3 -m midi_wled_bridge.qt_gui`.
- Click the `?` help link and confirm `README_EN.txt` opens.
- Run `scripts/windows/midi_input_tester.bat` on the target machine.
- Test WLED UDP output with the target controller.
- Confirm add/remove bridge tabs, temporary MIDI port creation, palette
  dropdown, sun/moon scaling, realtime LED preview, and layout import/export.

## Windows Package

- Build the portable folder and GitHub ZIP with
  `powershell -ExecutionPolicy Bypass -File packaging/windows/build_release_archive.ps1`.
- Confirm the build calls `packaging/windows/build_portable_release.ps1`.
- Confirm `assets/windows/w-midi.ico` is embedded as the executable icon.
- Include these files in the release archive:
  - `W-MIDI.exe`
  - `_internal/`
=======
- Start the GUI with `py -3 -m midi_wled_bridge.gui`.
- Click the `?` help link and confirm `README_EN.txt` opens.
- Run `scripts/windows/midi_input_tester.bat` on the target machine.
- Test WLED UDP output with the target controller.

## Windows Package

- Build `W-MIDI.exe` with `packaging/windows/build_w_midi_launcher.bat`.
- Confirm `assets/windows/w-midi.ico` is embedded as the executable icon.
- Include these files in the release archive:
  - `W-MIDI.exe`
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7
  - `assets/windows/w-midi.ico`
  - `README_EN.txt`
  - `README.txt`
  - `config.example.json`
<<<<<<< HEAD
  - `palettes/`
  - `layouts/`
=======
  - `requirements.txt`
  - `palettes/`
  - `scripts/windows/`
  - `midi_wled_bridge/`
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7

## Final Check

- Open the release folder on a clean Windows machine.
<<<<<<< HEAD
- Keep `W-MIDI.exe` and `_internal/` together.
- Start `W-MIDI.exe`.
- Confirm the window title and header show `W-MIDI`.
- Confirm the GitHub archive is named `W-MIDI-v1.1.0.zip`.
=======
- Install requirements with `py -3 -m pip install -r requirements.txt`.
- Start `W-MIDI.exe`.
- Confirm the window title and header show `W-MIDI`.
>>>>>>> eabdd911b25d79a2bbd5c264e3d24a69dda49ce7
