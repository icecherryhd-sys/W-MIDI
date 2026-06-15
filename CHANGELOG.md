# Changelog

## 1.1.0 - 2026-05-30

- Rebuilt the desktop interface as a PySide6 dashboard.
- Added independent multi-bridge instances with numbered tabs, add, and remove
  controls. Running bridges continue while another instance is selected.
- Added WLED discovery, connection tests, MIDI port reload, and saved workspace
  configuration.
- Added temporary virtual MIDI port creation from inside W-MIDI when the
  loopMIDI virtualMIDI driver is installed.
- Added a palette dropdown, Launchpad-style palette file support, a live
  128-color preview, and per-bridge sun/moon brightness scaling without
  changing the original palette files.
- Added realtime LED preview rendering with the configured LED count.
- Added a pop-out LED layout editor with visual placement, multi-select,
  dragging, rotation, reset, JSON import, and JSON export.

## 1.0.0 - 2026-05-27

- Standardized the public application name as "W-MIDI".
- Added user help in English and German.
- Added a Windows GUI launcher workflow.
- Added release metadata, packaging configuration, and release checklist files.
- Added tests for release branding and help-file behavior.
