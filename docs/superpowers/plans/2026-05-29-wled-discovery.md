# WLED Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `Find WLED` GUI feature that scans the local network for WLED devices and fills the selected device IP into the existing WLED IP field.

**Architecture:** Put network discovery in `midi_wled_bridge.discovery` with injected fetch support for tests. Keep Tk work in `midi_wled_bridge.gui` limited to a button, a result window, and background-thread coordination.

**Tech Stack:** Python standard library, Tkinter, unittest.

---

### Task 1: Discovery Module

**Files:**
- Create: `midi_wled_bridge/discovery.py`
- Test: `tests/test_wled_discovery.py`

- [ ] Write tests for parsing WLED `/json/info` responses and ignoring invalid hosts.
- [ ] Run `python -m unittest tests.test_wled_discovery` and confirm the module import fails.
- [ ] Implement `WledDevice`, `discover_wled_devices`, local network candidate generation, and HTTP JSON fetch.
- [ ] Run `python -m unittest tests.test_wled_discovery` and confirm it passes.

### Task 2: GUI Hook

**Files:**
- Modify: `midi_wled_bridge/gui.py`
- Test: `tests/test_gui_wled_discovery.py`

- [ ] Write a source-level GUI test that checks for the `Find WLED` button and discovery methods.
- [ ] Run `python -m unittest tests.test_gui_wled_discovery` and confirm it fails.
- [ ] Add the button, result popup, background thread, and IP selection behavior.
- [ ] Run `python -m unittest tests.test_gui_wled_discovery tests.test_wled_discovery` and confirm both pass.

### Task 3: Regression Check

**Files:**
- Existing test suite

- [ ] Run `python -m unittest discover tests`.
- [ ] Fix any regressions while keeping the discovery behavior unchanged.
