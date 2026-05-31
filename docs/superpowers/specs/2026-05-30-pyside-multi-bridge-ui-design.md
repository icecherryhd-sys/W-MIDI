# PySide6 Multi-Bridge UI Design

## Goal

Replace the Tkinter desktop interface with a PySide6 dashboard that closely
matches the supplied black, rounded-card reference while adding persistent
multi-bridge instances for multi-device WLED setups.

## Visual System

- Use a black application stage with a narrow left rail.
- Reuse the W-MIDI executable icon at the top of the rail.
- Represent each bridge instance as a circular `W` tab.
- Keep the circular `+` action at the bottom to create an instance.
- Use dark charcoal cards with 22-26 px radii.
- Use lime green as the primary accent, orange as the secondary accent, white
  text, and restrained muted gray labels.
- Put a circular `?` help button at the top right. It opens `README_EN.txt`.
- Remove the reference dashboard's unrelated top navigation and profile UI.

## Dashboard Layout

- Upper left card: `CONNECTION SETTINGS`.
- Upper middle card: `COLOR ENGINE`.
- Lower left card: `LED / MIDI MAPPING`.
- Right card: `BRIDGE EXECUTION`.
- `BRIDGE EXECUTION` contains `Save Config`, `Reload Ports`, and
  `Create New Midi Port` as pressable controls, bridge start/stop actions,
  telemetry values, status, and a compact expandable bridge log.

## Multi-Bridge Behavior

- Each bridge instance owns independent settings, process state, log lines,
  telemetry, and optional virtual MIDI ports.
- Clicking a circular `W` tab changes the visible editor without interrupting
  other running instances.
- Clicking `+` creates a new stopped instance with defaults and selects it.
- Instances and settings are saved in `config.json`.
- Saved instances reappear after restart but never auto-start.
- Closing the app terminates every bridge subprocess and closes every temporary
  virtual MIDI port created during that session.

## Architecture

Keep MIDI processing, CLI, WLED discovery, and virtualMIDI support unchanged.
Add a Qt settings model, a bridge process controller, and focused Qt widgets.
Make `midi_wled_bridge.gui` a compatibility launcher for the new Qt app while
retaining the former Tkinter implementation as `midi_wled_bridge.legacy_gui`.

## Error Handling

- Missing PySide6 produces a clear installation message.
- Validation errors remain per-instance and are shown before save or start.
- A missing virtualMIDI driver produces the existing loopMIDI installation
  guidance.
- Failed subprocess starts leave the selected instance stopped and show the
  error in both a dialog and its log.

## Testing

- Unit-test config migration from the old single-instance JSON format.
- Unit-test multi-instance persistence without automatic runtime restoration.
- Unit-test per-instance subprocess arguments and lifecycle using fakes.
- Unit-test expected visual tokens and major card labels.
- Run the complete existing suite to preserve MIDI, CLI, and virtualMIDI
  behavior.
- Launch the PySide6 interface offscreen and capture a screenshot for visual
  comparison against the supplied reference.
