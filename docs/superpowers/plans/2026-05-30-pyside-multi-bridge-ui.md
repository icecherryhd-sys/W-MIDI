# PySide6 Multi-Bridge UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Tkinter with a rounded PySide6 multi-bridge dashboard while preserving the Python MIDI/WLED backend.

**Architecture:** Store bridge instances in a dedicated model, manage one CLI
subprocess per instance, and compose a Qt dashboard from focused widgets.
Retain the old Tkinter code as a fallback module while `midi_wled_bridge.gui`
becomes the Qt entry point.

**Tech Stack:** Python, PySide6, Qt stylesheets, unittest, existing mido bridge

---

### Task 1: Persistent multi-instance model

**Files:**
- Create: `midi_wled_bridge/qt_model.py`
- Create: `tests/test_qt_model.py`

- [ ] Write failing tests for defaults, legacy config migration, multiple
  instances, add-instance behavior, and save/load round trips.
- [ ] Implement `BridgeInstanceSettings` and `BridgeWorkspace`.
- [ ] Run `py -3 -m unittest tests.test_qt_model -v`.

### Task 2: Per-instance process controller

**Files:**
- Create: `midi_wled_bridge/qt_controller.py`
- Create: `tests/test_qt_controller.py`

- [ ] Write failing tests for independent process state, CLI arguments,
  termination, and shutdown of all instances.
- [ ] Implement `BridgeProcessController`.
- [ ] Run `py -3 -m unittest tests.test_qt_controller -v`.

### Task 3: PySide6 dashboard

**Files:**
- Create: `midi_wled_bridge/qt_gui.py`
- Modify: `midi_wled_bridge/gui.py`
- Modify: `requirements.txt`
- Modify: `pyproject.toml`
- Create: `tests/test_qt_gui_source.py`

- [ ] Write failing source-level tests for required cards, tabs, buttons,
  styling tokens, help action, and Qt launcher.
- [ ] Add the rounded-card Qt dashboard and multi-instance rail.
- [ ] Move the previous Tkinter file to `midi_wled_bridge/legacy_gui.py` and
  make `midi_wled_bridge.gui` start Qt.
- [ ] Run Qt source tests and the complete suite.

### Task 4: Visual and runtime verification

**Files:**
- Modify: `README.md`
- Modify: `README.txt`
- Modify: `README_EN.txt`

- [ ] Document PySide6 installation and multi-bridge workflow.
- [ ] Install dependencies with `py -3 -m pip install -r requirements.txt`.
- [ ] Launch with `QT_QPA_PLATFORM=offscreen`, capture a screenshot, and compare
  it against the supplied dashboard reference.
- [ ] Run `py -3 -m unittest discover -s tests -v`.
- [ ] Run `py -3 -m compileall -q midi_wled_bridge tests`.
