# W-MIDI Virtual MIDI Ports Design

## Goal

W-MIDI can create temporary virtual MIDI input ports without requiring the
loopMIDI application to run. The user must still have loopMIDI installed so its
virtualMIDI driver is available.

## User Experience

- Keep the existing MIDI input selector and `Reload Ports` button.
- Add a `Create New Midi Port` button.
- Clicking it opens a small dialog with a name field prefilled with `W-MIDI`.
- `Cancel` closes the dialog without changes.
- `Add` creates a temporary virtual port, refreshes the selector, and selects
  the new port.
- Ports created by W-MIDI disappear when W-MIDI closes.
- If the driver cannot be loaded or the port cannot be created, show an
  understandable error that asks the user to install loopMIDI.

## Architecture

`midi_wled_bridge.virtual_midi` wraps the installed `teVirtualMIDI.dll` through
Python `ctypes`. A manager owns all ports created during the GUI session and
closes them during application shutdown.

The SDK delivers incoming MIDI bytes to the GUI process through a callback. The
existing bridge remains a separate subprocess, so the manager forwards those
bytes over a loopback-only UDP socket. The bridge gains an optional local UDP
MIDI source. Existing physical and external MIDI inputs continue to use `mido`
unchanged.

## Error Handling

Blank and duplicate port names are rejected. DLL loading and SDK creation
errors are reported in the GUI without crashing the application. Loopback UDP
packets received before the bridge starts are intentionally discarded.

## Testing

Unit tests use a fake SDK DLL to verify creation, byte forwarding, duplicate
validation, and cleanup. Bridge tests verify conversion of local UDP datagrams
into `mido.Message` objects. GUI tests verify command construction and the
presence of the requested button and dialog labels. A Windows smoke test creates
and closes one real SDK port when the installed driver is available.
