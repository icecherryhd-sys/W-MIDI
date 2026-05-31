# W-MIDI Virtual MIDI Ports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add temporary W-MIDI-owned virtual MIDI ports backed by the installed virtualMIDI driver.

**Architecture:** Wrap `teVirtualMIDI.dll` with `ctypes`, own ports in the GUI,
and forward callback bytes over loopback UDP to the existing bridge subprocess.
Keep the current `mido` device path intact for ordinary MIDI inputs.

**Tech Stack:** Python, ctypes, tkinter, UDP loopback, mido, unittest

---

### Task 1: virtualMIDI SDK wrapper

**Files:**
- Create: `midi_wled_bridge/virtual_midi.py`
- Create: `tests/test_virtual_midi.py`

- [ ] Write fake-DLL tests for creation, callback forwarding, duplicate names,
  blank names, and `close_all`.
- [ ] Run `py -3 -m unittest tests.test_virtual_midi -v` and confirm failure
  because the module is missing.
- [ ] Implement `VirtualMidiPortManager`.
- [ ] Re-run the focused test and confirm it passes.

### Task 2: Bridge loopback MIDI source

**Files:**
- Modify: `midi_wled_bridge/bridge.py`
- Modify: `midi_wled_bridge/cli.py`
- Create: `tests/test_virtual_midi_bridge.py`

- [ ] Write a failing test that sends MIDI bytes through a local UDP socket and
  expects parsed `mido.Message` values.
- [ ] Add `read_virtual_midi_messages`, `--virtual-midi-udp-port`, and the
  optional bridge source selection.
- [ ] Run the focused bridge tests and confirm they pass.

### Task 3: GUI dialog and lifecycle

**Files:**
- Modify: `midi_wled_bridge/gui.py`
- Create: `tests/test_gui_virtual_midi.py`

- [ ] Write failing tests for subprocess arguments and requested GUI labels.
- [ ] Add `Create New Midi Port`, the prefilled dialog with `Cancel` and `Add`,
  selector refresh, selected virtual source routing, and close-time cleanup.
- [ ] Run the focused GUI tests and confirm they pass.

### Task 4: Verification

**Files:**
- Modify: `README.md`
- Modify: `README_EN.txt`

- [ ] Document the installed-loopMIDI requirement and temporary port behavior.
- [ ] Run `py -3 -m unittest discover -s tests -v`.
- [ ] Run a Windows smoke test that creates and closes `W-MIDI Smoke Test`
  through the installed DLL.
