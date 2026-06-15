#!/usr/bin/env python3
"""Rounded PySide6 multi-bridge desktop dashboard for W-MIDI."""

from __future__ import annotations

import os
import json
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from math import ceil
from pathlib import Path

LOCAL_SITE_PACKAGES = Path(__file__).resolve().parents[1] / ".runtime" / "site-packages"
if LOCAL_SITE_PACKAGES.is_dir():
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

try:
    from PySide6.QtCore import QObject, QPointF, QRectF, Qt, Signal
    from PySide6.QtGui import QCloseEvent, QColor, QFontDatabase, QIcon, QMouseEvent, QPainter, QPen
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFormLayout,
        QFrame,
        QFileDialog,
        QGridLayout,
        QHBoxLayout,
        QLabel,
    QLineEdit,
        QListWidget,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:  # pragma: no cover - exercised on machines without Qt
    raise SystemExit("PySide6 is required. Run: py -3 -m pip install -r requirements.txt") from exc

from midi_wled_bridge.app_support import (
    REPO_ROOT,
    app_icon_path,
    build_subprocess_argv,
    find_available_loopback_udp_port,
    open_readme_file,
)
from midi_wled_bridge.bridge import encode_led_frame_line
from midi_wled_bridge.ports import get_input_port_names
from midi_wled_bridge.discovery import discover_wled_devices
from midi_wled_bridge.palette import load_velocity_palette_file, scale_palette_to_full
from midi_wled_bridge.qt_controller import BridgeProcessController
from midi_wled_bridge.qt_model import BridgeInstance, BridgeWorkspace
from midi_wled_bridge.serial_output import (
    SerialPortInfo,
    build_serial_test_frame,
    describe_serial_error,
    describe_serial_port,
    list_serial_ports,
)
from midi_wled_bridge.virtual_midi import VirtualMidiError, VirtualMidiPortManager, virtual_midi_driver_available

CONFIG_PATH = Path(REPO_ROOT) / "config.json"
LIME = "#a8ff4f"
ORANGE = "#ff9d1e"
WINDOWS_FONT_FILES = (
    Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "segoeui.ttf",
    Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf",
    Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arialn.ttf",
)

STYLE = """
QWidget {
    background: #050505;
    color: #ffffff;
    font-family: "Segoe UI";
    font-size: 12px;
}
QFrame#card {
    background: #202020;
    border: 1px solid #292929;
    border-radius: 24px;
}
QFrame#rail {
    background: #050505;
    border-right: 1px solid #151515;
}
QLabel#title {
    font-family: "Arial Narrow";
    font-size: 22px;
    font-weight: 900;
}
QLabel#cardTitle {
    font-family: "Arial Narrow";
    font-size: 15px;
    font-weight: 900;
}
QLabel#muted {
    color: #a2a2a2;
    font-size: 11px;
}
QLabel, QCheckBox {
    background: transparent;
}
QLineEdit, QComboBox, QSpinBox, QTextEdit {
    background: #141414;
    border: 1px solid #343434;
    border-radius: 12px;
    padding: 7px 9px;
    color: #ffffff;
    selection-background-color: #a8ff4f;
    selection-color: #050505;
}
QComboBox::drop-down {
    border: 0;
    width: 22px;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 0;
    height: 0;
    border: 0;
}
QPushButton {
    background: #292929;
    border: 1px solid #363636;
    border-radius: 14px;
    color: #ffffff;
    font-weight: 700;
    padding: 9px 12px;
}
QPushButton:hover {
    background: #353535;
}
QPushButton#primary {
    background: #a8ff4f;
    border-color: #a8ff4f;
    color: #101010;
}
QPushButton#danger {
    background: #ff9d1e;
    border-color: #ff9d1e;
    color: #101010;
}
QPushButton#round {
    min-width: 42px;
    max-width: 42px;
    min-height: 42px;
    max-height: 42px;
    border-radius: 21px;
    padding: 0;
}
QPushButton#round[selected="true"] {
    background: #a8ff4f;
    color: #101010;
    border-color: #a8ff4f;
}
QCheckBox {
    color: #cfcfcf;
    spacing: 8px;
}
"""


def _actual_popen(argv: list[str]):
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
    return subprocess.Popen(
        argv,
        cwd=REPO_ROOT,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )


def load_application_fonts() -> None:
    for path in WINDOWS_FONT_FILES:
        if path.is_file():
            QFontDatabase.addApplicationFont(str(path))


def palette_file_choices(repo_root: Path = Path(REPO_ROOT)) -> tuple[str, ...]:
    palette_dir = repo_root / "palettes"
    if not palette_dir.is_dir():
        return ()
    return tuple(
        path.relative_to(repo_root).as_posix()
        for path in sorted(palette_dir.iterdir(), key=lambda item: item.name.lower())
        if path.is_file()
    )


def normalize_palette_choice(path: str) -> str:
    return path.replace("\\", "/")


def load_preview_palette(path: str) -> list[tuple[int, int, int]]:
    palette_path = Path(path)
    if not palette_path.is_absolute():
        palette_path = Path(REPO_ROOT) / palette_path
    mapping = load_velocity_palette_file(str(palette_path))
    defined = tuple(mapping)
    return [
        mapping[min(defined, key=lambda candidate: abs(candidate - velocity))]
        for velocity in range(128)
    ]


def palette_grid_position(index: int) -> tuple[int, int]:
    block, within_block = divmod(index, 32)
    row_from_bottom, column_in_block = divmod(within_block, 4)
    return block * 4 + column_in_block, 7 - row_from_bottom


def brighten_preview_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(min(255, channel * 4) for channel in rgb)  # type: ignore[return-value]


class Card(QFrame):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 16, 18, 16)
        self.layout.setSpacing(10)
        heading = QLabel(title)
        heading.setObjectName("cardTitle")
        self.layout.addWidget(heading)


class ConnectionPreview(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(52)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt naming
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        lines = (
            (LIME, (0.62, 0.48, 0.58, 0.32, 0.54, 0.44, 0.28, 0.51, 0.42)),
            (ORANGE, (0.34, 0.43, 0.25, 0.61, 0.39, 0.52, 0.36, 0.46, 0.31)),
        )
        for color, values in lines:
            painter.setPen(QPen(QColor(color), 2))
            points = [
                QPointF(index * width / (len(values) - 1), height * value)
                for index, value in enumerate(values)
            ]
            painter.drawPolyline(points)


class ColorGridPreview(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(82)
        self.colors: list[tuple[int, int, int]] = []
        self.scale_to_full = False

    def set_palette_file(self, path: str) -> None:
        try:
            self.colors = load_preview_palette(path)
        except RuntimeError:
            self.colors = []
        self.update()

    def set_scale_to_full(self, enabled: bool) -> None:
        self.scale_to_full = enabled
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt naming
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.colors:
            return
        gap = 2.0
        tile_size = max(
            2.0,
            min(
                (self.width() - gap * 15) / 16,
                (self.height() - gap * 7) / 8,
            ),
        )
        grid_width = tile_size * 16 + gap * 15
        grid_height = tile_size * 8 + gap * 7
        offset_x = max(0.0, (self.width() - grid_width) / 2)
        offset_y = max(0.0, (self.height() - grid_height) / 2)
        painter.setPen(Qt.PenStyle.NoPen)
        for index, rgb in enumerate(self.colors):
            column, row = palette_grid_position(index)
            rect = QRectF(
                offset_x + column * (tile_size + gap),
                offset_y + row * (tile_size + gap),
                tile_size,
                tile_size,
            )
            display_rgb = scale_palette_to_full({0: rgb})[0] if self.scale_to_full else brighten_preview_rgb(rgb)
            painter.setBrush(QColor(*display_rgb))
            painter.drawRoundedRect(rect, 2, 2)


def decode_led_frame_line(line: str) -> list[tuple[int, int, int]]:
    prefix = "LED_FRAME rgb="
    if not line.startswith(prefix):
        raise ValueError("Not an LED frame line.")
    payload = line[len(prefix):]
    if len(payload) % 6:
        raise ValueError("LED frame payload must contain complete RGB triples.")
    try:
        return [
            tuple(bytes.fromhex(payload[offset:offset + 6]))  # type: ignore[misc]
            for offset in range(0, len(payload), 6)
        ]
    except ValueError as exc:
        raise ValueError("LED frame payload must be hexadecimal.") from exc


@dataclass(frozen=True)
class MappingTile:
    x: float
    y: float
    size: float
    dot_gap: float
    dot_radius: float


def mapping_grid_layout(count: int, width: float, height: float) -> list[MappingTile]:
    if count <= 0 or width <= 0 or height <= 0:
        return []
    gap = 7.0
    best: tuple[float, int, int, float, float] | None = None
    for columns in range(1, count + 1):
        rows = ceil(count / columns)
        dot_gap = 0.0
        dot_radius = 0.0
        size = min(
            (width - gap * (columns - 1)) / columns,
            (height - gap * (rows - 1)) / rows,
        )
        if size > 0 and (best is None or size > best[0]):
            best = size, columns, rows, dot_gap, dot_radius
    if best is None:
        return []
    size, columns, rows, dot_gap, dot_radius = best
    grid_width = columns * size + (columns - 1) * gap
    cell_height = size
    grid_height = rows * cell_height + (rows - 1) * gap
    offset_x = max(0.0, (width - grid_width) / 2)
    offset_y = max(0.0, (height - grid_height) / 2)
    return [
        MappingTile(
            x=offset_x + (index % columns) * (size + gap),
            y=offset_y + (index // columns) * (cell_height + gap),
            size=size,
            dot_gap=dot_gap,
            dot_radius=dot_radius,
        )
        for index in range(count)
    ]


def custom_mapping_layout(
    positions: list[tuple[float, float]],
    width: float,
    height: float,
) -> list[MappingTile]:
    size = max(12.0, min(34.0, min(width, height) / 14))
    dot_gap = 0.0
    dot_radius = 0.0
    return [
        MappingTile(
            x=position_x * width - size / 2,
            y=position_y * height - size / 2,
            size=size,
            dot_gap=dot_gap,
            dot_radius=dot_radius,
        )
        for position_x, position_y in positions
    ]


def underlights_layout_positions(count: int) -> list[tuple[float, float]]:
    if count <= 0:
        return []
    side_counts = [count // 4] * 4
    for index in range(count % 4):
        side_counts[index] += 1

    left, right = 0.16, 0.84
    top, bottom = 0.16, 0.84
    segments = (
        ((left, bottom), (right, bottom)),
        ((right, bottom), (right, top)),
        ((right, top), (left, top)),
        ((left, top), (left, bottom)),
    )
    positions: list[tuple[float, float]] = []
    for side_count, ((start_x, start_y), (end_x, end_y)) in zip(side_counts, segments):
        for item in range(side_count):
            progress = (item + 0.5) / max(1, side_count)
            positions.append(
                (
                    start_x + (end_x - start_x) * progress,
                    start_y + (end_y - start_y) * progress,
                )
            )
    return positions


def encode_layout_json(positions: list[tuple[float, float]]) -> str:
    return json.dumps(
        {
            "format": "w-midi-led-layout",
            "version": 1,
            "positions": [[round(x, 6), round(y, 6)] for x, y in positions],
        },
        indent=2,
    ) + "\n"


def decode_layout_json(raw: str) -> list[tuple[float, float]]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Layout file is not valid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("format") != "w-midi-led-layout":
        raise ValueError("Layout file is not a W-MIDI LED layout.")
    positions = payload.get("positions")
    if not isinstance(positions, list):
        raise ValueError("Layout file does not contain LED positions.")
    parsed: list[tuple[float, float]] = []
    for position in positions:
        if not isinstance(position, list) or len(position) != 2:
            raise ValueError("Each LED position must contain X and Y.")
        x, y = float(position[0]), float(position[1])
        if not 0 <= x <= 1 or not 0 <= y <= 1:
            raise ValueError("LED positions must stay inside the canvas.")
        parsed.append((x, y))
    return parsed


def rotate_selected_positions(
    positions: list[tuple[float, float]],
    selected: set[int],
    degrees_clockwise: int,
) -> list[tuple[float, float]]:
    rotated = list(positions)
    chosen = [positions[index] for index in selected if 0 <= index < len(positions)]
    if not chosen:
        return rotated
    center_x = sum(position[0] for position in chosen) / len(chosen)
    center_y = sum(position[1] for position in chosen) / len(chosen)
    normalized = degrees_clockwise % 360
    for index in selected:
        if not 0 <= index < len(positions):
            continue
        x, y = positions[index]
        delta_x, delta_y = x - center_x, y - center_y
        if normalized == 90:
            next_x, next_y = center_x - delta_y, center_y + delta_x
        elif normalized == 180:
            next_x, next_y = center_x - delta_x, center_y - delta_y
        elif normalized == 270:
            next_x, next_y = center_x + delta_y, center_y - delta_x
        else:
            next_x, next_y = x, y
        rotated[index] = (max(0.0, min(1.0, next_x)), max(0.0, min(1.0, next_y)))
    return rotated


class MappingPreview(QWidget):
    positionsChanged = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(150)
        self.colors: list[tuple[int, int, int]] = []
        self.led_count = 0
        self.custom_positions: list[tuple[float, float]] = []
        self.editable = False
        self.dragged_index: int | None = None
        self.selected_indexes: set[int] = set()
        self.selection_start: QPointF | None = None
        self.selection_current: QPointF | None = None
        self.drag_start: QPointF | None = None
        self.drag_positions: list[tuple[float, float]] = []

    def set_led_count(self, count: int) -> None:
        self.led_count = max(0, count)
        self.update()

    def set_colors(self, colors: list[tuple[int, int, int]]) -> None:
        self.colors = colors
        self.update()

    def set_custom_positions(self, positions: list[list[float]] | list[tuple[float, float]]) -> None:
        self.custom_positions = [
            (float(position[0]), float(position[1]))
            for position in positions
            if len(position) == 2
        ]
        self.selected_indexes = {index for index in self.selected_indexes if index < len(self.custom_positions)}
        self.update()

    def set_editable(self, editable: bool) -> None:
        if editable and len(self.custom_positions) != self.led_count:
            self.custom_positions = underlights_layout_positions(self.led_count)
            self.positionsChanged.emit(list(self.custom_positions))
        self.editable = editable
        self.setCursor(Qt.CursorShape.OpenHandCursor if editable else Qt.CursorShape.ArrowCursor)
        self.update()

    def _tiles(self) -> list[MappingTile]:
        if len(self.custom_positions) == self.led_count:
            return custom_mapping_layout(self.custom_positions, self.width(), self.height())
        return custom_mapping_layout(underlights_layout_positions(self.led_count), self.width(), self.height())

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt naming
        if not self.editable or event.button() != Qt.MouseButton.LeftButton:
            return
        point = event.position()
        for index, tile in reversed(list(enumerate(self._tiles()))):
            if QRectF(tile.x, tile.y, tile.size, tile.size).contains(point):
                self.dragged_index = index
                if index not in self.selected_indexes:
                    self.selected_indexes = {index}
                self.drag_start = point
                self.drag_positions = list(self.custom_positions)
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.update()
                return
        self.selected_indexes.clear()
        self.selection_start = point
        self.selection_current = point
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt naming
        if not self.editable:
            return
        if self.selection_start is not None:
            self.selection_current = event.position()
            selection = QRectF(self.selection_start, self.selection_current).normalized()
            self.selected_indexes = {
                index
                for index, tile in enumerate(self._tiles())
                if selection.intersects(QRectF(tile.x, tile.y, tile.size, tile.size))
            }
            self.update()
            return
        if self.dragged_index is None or self.drag_start is None:
            return
        tile = self._tiles()[self.dragged_index]
        margin_x = tile.size / 2 / max(1, self.width())
        margin_y = tile.size / 2 / max(1, self.height())
        point = event.position()
        delta_x = (point.x() - self.drag_start.x()) / max(1, self.width())
        delta_y = (point.y() - self.drag_start.y()) / max(1, self.height())
        for index in self.selected_indexes:
            origin_x, origin_y = self.drag_positions[index]
            self.custom_positions[index] = (
                max(margin_x, min(1 - margin_x, origin_x + delta_x)),
                max(margin_y, min(1 - margin_y, origin_y + delta_y)),
            )
        self.positionsChanged.emit(list(self.custom_positions))
        self.update()

    def mouseReleaseEvent(self, _event: QMouseEvent) -> None:  # noqa: N802 - Qt naming
        self.dragged_index = None
        self.drag_start = None
        self.drag_positions = []
        self.selection_start = None
        self.selection_current = None
        self.setCursor(Qt.CursorShape.OpenHandCursor if self.editable else Qt.CursorShape.ArrowCursor)
        self.update()

    def rotate_selection(self, degrees_clockwise: int) -> None:
        self.custom_positions = rotate_selected_positions(
            self.custom_positions,
            self.selected_indexes,
            degrees_clockwise,
        )
        self.positionsChanged.emit(list(self.custom_positions))
        self.update()

    def reset_layout(self) -> None:
        self.custom_positions = underlights_layout_positions(self.led_count)
        self.selected_indexes.clear()
        self.positionsChanged.emit(list(self.custom_positions))
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt naming
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for index, tile in enumerate(self._tiles()):
            color = self.colors[index] if index < len(self.colors) else (0, 0, 0)
            rect = QRectF(tile.x, tile.y, tile.size, tile.size)
            painter.setBrush(QColor(*color))
            painter.setPen(QPen(QColor(LIME if index in self.selected_indexes else "#383838"), 2 if index in self.selected_indexes else 1))
            painter.drawRoundedRect(rect, min(8, tile.size / 4), min(8, tile.size / 4))
        if self.selection_start is not None and self.selection_current is not None:
            painter.setBrush(QColor(168, 255, 79, 35))
            painter.setPen(QPen(QColor(LIME), 1))
            painter.drawRect(QRectF(self.selection_start, self.selection_current).normalized())


class MappingPopout(QDialog):
    positionsChanged = Signal(list)

    def __init__(
        self,
        led_count: int,
        colors: list[tuple[int, int, int]],
        positions: list[list[float]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("W-MIDI LED Layout")
        self.setMinimumSize(820, 560)
        layout = QHBoxLayout(self)
        self.preview = MappingPreview()
        self.preview.set_led_count(led_count)
        self.preview.set_colors(colors)
        self.preview.set_custom_positions(positions)
        self.preview.positionsChanged.connect(self.positionsChanged.emit)
        layout.addWidget(self.preview, 1)
        actions = QVBoxLayout()
        save_button = QPushButton("SAVE LAYOUT")
        save_button.clicked.connect(self._save_layout)
        actions.addWidget(save_button)
        import_button = QPushButton("IMPORT LAYOUT")
        import_button.clicked.connect(self._import_layout)
        actions.addWidget(import_button)
        reset_button = QPushButton("RESET LAYOUT")
        reset_button.clicked.connect(self.preview.reset_layout)
        actions.addWidget(reset_button)
        actions.addSpacing(12)
        for label, degrees in (
            ("90° Left", 270),
            ("90° Right", 90),
            ("180° Left", 180),
            ("180° Right", 180),
        ):
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, value=degrees: self.preview.rotate_selection(value))
            actions.addWidget(button)
        actions.addStretch(1)
        self.edit_button = QPushButton("EDIT LAYOUT")
        self.edit_button.clicked.connect(self._toggle_edit)
        actions.addWidget(self.edit_button)
        layout.addLayout(actions)

    def _toggle_edit(self) -> None:
        editing = not self.preview.editable
        self.preview.set_editable(editing)
        self.edit_button.setText("DONE EDITING" if editing else "EDIT LAYOUT")

    def set_colors(self, colors: list[tuple[int, int, int]]) -> None:
        self.preview.set_colors(colors)

    def set_led_count(self, count: int) -> None:
        self.preview.set_led_count(count)

    def _save_layout(self) -> None:
        path, _filter = QFileDialog.getSaveFileName(
            self,
            "Save W-MIDI LED Layout",
            "w-midi-layout.json",
            "W-MIDI LED Layout (*.json)",
        )
        if not path:
            return
        try:
            Path(path).write_text(encode_layout_json(self.preview.custom_positions), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "Could not save layout", str(exc))

    def _import_layout(self) -> None:
        path, _filter = QFileDialog.getOpenFileName(
            self,
            "Import W-MIDI LED Layout",
            "",
            "W-MIDI LED Layout (*.json)",
        )
        if not path:
            return
        try:
            positions = decode_layout_json(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Could not import layout", str(exc))
            return
        if len(positions) != self.preview.led_count:
            QMessageBox.critical(
                self,
                "Could not import layout",
                f"Layout contains {len(positions)} LEDs, but this bridge uses {self.preview.led_count}.",
            )
            return
        self.preview.set_custom_positions(positions)
        self.preview.positionsChanged.emit(list(self.preview.custom_positions))


class BridgeEvents(QObject):
    output = Signal(str, str)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        load_application_fonts()
        self.setWindowTitle("W-MIDI")
        self.setWindowIcon(QIcon(app_icon_path()))
        self.resize(1380, 860)
        self.setMinimumSize(1120, 720)
        self.workspace = BridgeWorkspace.load(CONFIG_PATH)
        self.events = BridgeEvents()
        self.events.output.connect(self._handle_bridge_output)
        self.controller = BridgeProcessController(
            argv_builder=build_subprocess_argv,
            popen_factory=_actual_popen,
            output_callback=lambda instance, line: self.events.output.emit(instance.id, line),
        )
        self.virtual_managers: dict[str, VirtualMidiPortManager] = {}
        self.virtual_udp_ports: dict[str, int] = {}
        self.instance_buttons: dict[str, QPushButton] = {}
        self.preview_frames: dict[str, list[tuple[int, int, int]]] = {}
        self.mapping_popouts: dict[str, MappingPopout] = {}
        self.fields: dict[str, QWidget] = {}
        self.serial_port_infos: dict[str, SerialPortInfo] = {}
        self._build()
        self._rebuild_instance_buttons()
        self._load_selected()

    def _build(self) -> None:
        root = QWidget()
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_rail())

        stage = QWidget()
        stage_layout = QVBoxLayout(stage)
        stage_layout.setContentsMargins(26, 22, 26, 24)
        stage_layout.setSpacing(18)
        stage_layout.addLayout(self._build_header())

        cards = QGridLayout()
        cards.setHorizontalSpacing(18)
        cards.setVerticalSpacing(18)
        cards.setColumnStretch(0, 3)
        cards.setColumnStretch(1, 3)
        cards.setColumnStretch(2, 5)
        cards.setRowStretch(0, 2)
        cards.setRowStretch(1, 3)
        cards.addWidget(self._build_connection_card(), 0, 0)
        cards.addWidget(self._build_color_card(), 0, 1)
        cards.addWidget(self._build_mapping_card(), 1, 0, 1, 2)
        cards.addWidget(self._build_execution_card(), 0, 2, 2, 1)
        stage_layout.addLayout(cards, 1)
        outer.addWidget(stage, 1)
        self.setCentralWidget(root)

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        title = QLabel("W-MIDI")
        title.setObjectName("title")
        header.addWidget(title)
        self.instance_title = QLabel("BRIDGE 1")
        self.instance_title.setObjectName("muted")
        header.addWidget(self.instance_title)
        header.addStretch(1)
        help_button = QPushButton("?")
        help_button.setObjectName("round")
        help_button.clicked.connect(self._open_help)
        header.addWidget(help_button)
        return header

    def _build_rail(self) -> QFrame:
        rail = QFrame()
        rail.setObjectName("rail")
        rail.setFixedWidth(82)
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)
        logo = QLabel()
        logo.setPixmap(QIcon(app_icon_path()).pixmap(46, 46))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(34)
        self.instance_layout = QVBoxLayout()
        self.instance_layout.setSpacing(10)
        layout.addLayout(self.instance_layout)
        layout.addStretch(1)
        remove_button = QPushButton("-")
        remove_button.setObjectName("round")
        remove_button.clicked.connect(self._remove_instance)
        add_button = QPushButton("+")
        add_button.setObjectName("round")
        add_button.clicked.connect(self._add_instance)
        layout.addWidget(remove_button)
        layout.addWidget(add_button)
        return rail

    def _line(self, key: str, placeholder: str = "") -> QLineEdit:
        widget = QLineEdit()
        widget.setPlaceholderText(placeholder)
        self.fields[key] = widget
        return widget

    def _spin(self, key: str, minimum: int, maximum: int) -> QSpinBox:
        widget = QSpinBox()
        widget.setRange(minimum, maximum)
        self.fields[key] = widget
        return widget

    def _combo(self, key: str, values: list[str]) -> QComboBox:
        widget = QComboBox()
        widget.addItems(values)
        self.fields[key] = widget
        return widget

    def _form_card(self, title: str) -> tuple[Card, QFormLayout]:
        card = Card(title)
        form = QFormLayout()
        form.setSpacing(9)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        card.layout.addLayout(form)
        return card, form

    def _build_connection_card(self) -> Card:
        card = Card("CONNECTION SETTINGS")
        self.connection_summary = QLabel("Wireless")
        self.connection_summary.setObjectName("muted")
        card.layout.addWidget(self.connection_summary)

        card_form = QFormLayout()
        card_form.setSpacing(10)
        card_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.midi_combo = self._combo("midi_port", [])
        card_form.addRow("MIDI INPUT", self.midi_combo)
        card.layout.addLayout(card_form)

        setup_buttons = QHBoxLayout()
        wireless_setup = QPushButton("Wireless Setup")
        wireless_setup.clicked.connect(self._open_wireless_setup)
        setup_buttons.addWidget(wireless_setup)
        wired_setup = QPushButton("Wired Setup")
        wired_setup.clicked.connect(self._open_wired_setup)
        setup_buttons.addWidget(wired_setup)
        card.layout.addLayout(setup_buttons)

        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self._test_connection)
        card.layout.addWidget(self.test_connection_button)
        create_port = QPushButton("Create Midi Port")
        create_port.clicked.connect(self._create_virtual_port)
        card.layout.addWidget(create_port)
        self.connection_test_status = QLabel("Wireless mode sends WLED UDP realtime packets.")
        self.connection_test_status.setObjectName("muted")
        card.layout.addWidget(self.connection_test_status)

        self.output_mode_combo = self._combo("output_mode", ["Wireless", "Wired"])
        self.output_mode_combo.currentTextChanged.connect(self._refresh_connection_mode)

        self.wireless_settings_dialog = QDialog(self)
        self.wireless_settings_dialog.setWindowTitle("Wireless Setup")
        self.wireless_settings_dialog.setMinimumSize(460, 260)
        wireless_layout = QVBoxLayout(self.wireless_settings_dialog)
        wireless_layout.setContentsMargins(18, 16, 18, 16)
        wireless_layout.setSpacing(12)
        wireless_form = QFormLayout()
        wireless_form.setSpacing(10)
        wireless_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        wireless_layout.addLayout(wireless_form)
        wireless_form.addRow("WLED IP", self._line("wled_ip"))
        wireless_form.addRow("UDP PORT", self._spin("wled_port", 1, 65535))
        self.find_wled_button = QPushButton("Find WLED")
        self.find_wled_button.clicked.connect(self._find_wled)
        wireless_layout.addWidget(self.find_wled_button)
        wireless_save = QPushButton("Save")
        wireless_save.clicked.connect(self._save_wireless_setup)
        wireless_layout.addWidget(wireless_save)

        self.wireless_panel = QWidget()

        self.wired_settings_dialog = QDialog(self)
        self.wired_settings_dialog.setWindowTitle("Wired Setup")
        self.wired_settings_dialog.setMinimumSize(520, 360)
        wired_layout = QVBoxLayout(self.wired_settings_dialog)
        wired_layout.setContentsMargins(18, 16, 18, 16)
        wired_layout.setSpacing(12)
        self.wired_panel = QWidget()
        wired_form = QFormLayout(self.wired_panel)
        wired_form.setSpacing(10)
        wired_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        wired_form.setContentsMargins(0, 0, 0, 0)
        self.serial_combo = self._combo("serial_port", [])
        self.serial_combo.setEditable(True)
        wired_form.addRow("COM PORT", self.serial_combo)
        wired_form.addRow("BAUDRATE", self._combo("serial_baudrate", ["115200", "230400", "460800", "921600"]))
        wired_form.addRow("SERIAL FPS", self._combo("serial_fps", ["30", "60", "90"]))
        wired_form.addRow("START DELAY MS", self._spin("serial_start_delay_ms", 0, 5000))
        self.serial_auto_reconnect = QCheckBox("Auto reconnect serial port")
        self.fields["serial_auto_reconnect"] = self.serial_auto_reconnect
        wired_form.addRow("", self.serial_auto_reconnect)
        self.serial_blackout_on_disconnect = QCheckBox("Send black frame when disconnecting")
        self.fields["serial_blackout_on_disconnect"] = self.serial_blackout_on_disconnect
        wired_form.addRow("", self.serial_blackout_on_disconnect)
        wired_layout.addWidget(self.wired_panel)
        self.find_com_button = QPushButton("Find COM Ports")
        self.find_com_button.clicked.connect(self._reload_serial_ports)
        wired_layout.addWidget(self.find_com_button)
        wired_save = QPushButton("Save")
        wired_save.clicked.connect(self._save_wired_setup)
        wired_layout.addWidget(wired_save)
        return card

    def _build_color_card(self) -> Card:
        card = Card("")
        card.layout.takeAt(0).widget().deleteLater()
        color_header = QHBoxLayout()
        heading = QLabel("COLOR ENGINE")
        heading.setObjectName("cardTitle")
        color_header.addWidget(heading)
        color_header.addStretch(1)
        self.palette_sun = QPushButton("☀")
        self.palette_sun.setObjectName("round")
        self.palette_sun.setToolTip("Scale this bridge palette from 0..63 to maximum 0..255 brightness")
        self.palette_sun.clicked.connect(lambda: self._set_palette_scale_to_full(True))
        self.palette_moon = QPushButton("☾")
        self.palette_moon.setObjectName("round")
        self.palette_moon.setToolTip("Use the original palette values for this bridge")
        self.palette_moon.clicked.connect(lambda: self._set_palette_scale_to_full(False))
        color_header.addWidget(self.palette_sun)
        color_header.addWidget(self.palette_moon)
        card.layout.addLayout(color_header)
        palette_preview = QWidget()
        palette_preview.setStyleSheet("background: transparent;")
        palette_layout = QHBoxLayout(palette_preview)
        palette_layout.setContentsMargins(0, 0, 0, 0)
        palette_layout.setSpacing(10)
        self.color_grid_preview = ColorGridPreview()
        self.color_grid_preview.setMinimumHeight(140)
        palette_layout.addWidget(self.color_grid_preview, 1)
        card.layout.addWidget(palette_preview)
        form = QFormLayout()
        form.setSpacing(9)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.addRow(
            "MODE",
            self._combo(
                "color_mode",
                ["velocity_palette", "fixed", "velocity_white", "velocity_red", "velocity_blue", "rainbow_note"],
            ),
        )
        form.addRow("FIXED RGB", self._line("fixed_color", "0,120,255"))
        palette_file = self._combo("velocity_palette_file", list(palette_file_choices()))
        form.addRow("PALETTE FILE", palette_file)
        palette_file.currentTextChanged.connect(self.color_grid_preview.set_palette_file)
        card.layout.addLayout(form)
        return card

    def _build_mapping_card(self) -> Card:
        card, form = self._form_card("LED / MIDI MAPPING")
        led_count = self._spin("led_count", 1, 9999)
        form.addRow("TOTAL LED COUNT", led_count)
        form.addRow("START NOTE", self._spin("base_note", 0, 127))
        form.addRow("LISTEN CHANNEL", self._combo("midi_channel", ["All"] + [str(index) for index in range(1, 17)]))
        form.addRow("LEDS PER CHANNEL", self._line("channel_bank_size"))
        self.mapping_preview = MappingPreview()
        led_count.valueChanged.connect(self.mapping_preview.set_led_count)
        led_count.valueChanged.connect(self._mapping_led_count_changed)
        popout = QPushButton("Edit Custom Led Layout")
        popout.clicked.connect(self._open_mapping_popout)
        card.layout.addWidget(popout)
        return card

    def _build_execution_card(self) -> Card:
        card = Card("BRIDGE EXECUTION")
        actions = QHBoxLayout()
        for label, callback in (
            ("Save Config", self._save),
            ("Reload Ports", self._reload_ports),
        ):
            button = QPushButton(label)
            button.clicked.connect(callback)
            actions.addWidget(button)
        card.layout.addLayout(actions)

        self.status_label = QLabel("●  READY")
        self.status_label.setStyleSheet(f"color: {LIME}; font-weight: 800;")
        card.layout.addWidget(self.status_label)

        metrics = QGridLayout()
        self.metric_labels: dict[str, QLabel] = {}
        self.metric_caption_labels: dict[str, QLabel] = {}
        for column, (key, value, caption, color) in enumerate(
            (("fps", "0.0", "FPS", LIME), ("midi_per_s", "0.0", "MIDI / SEC", ORANGE), ("output_per_s", "0.0", "OUT / SEC", "#ffffff"))
        ):
            number = QLabel(value)
            number.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 900;")
            metrics.addWidget(number, 0, column)
            self.metric_labels[key] = number
            label = QLabel(caption)
            label.setObjectName("muted")
            metrics.addWidget(label, 1, column)
            self.metric_caption_labels[key] = label
        card.layout.addLayout(metrics)

        start = QPushButton("START BRIDGE")
        start.setObjectName("primary")
        start.clicked.connect(self._start)
        card.layout.addWidget(start)
        stop = QPushButton("STOP BRIDGE")
        stop.setObjectName("danger")
        stop.clicked.connect(self._stop)
        card.layout.addWidget(stop)

        self.verbose = QCheckBox("Verbose output in log")
        self.fields["verbose"] = self.verbose
        card.layout.addWidget(self.verbose)
        tuning, form = self._form_card("RUNTIME")
        form.addRow("FRAME INTERVAL MS", self._spin("frame_interval_ms", 0, 1000))
        form.addRow("MIDI READ BURST", self._spin("midi_read_burst", 1, 4096))
        card.layout.addWidget(tuning)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Bridge log")
        card.layout.addWidget(self.log, 1)
        return card

    def _append_log(self, text: str) -> None:
        self._current().log_lines.append(text)
        self.log.append(text)

    def _handle_bridge_output(self, instance_id: str, line: str) -> None:
        instance = next((item for item in self.workspace.instances if item.id == instance_id), None)
        if instance is None:
            return
        if line.startswith("LED_FRAME "):
            try:
                colors = decode_led_frame_line(line)
            except ValueError:
                return
            self.preview_frames[instance_id] = colors
            if instance_id == self.workspace.selected_instance_id:
                self.mapping_preview.set_colors(colors)
            popout = self.mapping_popouts.get(instance_id)
            if popout is not None:
                popout.set_colors(colors)
            return
        instance.log_lines.append(line)
        if instance_id == self.workspace.selected_instance_id:
            if line.startswith("TELEMETRY "):
                values = dict(part.split("=", 1) for part in line.split()[1:] if "=" in part)
                serial_active = values.get("serial_state") not in (None, "disabled")
                if "output_per_s" in self.metric_labels:
                    output_key = "serial_per_s" if serial_active else "udp_per_s"
                    self.metric_labels["output_per_s"].setText(values.get(output_key, "0.0"))
                    self.metric_caption_labels["output_per_s"].setText("SERIAL / SEC" if serial_active else "UDP / SEC")
                for key, label in self.metric_labels.items():
                    if key == "output_per_s":
                        continue
                    if key in values:
                        label.setText(values[key])
            else:
                self.log.append(line)

    def _rebuild_instance_buttons(self) -> None:
        while self.instance_layout.count():
            item = self.instance_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.instance_buttons.clear()
        for index, instance in enumerate(self.workspace.instances, start=1):
            button = QPushButton(str(index))
            button.setObjectName("round")
            button.clicked.connect(lambda _checked=False, instance_id=instance.id: self._switch_instance(instance_id))
            self.instance_layout.addWidget(button)
            self.instance_buttons[instance.id] = button
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        for instance_id, button in self.instance_buttons.items():
            button.setProperty("selected", instance_id == self.workspace.selected_instance_id)
            button.style().unpolish(button)
            button.style().polish(button)

    def _switch_instance(self, instance_id: str) -> None:
        self._store_selected()
        self.workspace.selected_instance_id = instance_id
        self._refresh_tabs()
        self._load_selected()

    def _add_instance(self) -> None:
        self._store_selected()
        self.workspace.add_instance()
        self._rebuild_instance_buttons()
        self._load_selected()
        self._save()

    def _remove_instance(self) -> None:
        instance = self._current()
        if len(self.workspace.instances) <= 1:
            QMessageBox.information(self, "Cannot remove bridge", "At least one bridge instance must remain.")
            return
        answer = QMessageBox.question(
            self,
            "Remove bridge",
            f"Remove {instance.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.controller.stop(instance)
        manager = self.virtual_managers.pop(instance.id, None)
        if manager is not None:
            manager.close_all()
        self.virtual_udp_ports.pop(instance.id, None)
        popout = self.mapping_popouts.pop(instance.id, None)
        if popout is not None:
            popout.close()
        self.workspace.remove_selected_instance()
        self._rebuild_instance_buttons()
        self._load_selected()
        self._save()

    def _current(self) -> BridgeInstance:
        return self.workspace.selected()

    def _display_output_mode(self, stored: object) -> str:
        return "Wired" if str(stored).lower() in ("serial", "wired") else "Wireless"

    def _stored_output_mode(self) -> str:
        return "serial" if self.output_mode_combo.currentText() == "Wired" else "udp"

    def _open_wireless_setup(self) -> None:
        self.output_mode_combo.setCurrentText("Wireless")
        self._reload_ports()
        self._refresh_connection_mode()
        self.wireless_settings_dialog.show()
        self.wireless_settings_dialog.raise_()
        self.wireless_settings_dialog.activateWindow()

    def _open_wired_setup(self) -> None:
        self.output_mode_combo.setCurrentText("Wired")
        self._reload_ports()
        self._refresh_connection_mode()
        self.wired_settings_dialog.show()
        self.wired_settings_dialog.raise_()
        self.wired_settings_dialog.activateWindow()

    def _save_wireless_setup(self) -> None:
        self.output_mode_combo.setCurrentText("Wireless")
        self._save()
        self.wireless_settings_dialog.accept()

    def _save_wired_setup(self) -> None:
        self.output_mode_combo.setCurrentText("Wired")
        self._save()
        self.wired_settings_dialog.accept()

    def _refresh_connection_mode(self) -> None:
        wired = self.output_mode_combo.currentText() == "Wired"
        self.test_connection_button.setText("Test Wired Connection" if wired else "Test Wireless Connection")
        self.connection_summary.setText(
            f"Wired: {self.serial_combo.currentData() or self.serial_combo.currentText() or 'no COM port selected'}"
            if wired
            else f"Wireless: {self.fields['wled_ip'].text()}:{self.fields['wled_port'].value()}"  # type: ignore[union-attr]
        )
        if wired:
            self.connection_test_status.setText("Set the same baudrate in WLED Sync Interfaces / Serial.")
        else:
            self.connection_test_status.setText("Wireless mode sends WLED UDP realtime packets.")

    def _load_selected(self) -> None:
        instance = self._current()
        self.instance_title.setText(instance.name.upper())
        self._reload_ports()
        for key, widget in self.fields.items():
            value = instance.settings.get(key, "")
            if isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value or 0))
            elif isinstance(widget, QComboBox):
                text = str(value)
                if key == "velocity_palette_file":
                    text = normalize_palette_choice(text)
                if key == "output_mode":
                    widget.setCurrentText(self._display_output_mode(value))
                elif key == "serial_port":
                    index = widget.findData(text)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        widget.setCurrentText(text)
                else:
                    widget.setCurrentText(text)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
        self.log.setPlainText("\n".join(instance.log_lines))
        self.mapping_preview.set_led_count(int(instance.settings.get("led_count", 0) or 0))
        self.mapping_preview.set_colors(self.preview_frames.get(instance.id, []))
        palette_file_widget = self.fields["velocity_palette_file"]
        if isinstance(palette_file_widget, QComboBox):
            self.color_grid_preview.set_palette_file(palette_file_widget.currentText())
        self._refresh_palette_scale()
        self._refresh_status()
        self._refresh_connection_mode()

    def _set_palette_scale_to_full(self, enabled: bool) -> None:
        self._store_selected()
        self._current().settings["scale_velocity_palette_to_full"] = enabled
        self.workspace.save(CONFIG_PATH)
        self._refresh_palette_scale()

    def _refresh_palette_scale(self) -> None:
        enabled = bool(self._current().settings.get("scale_velocity_palette_to_full", False))
        self.color_grid_preview.set_scale_to_full(enabled)
        for button, selected in ((self.palette_sun, enabled), (self.palette_moon, not enabled)):
            button.setProperty("selected", selected)
            button.style().unpolish(button)
            button.style().polish(button)

    def _store_selected(self) -> None:
        settings = self._current().settings
        for key, widget in self.fields.items():
            if isinstance(widget, QLineEdit):
                settings[key] = widget.text().strip()
            elif isinstance(widget, QSpinBox):
                settings[key] = widget.value()
            elif isinstance(widget, QComboBox):
                if key == "output_mode":
                    settings[key] = self._stored_output_mode()
                elif key == "serial_port" and widget.currentData():
                    settings[key] = str(widget.currentData())
                else:
                    settings[key] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                settings[key] = widget.isChecked()
        selected_port = str(settings.get("serial_port") or "")
        info = self.serial_port_infos.get(selected_port)
        if info is not None:
            settings["serial_port_vid"] = f"{info.vid:04X}" if info.vid is not None else ""
            settings["serial_port_pid"] = f"{info.pid:04X}" if info.pid is not None else ""
            settings["serial_port_serial_number"] = info.serial_number or ""

    def _mapping_led_count_changed(self, count: int) -> None:
        popout = self.mapping_popouts.get(self._current().id)
        if popout is not None:
            popout.set_led_count(count)

    def _open_mapping_popout(self) -> None:
        self._store_selected()
        instance = self._current()
        existing = self.mapping_popouts.get(instance.id)
        if existing is not None:
            existing.show()
            existing.raise_()
            existing.activateWindow()
            return
        positions = instance.settings.get("led_layout_positions", [])
        if not isinstance(positions, list):
            positions = []
        popout = MappingPopout(
            led_count=int(instance.settings["led_count"]),
            colors=self.preview_frames.get(instance.id, []),
            positions=positions,
            parent=self,
        )
        popout.positionsChanged.connect(
            lambda updated, instance_id=instance.id: self._save_led_layout(instance_id, updated)
        )
        popout.finished.connect(lambda _result, instance_id=instance.id: self.mapping_popouts.pop(instance_id, None))
        self.mapping_popouts[instance.id] = popout
        popout.show()

    def _save_led_layout(self, instance_id: str, positions: list[tuple[float, float]]) -> None:
        instance = next((item for item in self.workspace.instances if item.id == instance_id), None)
        if instance is None:
            return
        instance.settings["led_layout_positions"] = [
            [round(position_x, 6), round(position_y, 6)]
            for position_x, position_y in positions
        ]
        self.workspace.save(CONFIG_PATH)

    def _save(self) -> None:
        self._store_selected()
        self.workspace.save(CONFIG_PATH)
        self._append_log("Settings saved.")

    def _reload_ports(self) -> None:
        current = self.midi_combo.currentText()
        names = list(get_input_port_names())
        manager = self.virtual_managers.get(self._current().id)
        if manager is not None:
            for name in manager.port_names():
                if name not in names:
                    names.append(name)
        self.midi_combo.clear()
        self.midi_combo.addItems(names)
        self.midi_combo.setCurrentText(current)
        self._reload_serial_ports()

    def _reload_serial_ports(self) -> None:
        current = ""
        if hasattr(self, "serial_combo"):
            current = str(self.serial_combo.currentData() or self.serial_combo.currentText())
        self.serial_combo.clear()
        self.serial_port_infos = {}
        for info in list_serial_ports():
            self.serial_port_infos[info.device] = info
            self.serial_combo.addItem(describe_serial_port(info), info.device)
        if current:
            index = self.serial_combo.findData(current)
            if index >= 0:
                self.serial_combo.setCurrentIndex(index)
            else:
                self.serial_combo.setCurrentText(current)
        self._refresh_connection_mode()
        message = f"Found {len(self.serial_port_infos)} COM port{'s' if len(self.serial_port_infos) != 1 else ''}."
        self.connection_test_status.setText(message)
        self._append_log(message)

    def _create_virtual_port(self) -> None:
        driver_available, driver_message = virtual_midi_driver_available()
        if not driver_available:
            QMessageBox.warning(self, "loopMIDI required", driver_message)
            return
        name, accepted = PortNameDialog.get_name(self)
        if not accepted:
            return
        instance = self._current()
        try:
            manager = self.virtual_managers.get(instance.id)
            if manager is None:
                udp_port = find_available_loopback_udp_port()
                manager = VirtualMidiPortManager(udp_port)
                self.virtual_managers[instance.id] = manager
                self.virtual_udp_ports[instance.id] = udp_port
            created = manager.create_port(name)
        except (ValueError, VirtualMidiError) as exc:
            QMessageBox.critical(self, "Could not create MIDI port", str(exc))
            return
        self._reload_ports()
        self.midi_combo.setCurrentText(created)
        self._append_log(f"Created temporary MIDI port: {created}")

    def _start(self) -> None:
        self._store_selected()
        instance = self._current()
        instance.settings.pop("virtual_midi_udp_port", None)
        if instance.id in self.virtual_udp_ports:
            manager = self.virtual_managers[instance.id]
            if manager.has_port(str(instance.settings["midi_port"])):
                instance.settings["virtual_midi_udp_port"] = self.virtual_udp_ports[instance.id]
        try:
            self.controller.start(instance)
        except OSError as exc:
            QMessageBox.critical(self, "Start failed", str(exc))
            self._append_log(f"Start failed: {exc}")
            return
        self._append_log(f"Started {instance.name}.")
        self._refresh_status()

    def _stop(self) -> None:
        instance = self._current()
        self.controller.stop(instance)
        self._append_log(f"Stopped {instance.name}.")
        self._refresh_status()

    def _refresh_status(self) -> None:
        running = self.controller.is_running(self._current())
        self.status_label.setText("●  RUNNING" if running else "●  READY")
        self.status_label.setStyleSheet(f"color: {LIME if running else '#ffffff'}; font-weight: 800;")

    def _test_connection(self) -> None:
        if self.output_mode_combo.currentText() == "Wired":
            self._test_serial_connection()
            return
        try:
            ip = self.fields["wled_ip"].text().strip()  # type: ignore[union-attr]
            port = self.fields["wled_port"].value()  # type: ignore[union-attr]
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(bytes([2, 2, 0, 120, 255]), (ip, port))
            self._append_log(f"Sent test packet to {ip}:{port}.")
            self.connection_test_status.setText(f"Wireless test packet sent to {ip}:{port}.")
        except OSError as exc:
            self.connection_test_status.setText(f"Wireless test failed: {exc}")
            QMessageBox.critical(self, "Test failed", str(exc))

    def _test_serial_connection(self) -> None:
        port = str(self.serial_combo.currentData() or self.serial_combo.currentText()).strip()
        if not port:
            self.connection_test_status.setText("Choose a COM port first.")
            QMessageBox.warning(self, "Test failed", "Choose a COM port first.")
            return
        baudrate = int(self.fields["serial_baudrate"].currentText())  # type: ignore[union-attr]
        led_count = int(self.fields["led_count"].value())  # type: ignore[union-attr]
        start_delay_ms = int(self.fields["serial_start_delay_ms"].value())  # type: ignore[union-attr]
        payload = build_serial_test_frame(led_count)
        test_duration_s = 4.0
        frame_interval_s = 1.0 / 30.0
        try:
            import serial

            with serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0,
                write_timeout=1.0,
                rtscts=False,
                dsrdtr=False,
                xonxoff=False,
            ) as serial_port:
                for name in ("setDTR", "setRTS"):
                    method = getattr(serial_port, name, None)
                    if callable(method):
                        try:
                            method(False)
                        except Exception:
                            pass
                if start_delay_ms:
                    time.sleep(start_delay_ms / 1000.0)
                deadline = time.monotonic() + test_duration_s
                frames_sent = 0
                while time.monotonic() < deadline:
                    written = serial_port.write(payload)
                    if written != len(payload):
                        raise OSError(f"Serial write incomplete: {written}/{len(payload)} bytes")
                    serial_port.flush()
                    frames_sent += 1
                    time.sleep(frame_interval_s)
            self.connection_test_status.setText(
                f"Serial test frame sent to {port}: {frames_sent} frames, {led_count} LEDs at {baudrate}."
            )
            self._append_log(
                f"Serial test frame sent to {port}: {frames_sent} frames, "
                f"{led_count} LEDs, {len(payload)} bytes/frame at {baudrate}."
            )
        except Exception as exc:  # pylint: disable=broad-except
            message = describe_serial_error(port, exc)
            self.connection_test_status.setText(f"Serial test failed: {message}")
            QMessageBox.critical(self, "Serial test failed", message)

    def _find_wled(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Find WLED Devices")
        dialog.setMinimumSize(420, 300)
        layout = QVBoxLayout(dialog)
        status = QLabel("Searching local network...")
        layout.addWidget(status)
        results = QListWidget()
        layout.addWidget(results, 1)
        devices = discover_wled_devices()
        for device in devices:
            results.addItem(f"{device.name} - {device.ip}")
        status.setText(f"Found {len(devices)} WLED device{'s' if len(devices) != 1 else ''}.")
        choose = QPushButton("Use Selected IP")

        def select_ip() -> None:
            if results.currentRow() < 0:
                return
            device = devices[results.currentRow()]
            self.fields["wled_ip"].setText(device.ip)  # type: ignore[union-attr]
            self._append_log(f"Selected WLED device: {device.name} ({device.ip})")
            dialog.accept()

        choose.clicked.connect(select_ip)
        layout.addWidget(choose)
        dialog.exec()

    def _open_help(self) -> None:
        try:
            open_readme_file()
        except OSError as exc:
            QMessageBox.critical(self, "README could not be opened", str(exc))

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt naming
        self._store_selected()
        self.workspace.save(CONFIG_PATH)
        self.controller.shutdown()
        for manager in self.virtual_managers.values():
            manager.close_all()
        for popout in list(self.mapping_popouts.values()):
            popout.close()
        event.accept()


class PortNameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        load_application_fonts()
        self.setWindowTitle("Create New Midi Port")
        self.setFixedWidth(360)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("MIDI PORT NAME"))
        self.name = QLineEdit("W-MIDI")
        self.name.selectAll()
        layout.addWidget(self.name)
        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        add = QPushButton("Add")
        add.setObjectName("primary")
        add.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(add)
        layout.addLayout(buttons)

    @classmethod
    def get_name(cls, parent: QWidget | None = None) -> tuple[str, bool]:
        dialog = cls(parent)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        return dialog.name.text(), accepted


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
