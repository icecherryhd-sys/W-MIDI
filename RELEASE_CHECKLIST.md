# W-MIDI Release Checklist

Use this checklist before publishing a release archive or installer.

## Version

- Confirm `midi_wled_bridge/__init__.py` contains the intended version.
- Confirm `pyproject.toml` uses the same version.
- Update `CHANGELOG.md` with user-visible changes.

## Validation

- Run `py -3 -m unittest discover -s tests`.
- Start the GUI with `py -3 -m midi_wled_bridge.gui`.
- Click the `?` help link and confirm `README_EN.txt` opens.
- Run `scripts/windows/midi_input_tester.bat` on the target machine.
- Test WLED UDP output with the target controller.

## Windows Package

- Build `W-MIDI.exe` with `packaging/windows/build_w_midi_launcher.bat`.
- Confirm `assets/windows/w-midi.ico` is embedded as the executable icon.
- Include these files in the release archive:
  - `W-MIDI.exe`
  - `assets/windows/w-midi.ico`
  - `README_EN.txt`
  - `README.txt`
  - `config.example.json`
  - `requirements.txt`
  - `palettes/`
  - `scripts/windows/`
  - `midi_wled_bridge/`

## Final Check

- Open the release folder on a clean Windows machine.
- Install requirements with `py -3 -m pip install -r requirements.txt`.
- Start `W-MIDI.exe`.
- Confirm the window title and header show `W-MIDI`.
