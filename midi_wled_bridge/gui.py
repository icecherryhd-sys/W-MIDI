#!/usr/bin/env python3
"""Desktop GUI for the MIDI -> WLED bridge."""

from __future__ import annotations

import json
import os
import queue
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

from midi_wled_bridge import __version__
from midi_wled_bridge.constants import WLED_REALTIME_PORT
from midi_wled_bridge.ports import get_input_port_names

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
APP_NAME = "W-MIDI"
CONFIG_FILENAME = "config.json"
README_TXT_FILENAME = "README_EN.txt"
APP_ICON_FILENAME = os.path.join("assets", "windows", "w-midi.ico")
LOG_PREVIEW_MAX_CHARS = 120
LOG_QUEUE_LINES_PER_TICK = 40
LOG_QUEUE_MAX_LINES = 2000
LOG_VISIBLE_MAX_LINES = 400

COLOR_MODES = [
    "fixed",
    "velocity_palette",
    "velocity_white",
    "velocity_red",
    "velocity_blue",
    "rainbow_note",
]

THEME = {
    "bg": "#111418",
    "bar": "#15191f",
    "panel": "#181d24",
    "panel_2": "#202630",
    "border": "#303844",
    "input": "#151a21",
    "input_border": "#465261",
    "text": "#f3f6fb",
    "text_dim": "#c0c8d2",
    "text_muted": "#7f8996",
    "cyan": "#00B7FF",
    "cyan_hover": "#23c4ff",
    "cyan_dark": "#123243",
    "green": "#13d18e",
    "green_dark": "#0d3b31",
    "red": "#e74c3c",
    "red_hover": "#f05a4b",
    "secondary": "#202732",
    "secondary_hover": "#2a3341",
    "log_bg": "#090c10",
    "log_line": "#0d1818",
}

DEFAULT_GUI_SETTINGS: dict[str, object] = {
    "wled_ip": "192.168.1.100",
    "wled_port": WLED_REALTIME_PORT,
    "midi_port": "loopMIDI",
    "led_count": 64,
    "base_note": 36,
    "midi_channel": "All",
    "channel_bank_size": "",
    "frame_interval_ms": 5,
    "midi_read_burst": 64,
    "color_mode": "velocity_palette",
    "fixed_color": "0,120,255",
    "velocity_palette_file": "palettes/velocity_palette.txt",
    "verbose": False,
}


def config_path() -> str:
    return os.path.join(REPO_ROOT, CONFIG_FILENAME)


def readme_txt_path() -> str:
    return os.path.join(REPO_ROOT, README_TXT_FILENAME)


def app_icon_path() -> str:
    return os.path.join(REPO_ROOT, APP_ICON_FILENAME)


def open_readme_file() -> None:
    os.startfile(readme_txt_path())


def load_settings() -> dict[str, object]:
    path = config_path()
    if not os.path.isfile(path):
        return dict(DEFAULT_GUI_SETTINGS)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_GUI_SETTINGS)

    merged = dict(DEFAULT_GUI_SETTINGS)
    for key in DEFAULT_GUI_SETTINGS:
        if key in raw:
            merged[key] = raw[key]
    return merged


def save_settings(data: dict[str, object]) -> None:
    clean = {key: data[key] for key in DEFAULT_GUI_SETTINGS if key in data}
    with open(config_path(), "w", encoding="utf-8") as handle:
        json.dump(clean, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def build_subprocess_argv(settings: dict[str, object]) -> list[str]:
    argv = [
        sys.executable,
        "-m",
        "midi_wled_bridge.cli",
        "--wled-ip",
        str(settings["wled_ip"]).strip(),
        "--port",
        str(int(settings["wled_port"])),
        "--midi-port",
        str(settings["midi_port"]).strip(),
        "--led-count",
        str(int(settings["led_count"])),
        "--base-note",
        str(int(settings["base_note"])),
        "--frame-interval-ms",
        str(int(settings["frame_interval_ms"])),
        "--midi-read-burst",
        str(int(settings["midi_read_burst"])),
        "--color-mode",
        str(settings["color_mode"]),
        "--fixed-color",
        str(settings["fixed_color"]).strip(),
    ]

    midi_channel = str(settings.get("midi_channel") or "All").strip()
    if midi_channel and midi_channel.lower() != "all":
        argv.extend(["--midi-channel", str(int(midi_channel))])

    channel_bank_size = str(settings.get("channel_bank_size") or "").strip()
    if channel_bank_size:
        argv.extend(["--channel-bank-size", str(int(channel_bank_size))])

    palette_file = str(settings.get("velocity_palette_file") or "").strip()
    if str(settings["color_mode"]) == "velocity_palette" and palette_file:
        abs_palette = palette_file if os.path.isabs(palette_file) else os.path.abspath(os.path.join(REPO_ROOT, palette_file))
        argv.extend(["--velocity-palette-file", abs_palette])

    if settings.get("verbose"):
        argv.append("--verbose")
    return argv


def _parse_rgb_triple(value: str) -> tuple[int, int, int]:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 3:
        return 0, 120, 255
    try:
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return 0, 120, 255
    return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))


class BridgeGuiApp:
    def __init__(self) -> None:
        self._t = THEME
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        icon_path = app_icon_path()
        if os.path.isfile(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass
        self.root.minsize(1000, 650)
        self.root.configure(bg=self._t["bg"])

        self._proc: subprocess.Popen[str] | None = None
        self._reader_thread: threading.Thread | None = None
        self._stop_reader = threading.Event()
        self._log_queue: queue.Queue[str] = queue.Queue()
        self._dropped_log_lines = 0
        self._visible_log_lines = 0
        self._log_expanded = False
        self._popout_window: tk.Toplevel | None = None
        self._popout_log: tk.Text | None = None
        self._last_log_line = tk.StringVar(value="Settings are saved to config.json.")
        self._telemetry_vars = {
            "fps": tk.StringVar(value="0.0"),
            "midi": tk.StringVar(value="0.0"),
            "udp": tk.StringVar(value="0.0"),
            "last_frame": tk.StringVar(value="-"),
        }

        self._font_ui = tkfont.nametofont("TkDefaultFont")
        try:
            self._font_ui.configure(family="Segoe UI", size=10)
        except tk.TclError:
            pass
        family = self._font_ui.cget("family")
        self._font_title = tkfont.Font(family=family, size=15, weight="bold")
        self._font_card_title = tkfont.Font(family=family, size=11, weight="bold")
        self._font_label = tkfont.Font(family=family, size=8, weight="bold")
        self._font_small = tkfont.Font(family=family, size=8)
        self._font_big = tkfont.Font(family=family, size=11, weight="bold")
        self._font_mono = tkfont.Font(family="Consolas", size=9)
        if "Consolas" not in tkfont.families():
            self._font_mono = tkfont.Font(family="Courier New", size=9)

        self._style = ttk.Style()
        if "clam" in self._style.theme_names():
            self._style.theme_use("clam")
        self._configure_ttk()

        self._rgb_r = tk.StringVar(value="0")
        self._rgb_g = tk.StringVar(value="120")
        self._rgb_b = tk.StringVar(value="255")

        self._build_form()
        self._load_into_form()
        self._poll_log_queue()
        self._set_status_ready()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        for var in (self._rgb_r, self._rgb_g, self._rgb_b, self._led_count, self._base_note, self._channel_bank_size):
            var.trace_add("write", lambda *_: self._refresh_visuals())

    def _configure_ttk(self) -> None:
        self._style.configure(
            "Bridge.TCombobox",
            fieldbackground=self._t["input"],
            background=self._t["secondary"],
            foreground=self._t["text"],
            arrowcolor=self._t["text"],
            bordercolor=self._t["input_border"],
            lightcolor=self._t["input"],
            darkcolor=self._t["input"],
            padding=4,
        )
        self._style.map(
            "Bridge.TCombobox",
            fieldbackground=[("readonly", self._t["input"])],
            selectbackground=[("readonly", self._t["cyan_dark"])],
            selectforeground=[("readonly", self._t["text"])],
        )
        self._style.configure(
            "Bridge.Horizontal.TScale",
            background=self._t["panel"],
            troughcolor=self._t["input"],
        )
        self._style.configure(
            "Bridge.Vertical.TScrollbar",
            background=self._t["secondary"],
            troughcolor=self._t["log_bg"],
            bordercolor=self._t["border"],
            arrowcolor=self._t["text_dim"],
        )

    def _configure_entry(self, widget: tk.Entry | tk.Spinbox) -> None:
        widget.configure(
            bg=self._t["input"],
            fg=self._t["text"],
            insertbackground=self._t["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self._t["input_border"],
            highlightcolor=self._t["cyan"],
            font=self._font_ui,
        )

    def _button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        *,
        bg: str | None = None,
        hover: str | None = None,
        fg: str | None = None,
        padx: int = 14,
        pady: int = 8,
        state: str = "normal",
        font: tkfont.Font | None = None,
    ) -> tk.Button:
        base = bg or self._t["secondary"]
        active = hover or self._t["secondary_hover"]
        text_color = fg or self._t["text"]
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=base,
            fg=text_color,
            activebackground=active,
            activeforeground=text_color,
            relief=tk.FLAT,
            cursor="hand2",
            font=font or self._font_ui,
            padx=padx,
            pady=pady,
            borderwidth=0,
            disabledforeground=self._t["text_muted"],
            state=state,
        )

        def on_enter(_: object) -> None:
            if str(button.cget("state")) != "disabled":
                button.configure(bg=active)

        def on_leave(_: object) -> None:
            if str(button.cget("state")) != "disabled":
                button.configure(bg=base)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def _panel(self, parent: tk.Widget, title: str, description: str = "") -> tk.Frame:
        panel = tk.Frame(parent, bg=self._t["panel"], highlightbackground=self._t["border"], highlightthickness=1)
        header = tk.Frame(panel, bg=self._t["panel"])
        header.pack(fill="x", padx=14, pady=8)
        tk.Label(header, text=title, bg=self._t["panel"], fg=self._t["text"], font=self._font_card_title, anchor="w").pack(
            fill="x"
        )
        if description:
            tk.Label(
                header,
                text=description,
                bg=self._t["panel"],
                fg=self._t["text_dim"],
                font=self._font_small,
                anchor="w",
                justify="left",
                wraplength=520,
            ).pack(fill="x", pady=(2, 0))
        body = tk.Frame(panel, bg=self._t["panel"])
        body.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        return body

    def _label(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(parent, text=text.upper(), bg=self._t["panel"], fg=self._t["text_dim"], font=self._font_label, anchor="w")

    def _field(self, parent: tk.Widget, row: int, column: int, label: str, widget: tk.Widget, *, width: int = 1) -> None:
        self._label(parent, label).grid(row=row * 2, column=column, columnspan=width, sticky="ew", pady=(0, 3), padx=(0, 10))
        widget.grid(row=row * 2 + 1, column=column, columnspan=width, sticky="ew", pady=(0, 8), padx=(0, 10))

    def _build_form(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_header()

        main = tk.Frame(self.root, bg=self._t["bg"])
        main.grid(row=1, column=0, sticky="nsew", padx=18, pady=14)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(1, weight=1)

        self._build_engine(main)
        self._build_mapping(main)
        self._build_color(main)
        self._build_runtime(main)
        self._build_log(main)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=self._t["bar"], height=52, highlightbackground="#2a313b", highlightthickness=1)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.columnconfigure(1, weight=1)

        brand = tk.Frame(header, bg=self._t["bar"])
        brand.grid(row=0, column=0, sticky="w", padx=18)
        logo = tk.Canvas(brand, width=24, height=24, bg=self._t["bar"], highlightthickness=0)
        logo.pack(side="left", pady=13)
        logo.create_rectangle(2, 2, 22, 22, fill=self._t["cyan_dark"], outline=self._t["cyan"], width=1)
        logo.create_line(6, 13, 10, 13, 12, 7, 15, 19, 19, 12, fill=self._t["cyan"], width=2)
        tk.Label(brand, text=APP_NAME, bg=self._t["bar"], fg=self._t["text"], font=self._font_title).pack(
            side="left", padx=(10, 0)
        )

        nav = tk.Frame(header, bg=self._t["bar"])
        nav.grid(row=0, column=1, sticky="w")
        tk.Label(
            nav,
            text="Control Dashboard",
            bg=self._t["secondary"],
            fg=self._t["text"],
            font=self._font_label,
            padx=12,
            pady=7,
        ).pack(side="left", padx=(20, 8))

        status = tk.Frame(header, bg=self._t["bar"])
        status.grid(row=0, column=2, sticky="e", padx=18)
        self._status_pill = tk.Frame(status, bg=self._t["green_dark"], highlightbackground="#17664f", highlightthickness=1)
        self._status_pill.pack(side="left", padx=(0, 14))
        self._status_dot = tk.Canvas(self._status_pill, width=12, height=12, bg=self._t["green_dark"], highlightthickness=0)
        self._status_dot.pack(side="left", padx=(10, 2), pady=5)
        self._status_label = tk.Label(
            self._status_pill,
            text="Ready",
            bg=self._t["green_dark"],
            fg=self._t["green"],
            font=self._font_small,
            padx=8,
        )
        self._status_label.pack(side="left", pady=5)
        help_label = tk.Label(status, text="?", bg=self._t["bar"], fg=self._t["text_dim"], font=self._font_big, cursor="hand2")
        help_label.pack(side="left", padx=6)
        help_label.bind("<Button-1>", lambda _: self._open_readme_clicked())
        tk.Label(status, text="v" + __version__, bg=self._t["bar"], fg=self._t["text_muted"], font=self._font_small).pack(side="left", padx=8)

    def _open_readme_clicked(self) -> None:
        try:
            open_readme_file()
        except OSError as exc:
            messagebox.showerror("README konnte nicht geoeffnet werden", str(exc))

    def _build_engine(self, parent: tk.Frame) -> None:
        engine = tk.Frame(parent, bg=self._t["panel"], highlightbackground=self._t["border"], highlightthickness=1)
        engine.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        engine.columnconfigure(0, weight=3)
        engine.columnconfigure(1, weight=2)

        left = tk.Frame(engine, bg=self._t["panel"])
        left.grid(row=0, column=0, sticky="nsew", padx=16, pady=12)
        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=1)

        tk.Label(left, text="CONNECTION SETTINGS", bg=self._t["panel"], fg=self._t["text"], font=self._font_card_title).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        self._midi_combo = ttk.Combobox(left, width=34, style="Bridge.TCombobox", state="readonly")
        self._midi_combo.configure(values=self._refresh_ports())
        self._field(left, 1, 0, "MIDI input device", self._midi_combo)

        self._wled_ip = tk.StringVar()
        ip_entry = tk.Entry(left, textvariable=self._wled_ip)
        self._configure_entry(ip_entry)
        self._field(left, 1, 1, "WLED controller IP", ip_entry)

        self._wled_port = tk.StringVar()
        port_entry = tk.Entry(left, textvariable=self._wled_port)
        self._configure_entry(port_entry)
        self._field(left, 2, 0, "UDP port (WLED default: 21324)", port_entry)

        self._button(
            left,
            "Test Connection",
            self._test_connection_clicked,
            bg=self._t["input"],
            hover=self._t["secondary_hover"],
            fg=self._t["text"],
        ).grid(row=5, column=1, sticky="ew", pady=(0, 8), padx=(0, 10))

        right = tk.Frame(engine, bg=self._t["panel_2"], highlightbackground=self._t["border"], highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            right,
            text="BRIDGE EXECUTION",
            bg=self._t["panel_2"],
            fg=self._t["text"],
            font=self._font_card_title,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(
            right,
            text="Start the MIDI bridge to translate incoming Note and CC messages into WLED UDP frames.",
            bg=self._t["panel_2"],
            fg=self._t["text_dim"],
            font=self._font_small,
            justify="left",
            wraplength=340,
        ).pack(fill="x", padx=16, pady=(0, 10))
        self._start_btn = self._button(
            right,
            "START BRIDGE",
            self._start_clicked,
            bg=self._t["cyan"],
            hover=self._t["cyan_hover"],
            fg="#061019",
            font=self._font_big,
            pady=9,
        )
        self._start_btn.pack(fill="x", padx=16, pady=(0, 8))
        self._stop_btn = self._button(
            right,
            "STOP BRIDGE",
            self._stop_clicked,
            bg=self._t["red"],
            hover=self._t["red_hover"],
            fg="#ffffff",
            font=self._font_big,
            pady=9,
            state="disabled",
        )
        self._stop_btn.pack(fill="x", padx=16, pady=(0, 8))
        actions = tk.Frame(right, bg=self._t["panel_2"])
        actions.pack(fill="x", padx=16, pady=(0, 12))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        self._button(actions, "Save Config", self._save_clicked).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._button(actions, "Reload Ports", self._reload_ports).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _build_mapping(self, parent: tk.Frame) -> None:
        mapping = self._panel(parent, "LED / MIDI Mapping", "Configure how MIDI notes translate to LED pixels.")
        mapping.master.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        mapping.columnconfigure(0, weight=1)
        mapping.columnconfigure(1, weight=1)

        self._led_count = tk.StringVar()
        led_spin = tk.Spinbox(mapping, from_=1, to=9999, textvariable=self._led_count, wrap=True)
        self._configure_entry(led_spin)
        self._field(mapping, 0, 0, "Total LED count", led_spin)

        self._base_note = tk.StringVar()
        base_spin = tk.Spinbox(mapping, from_=0, to=127, textvariable=self._base_note, wrap=True)
        self._configure_entry(base_spin)
        self._field(mapping, 0, 1, "Start note (base)", base_spin)

        self._midi_channel = tk.StringVar()
        channel_combo = ttk.Combobox(
            mapping,
            textvariable=self._midi_channel,
            values=("All",) + tuple(str(i) for i in range(1, 17)),
            state="readonly",
            style="Bridge.TCombobox",
        )
        self._field(mapping, 1, 0, "Listen channel", channel_combo)

        self._channel_bank_size = tk.StringVar()
        bank_spin = tk.Spinbox(mapping, from_=1, to=9999, textvariable=self._channel_bank_size, wrap=True)
        self._configure_entry(bank_spin)
        self._field(mapping, 1, 1, "LEDs per channel", bank_spin)

        tk.Label(
            mapping,
            text="MAPPING PREVIEW",
            bg=self._t["panel"],
            fg=self._t["text_dim"],
            font=self._font_label,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(3, 4))
        self._led_canvas = tk.Canvas(mapping, height=48, bg=self._t["input"], highlightthickness=1, highlightbackground=self._t["border"])
        self._led_canvas.grid(row=5, column=0, columnspan=2, sticky="ew")
        self._led_canvas.bind("<Configure>", lambda _: self._draw_led_preview())

    def _build_color(self, parent: tk.Frame) -> None:
        color = self._panel(parent, "Color Engine", "Configure output color modes and palettes.")
        color.master.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))
        color.columnconfigure(0, weight=1)

        self._color_mode = tk.StringVar()
        color_combo = ttk.Combobox(color, textvariable=self._color_mode, values=COLOR_MODES, state="readonly", style="Bridge.TCombobox")
        self._field(color, 0, 0, "Mapping mode", color_combo)

        palette_box = tk.Frame(color, bg=self._t["panel_2"], highlightbackground=self._t["border"], highlightthickness=1)
        palette_box.grid(row=2, column=0, sticky="ew", pady=(2, 8))
        palette_box.columnconfigure(1, weight=1)
        tk.Label(palette_box, text="Palette Selection", bg=self._t["panel_2"], fg=self._t["text"], font=self._font_label).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 6)
        )
        self._color_preview = tk.Canvas(palette_box, width=34, height=34, bg=self._t["panel_2"], highlightthickness=0)
        self._color_preview.grid(row=1, column=0, padx=(10, 10), pady=(0, 8))
        rgb_frame = tk.Frame(palette_box, bg=self._t["panel_2"])
        rgb_frame.grid(row=1, column=1, sticky="ew", pady=(0, 8))
        for idx, (label, var) in enumerate((("R", self._rgb_r), ("G", self._rgb_g), ("B", self._rgb_b))):
            tk.Label(rgb_frame, text=label, bg=self._t["panel_2"], fg=self._t["text_muted"], font=self._font_small).grid(
                row=0, column=idx * 2, sticky="w", padx=(0, 4)
            )
            spin = tk.Spinbox(rgb_frame, from_=0, to=255, textvariable=var, width=5, wrap=True)
            self._configure_entry(spin)
            spin.grid(row=0, column=idx * 2 + 1, padx=(0, 8))

        self._palette = tk.StringVar()
        palette_entry = tk.Entry(color, textvariable=self._palette)
        self._configure_entry(palette_entry)
        self._field(color, 2, 0, "Velocity palette file", palette_entry)
        self._button(color, "Browse Palette File", self._browse_palette, pady=5).grid(row=5, column=0, sticky="ew", padx=(0, 10))

    def _build_runtime(self, parent: tk.Frame) -> None:
        runtime = self._panel(parent, "Runtime Tuning", "Tune bridge responsiveness and processing batch size.")
        runtime.master.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for column in range(5):
            runtime.columnconfigure(column, weight=1)

        self._frame_ms = tk.StringVar()
        frame_spin = tk.Spinbox(runtime, from_=0, to=500, textvariable=self._frame_ms, wrap=True)
        self._configure_entry(frame_spin)
        self._field(runtime, 0, 0, "Frame interval (ms)", frame_spin)

        self._burst = tk.StringVar()
        burst_spin = tk.Spinbox(runtime, from_=1, to=512, textvariable=self._burst, wrap=True)
        self._configure_entry(burst_spin)
        self._field(runtime, 0, 1, "MIDI read burst", burst_spin)

        self._verbose = tk.BooleanVar()
        verbose_check = tk.Checkbutton(
            runtime,
            text="Verbose output in log",
            variable=self._verbose,
            bg=self._t["panel"],
            fg=self._t["text"],
            selectcolor=self._t["input"],
            activebackground=self._t["panel"],
            activeforeground=self._t["text"],
            font=self._font_ui,
            highlightthickness=0,
        )
        verbose_check.grid(row=1, column=2, sticky="w", pady=(0, 8), padx=(0, 10))

        self._telemetry_box(runtime, 3, "FRAMES / SEC", self._telemetry_vars["fps"])
        self._telemetry_box(runtime, 4, "MIDI MSG / SEC", self._telemetry_vars["midi"])
        self._telemetry_box(runtime, 5, "UDP PKT / SEC", self._telemetry_vars["udp"])
        self._telemetry_box(runtime, 6, "LAST FRAME", self._telemetry_vars["last_frame"])

    def _telemetry_box(self, parent: tk.Frame, column: int, label: str, value: tk.StringVar) -> None:
        parent.columnconfigure(column, weight=1)
        box = tk.Frame(parent, bg=self._t["panel_2"], highlightbackground=self._t["border"], highlightthickness=1)
        box.grid(row=1, column=column, sticky="ew", padx=(0, 8), pady=(0, 8))
        tk.Label(box, text=label, bg=self._t["panel_2"], fg=self._t["text_dim"], font=self._font_label).pack(
            anchor="w", padx=8, pady=(6, 0)
        )
        tk.Label(box, textvariable=value, bg=self._t["panel_2"], fg=self._t["cyan"], font=self._font_big).pack(
            anchor="w", padx=8, pady=(1, 6)
        )

    def _build_log(self, parent: tk.Frame) -> None:
        self._log_outer = tk.Frame(parent, bg=self._t["panel"], highlightbackground=self._t["border"], highlightthickness=1)
        self._log_outer.grid(row=3, column=0, columnspan=2, sticky="ew")
        self._main = parent
        parent.rowconfigure(3, weight=0)

        header = tk.Frame(self._log_outer, bg=self._t["panel"])
        header.pack(fill="x", padx=10, pady=6)
        self._log_toggle_btn = self._button(header, "v", self._toggle_log, bg=self._t["panel"], hover=self._t["secondary_hover"], padx=8, pady=2)
        self._log_toggle_btn.pack(side="left")
        tk.Label(header, text="BRIDGE LOG", bg=self._t["panel"], fg=self._t["text"], font=self._font_card_title).pack(side="left", padx=(8, 14))
        tk.Label(header, textvariable=self._last_log_line, bg=self._t["panel"], fg=self._t["text_muted"], font=self._font_small).pack(
            side="left", fill="x", expand=True
        )
        self._clear_log_btn = self._button(header, "Clear Log", self._clear_log, padx=10, pady=3)
        self._clear_log_btn.pack(side="right")
        self._button(header, "Pop Out", self._open_log_popout, padx=10, pady=3).pack(side="right", padx=(0, 8))

        self._log_body = tk.Frame(self._log_outer, bg=self._t["panel"])
        self._log = tk.Text(
            self._log_body,
            height=10,
            wrap="word",
            font=self._font_mono,
            bg=self._t["log_bg"],
            fg=self._t["text_dim"],
            insertbackground=self._t["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self._t["border"],
            borderwidth=0,
        )
        scroll = ttk.Scrollbar(self._log_body, command=self._log.yview, style="Bridge.Vertical.TScrollbar")
        self._log.configure(yscrollcommand=scroll.set)
        self._log.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=(0, 14))
        scroll.pack(side="right", fill="y", padx=(0, 14), pady=(0, 14))
        self._set_log_expanded(False)

        self._append_log_line(f"Project root: {REPO_ROOT}")
        self._append_log_line("Settings are saved to config.json.")

    def _set_status_ready(self) -> None:
        self._status_label.configure(text="Ready", fg=self._t["green"], bg=self._t["green_dark"])
        self._status_pill.configure(bg=self._t["green_dark"])
        self._status_dot.configure(bg=self._t["green_dark"])
        self._draw_status_dot(self._t["green"])

    def _set_status_busy(self) -> None:
        self._status_label.configure(text="Running", fg=self._t["cyan"], bg=self._t["cyan_dark"])
        self._status_pill.configure(bg=self._t["cyan_dark"])
        self._status_dot.configure(bg=self._t["cyan_dark"])
        self._draw_status_dot(self._t["cyan"])

    def _draw_status_dot(self, color: str) -> None:
        self._status_dot.delete("all")
        self._status_dot.create_oval(3, 3, 9, 9, fill=color, outline=color)

    def _refresh_visuals(self) -> None:
        self._update_color_preview()
        self._draw_led_preview()

    def _update_color_preview(self) -> None:
        try:
            r, g, b = int(self._rgb_r.get()), int(self._rgb_g.get()), int(self._rgb_b.get())
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            color = f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, tk.TclError):
            color = "#0078ff"
        self._color_preview.delete("all")
        self._color_preview.create_rectangle(3, 3, 39, 39, fill=color, outline=self._t["cyan"], width=1)

    def _draw_led_preview(self) -> None:
        if not hasattr(self, "_led_canvas"):
            return
        canvas = self._led_canvas
        canvas.delete("all")
        width = max(260, canvas.winfo_width())
        y = 24
        left = 18
        right = width - 18
        try:
            count = max(1, int(self._led_count.get()))
        except ValueError:
            count = 64
        try:
            bank_size = int(self._channel_bank_size.get() or "0")
        except ValueError:
            bank_size = 0
        canvas.create_text(left, 11, text="LED 0", fill=self._t["text_dim"], anchor="w", font=self._font_small)
        canvas.create_text((left + right) // 2, 11, text=f"PREVIEW ({count} LEDS)", fill=self._t["text_dim"], font=self._font_label)
        canvas.create_text(right, 11, text=f"LED {count - 1}", fill=self._t["text_dim"], anchor="e", font=self._font_small)
        canvas.create_line(left, y, right, y, fill=self._t["border"], width=8)
        ticks = min(count, 96)
        for index in range(ticks):
            x = left + (right - left) * index / max(1, ticks - 1)
            led_index = round(index * (count - 1) / max(1, ticks - 1))
            is_bank_start = bank_size > 0 and led_index % bank_size == 0
            color = self._t["cyan"] if index == 0 or is_bank_start else "#2c64ff" if index % 8 == 0 else "#243140"
            canvas.create_line(x, y - 4, x, y + 4, fill=color, width=2 if index == 0 else 1)
        canvas.create_oval(left - 5, y - 5, left + 5, y + 5, fill=self._t["cyan"], outline="")
        canvas.create_text(left, 40, text=f"Note {self._base_note.get()} -> LED 0", fill=self._t["text_muted"], anchor="w", font=self._font_small)
        mapping_label = f"Channel banks: {bank_size} LEDs/channel" if bank_size > 0 else "Linear mapping"
        canvas.create_text(right, 40, text=mapping_label, fill=self._t["text_muted"], anchor="e", font=self._font_small)

    def _clear_log(self) -> None:
        self._log.delete("1.0", "end")
        self._visible_log_lines = 0
        if self._popout_log is not None:
            self._popout_log.delete("1.0", "end")
        self._last_log_line.set("Log cleared.")

    def _open_log_popout(self) -> None:
        if self._popout_window is not None and self._popout_window.winfo_exists():
            self._popout_window.lift()
            self._popout_window.focus_force()
            return

        window = tk.Toplevel(self.root)
        window.title("Bridge Log")
        window.geometry("820x420")
        window.minsize(560, 260)
        window.configure(bg=self._t["bg"])
        window.columnconfigure(0, weight=1)
        window.rowconfigure(1, weight=1)

        header = tk.Frame(window, bg=self._t["panel"], highlightbackground=self._t["border"], highlightthickness=1)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="BRIDGE LOG", bg=self._t["panel"], fg=self._t["text"], font=self._font_card_title).pack(
            side="left", padx=14, pady=10
        )
        self._button(header, "Clear Log", self._clear_log, padx=10, pady=4).pack(side="right", padx=14, pady=8)

        body = tk.Frame(window, bg=self._t["panel"], padx=12, pady=12)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        text = tk.Text(
            body,
            wrap="word",
            font=self._font_mono,
            bg=self._t["log_bg"],
            fg=self._t["text_dim"],
            insertbackground=self._t["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self._t["border"],
            borderwidth=0,
        )
        scroll = ttk.Scrollbar(body, command=text.yview, style="Bridge.Vertical.TScrollbar")
        text.configure(yscrollcommand=scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        existing = self._log.get("1.0", "end-1c")
        if existing:
            text.insert("end", existing + "\n")
            text.see("end")

        def on_close() -> None:
            self._popout_log = None
            self._popout_window = None
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)
        self._popout_window = window
        self._popout_log = text

    def _toggle_log(self) -> None:
        self._set_log_expanded(not self._log_expanded)

    def _set_log_expanded(self, expanded: bool) -> None:
        self._log_expanded = expanded
        if expanded:
            self._log_outer.grid_configure(sticky="nsew")
            if hasattr(self, "_main"):
                self._main.rowconfigure(3, weight=1)
            self._log_body.pack(fill="both", expand=True)
            self._log_toggle_btn.configure(text="^")
            self._clear_log_btn.configure(state="normal")
        else:
            self._log_body.pack_forget()
            self._log_outer.grid_configure(sticky="ew")
            if hasattr(self, "_main"):
                self._main.rowconfigure(3, weight=0)
            self._log_toggle_btn.configure(text="v")
            self._clear_log_btn.configure(state="disabled")

    def _refresh_ports(self) -> tuple[str, ...]:
        try:
            return tuple(get_input_port_names())
        except Exception as exc:
            messagebox.showerror("MIDI", f"Could not load MIDI ports: {exc}")
            return ()

    def _reload_ports(self) -> None:
        names = self._refresh_ports()
        self._midi_combo.configure(values=names)
        if names and not self._midi_combo.get().strip():
            self._midi_combo.set(names[0])
        self._append_log_line(f"MIDI ports updated: {len(names)} found.")

    def _browse_palette(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Palette file",
            initialdir=REPO_ROOT,
            filetypes=[("Palette / Text", "*.txt"), ("All files", "*.*")],
        )
        if path:
            try:
                self._palette.set(os.path.relpath(path, REPO_ROOT))
            except ValueError:
                self._palette.set(path)

    def _fixed_color_string(self) -> str:
        try:
            r, g, b = int(self._rgb_r.get()), int(self._rgb_g.get()), int(self._rgb_b.get())
            return f"{max(0, min(255, r))},{max(0, min(255, g))},{max(0, min(255, b))}"
        except (ValueError, tk.TclError):
            return "0,120,255"

    def _collect_settings_from_form(self) -> dict[str, object]:
        return {
            "wled_ip": self._wled_ip.get(),
            "wled_port": int(self._wled_port.get().strip()),
            "midi_port": self._midi_combo.get().strip(),
            "led_count": int(self._led_count.get().strip()),
            "base_note": int(self._base_note.get().strip()),
            "midi_channel": self._midi_channel.get().strip() or "All",
            "channel_bank_size": self._channel_bank_size.get().strip(),
            "frame_interval_ms": int(self._frame_ms.get().strip()),
            "midi_read_burst": int(self._burst.get().strip()),
            "color_mode": self._color_mode.get(),
            "fixed_color": self._fixed_color_string(),
            "velocity_palette_file": self._palette.get().strip(),
            "verbose": bool(self._verbose.get()),
        }

    def _validate_settings(self, settings: dict[str, object]) -> str | None:
        try:
            if not str(settings["wled_ip"]).strip():
                return "WLED IP cannot be empty."
            if not str(settings["midi_port"]).strip():
                return "MIDI port cannot be empty."
            if int(settings["wled_port"]) <= 0:
                return "WLED UDP port must be greater than 0."
            if int(settings["led_count"]) <= 0:
                return "LED count must be greater than 0."
            midi_channel = str(settings["midi_channel"]).strip()
            if midi_channel.lower() != "all" and not 1 <= int(midi_channel) <= 16:
                return "MIDI channel must be All or 1..16."
            channel_bank_size = str(settings["channel_bank_size"]).strip()
            if channel_bank_size and int(channel_bank_size) <= 0:
                return "LEDs per channel must be greater than 0."
            if int(settings["frame_interval_ms"]) < 0:
                return "Frame interval cannot be negative."
            if int(settings["midi_read_burst"]) <= 0:
                return "MIDI read burst must be greater than 0."
        except ValueError:
            return "Please fill in numeric fields correctly."
        return None

    def _load_into_form(self) -> None:
        settings = load_settings()
        self._wled_ip.set(str(settings["wled_ip"]))
        self._wled_port.set(str(settings["wled_port"]))
        self._midi_combo.set(str(settings["midi_port"]))
        self._led_count.set(str(settings["led_count"]))
        self._base_note.set(str(settings["base_note"]))
        self._midi_channel.set(str(settings.get("midi_channel", "All") or "All"))
        self._channel_bank_size.set(str(settings.get("channel_bank_size", "")))
        self._frame_ms.set(str(settings["frame_interval_ms"]))
        self._burst.set(str(settings["midi_read_burst"]))
        self._color_mode.set(str(settings["color_mode"]))
        r, g, b = _parse_rgb_triple(str(settings["fixed_color"]))
        self._rgb_r.set(str(r))
        self._rgb_g.set(str(g))
        self._rgb_b.set(str(b))
        self._palette.set(str(settings.get("velocity_palette_file", "")))
        self._verbose.set(bool(settings.get("verbose")))
        self._reload_ports()
        self._refresh_visuals()

    def _save_clicked(self) -> None:
        settings = self._collect_settings_from_form()
        message = self._validate_settings(settings)
        if message:
            messagebox.showwarning("Validation", message)
            return
        save_settings(settings)
        self._append_log_line(f"Settings saved: {config_path()}")

    def _test_connection_clicked(self) -> None:
        try:
            settings = self._collect_settings_from_form()
            message = self._validate_settings(settings)
            if message:
                messagebox.showwarning("Validation", message)
                return
            r, g, b = _parse_rgb_triple(str(settings["fixed_color"]))
            count = int(settings["led_count"])
            payload = bytes([2, 2]) + bytes([r, g, b]) * count
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(payload, (str(settings["wled_ip"]).strip(), int(settings["wled_port"])))
            self._append_log_line(f"[{time.strftime('%H:%M:%S')}] Sent test packet to {settings['wled_ip']}:{settings['wled_port']}")
        except OSError as exc:
            messagebox.showerror("Test failed", str(exc))

    def _append_log_line(self, line: str) -> None:
        if self._handle_bridge_output(line):
            return
        self._last_log_line.set(self._preview_log_line(line))
        self._log.insert("end", line + "\n")
        self._visible_log_lines += 1
        self._trim_embedded_log()
        self._log.see("end")
        if self._popout_log is not None:
            self._popout_log.insert("end", line + "\n")
            self._popout_log.see("end")

    def _trim_embedded_log(self) -> None:
        extra = self._visible_log_lines - LOG_VISIBLE_MAX_LINES
        if extra <= 0:
            return
        self._log.delete("1.0", f"{extra + 1}.0")
        self._visible_log_lines -= extra

    def _handle_bridge_output(self, line: str) -> bool:
        if not line.startswith("TELEMETRY "):
            return False
        values: dict[str, str] = {}
        for part in line.split()[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            values[key] = value
        if "fps" in values:
            self._telemetry_vars["fps"].set(values["fps"])
        if "midi_per_s" in values:
            self._telemetry_vars["midi"].set(values["midi_per_s"])
        if "udp_per_s" in values:
            self._telemetry_vars["udp"].set(values["udp_per_s"])
        if "last_frame_ms" in values:
            self._telemetry_vars["last_frame"].set(f"{values['last_frame_ms']}ms")
        return True

    def _preview_log_line(self, line: str) -> str:
        if line.startswith("$ "):
            return "Bridge start command sent. Open or pop out the log to view the full command."
        if len(line) <= LOG_PREVIEW_MAX_CHARS:
            return line
        return line[: LOG_PREVIEW_MAX_CHARS - 3].rstrip() + "..."

    def _poll_log_queue(self) -> None:
        processed = 0
        try:
            while processed < LOG_QUEUE_LINES_PER_TICK:
                self._append_log_line(self._log_queue.get_nowait())
                processed += 1
        except queue.Empty:
            pass
        if self._dropped_log_lines:
            dropped = self._dropped_log_lines
            self._dropped_log_lines = 0
            self._append_log_line(f"[log throttled] Dropped {dropped} lines to keep the GUI responsive.")
        delay = 20 if processed == LOG_QUEUE_LINES_PER_TICK else 120
        self.root.after(delay, self._poll_log_queue)

    def _start_clicked(self) -> None:
        if self._proc is not None:
            messagebox.showinfo("Running", "The bridge process is already running.")
            return
        settings = self._collect_settings_from_form()
        message = self._validate_settings(settings)
        if message:
            messagebox.showwarning("Validation", message)
            return

        argv = build_subprocess_argv(settings)
        self._append_log_line("$ " + " ".join(argv))
        creationflags = 0
        if sys.platform.startswith("win"):
            creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

        try:
            save_settings(settings)
            self._proc = subprocess.Popen(
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
        except OSError as exc:
            self._proc = None
            messagebox.showerror("Start failed", str(exc))
            return

        self._stop_reader.clear()

        def reader() -> None:
            assert self._proc is not None and self._proc.stdout is not None
            for chunk in iter(self._proc.stdout.readline, ""):
                if self._stop_reader.is_set():
                    break
                if chunk.strip():
                    if self._log_queue.qsize() < LOG_QUEUE_MAX_LINES:
                        self._log_queue.put(chunk.rstrip())
                    else:
                        self._dropped_log_lines += 1
            self._proc.stdout.close()

        self._reader_thread = threading.Thread(target=reader, daemon=True)
        self._reader_thread.start()
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._set_status_busy()

        def watch_exit() -> None:
            if self._proc is None:
                return
            code = self._proc.poll()
            if code is None:
                self.root.after(500, watch_exit)
            else:
                self._append_log_line(f"<< Process ended (Exit {code}) >>")
                self._proc = None
                self._start_btn.configure(state="normal")
                self._stop_btn.configure(state="disabled")
                self._set_status_ready()

        watch_exit()

    def _stop_clicked(self) -> None:
        if self._proc is None:
            return
        self._stop_reader.set()
        try:
            self._proc.terminate()
        except OSError:
            pass
        self._append_log_line("Stop requested.")

    def _on_close(self) -> None:
        if self._proc is not None:
            try:
                self._proc.terminate()
            except OSError:
                pass
            self._stop_reader.set()
        self.root.destroy()

    def mainloop(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = BridgeGuiApp()
    app.mainloop()


if __name__ == "__main__":
    main()
