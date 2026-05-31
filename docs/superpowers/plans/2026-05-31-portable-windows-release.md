# Portable Windows Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build W-MIDI v1.1.0 as a portable Windows folder and ZIP that run without a separately installed Python interpreter.

**Architecture:** PyInstaller builds a windowed one-folder distribution with a visible `W-MIDI.exe` and `_internal/`. A small frozen-runtime helper makes the GUI use the executable folder for writable user files and relaunch the same executable in CLI mode for bridge subprocesses. The release script copies editable palettes, layouts, assets, and documentation beside the executable before creating the ZIP.

**Tech Stack:** Python 3, PyInstaller, PowerShell, unittest, PySide6

---

### Task 1: Specify Portable Packaging Behavior

**Files:**
- Modify: `tests/test_release_branding.py`
- Modify: `tests/test_qt_gui_source.py`

- [ ] Add regression assertions for `packaging/windows/build_portable_release.ps1`, PyInstaller one-folder windowed mode, visible editable folders, and frozen executable subprocess mode.
- [ ] Run `py -3 -m unittest tests.test_release_branding tests.test_qt_gui_source -v`.
- [ ] Confirm failures point to the missing portable build flow and frozen runtime behavior.

### Task 2: Add Frozen Runtime Entry Points

**Files:**
- Create: `midi_wled_bridge/runtime.py`
- Create: `midi_wled_bridge/frozen_entry.py`
- Modify: `midi_wled_bridge/gui.py`
- Modify: `midi_wled_bridge/qt_gui.py`

- [ ] Add a helper that resolves the executable directory when frozen and the repository root during source development.
- [ ] Add a frozen entry point that starts the Qt GUI by default and dispatches `--bridge-cli` to the existing CLI.
- [ ] Make GUI resource and config paths use the helper.
- [ ] Make bridge subprocess creation use `W-MIDI.exe --bridge-cli ...` in frozen builds and the existing Python module command during source development.
- [ ] Run the focused unit tests and then `py -3 -m unittest discover -s tests`.

### Task 3: Build Portable Folder And Archive

**Files:**
- Create: `packaging/windows/build_portable_release.ps1`
- Modify: `packaging/windows/build_release_archive.ps1`
- Modify: `README.md`
- Modify: `README.txt`
- Modify: `README_EN.txt`
- Modify: `RELEASE_CHECKLIST.md`

- [ ] Add a PowerShell build script that invokes PyInstaller with `--onedir`, `--windowed`, `_internal`, the application icon, and `midi_wled_bridge.frozen_entry`.
- [ ] Copy visible palettes, layouts, assets, documentation, and example configuration beside the generated executable.
- [ ] Make the archive script call the portable build script and compress the prepared package folder.
- [ ] Update release instructions so normal users extract the ZIP and start `W-MIDI.exe` without installing Python.
- [ ] Run `py -3 -m unittest discover -s tests` and `py -3 -m compileall -q midi_wled_bridge tests`.

### Task 4: Produce And Smoke-Test Release

**Files:**
- Generate: `release/W-MIDI-v1.1.0/`
- Generate: `release/W-MIDI-v1.1.0.zip`

- [ ] Ensure PyInstaller is available for a compatible Python interpreter.
- [ ] Run `powershell -ExecutionPolicy Bypass -File packaging/windows/build_release_archive.ps1`.
- [ ] Start `release/W-MIDI-v1.1.0/W-MIDI.exe`.
- [ ] Confirm the process remains alive after GUI initialization, then close it.
- [ ] Confirm the ZIP contains `W-MIDI-v1.1.0/W-MIDI.exe`, `_internal/`, `palettes/`, and `layouts/`.
