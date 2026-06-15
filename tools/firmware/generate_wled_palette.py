"""Generate the W-MIDI WLED palette header from the desktop palette file."""

from __future__ import annotations

import argparse
from pathlib import Path

from midi_wled_bridge.palette import load_velocity_palette_file, scale_palette_to_full


def load_scaled_palette(path: Path) -> dict[int, tuple[int, int, int]]:
    return scale_palette_to_full(load_velocity_palette_file(str(path)))


def render_palette_header(palette: dict[int, tuple[int, int, int]]) -> str:
    rows: list[str] = []
    for velocity in range(128):
        red, green, blue = palette.get(velocity, (0, 0, 0))
        rows.append(f"  {{{red}, {green}, {blue}}},")
    return (
        "#pragma once\n"
        "\n"
        "#include <stdint.h>\n"
        "\n"
        "constexpr uint8_t W_MIDI_PALETTE[128][3] = {\n"
        + "\n".join(rows)
        + "\n};\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate W-MIDI WLED palette header.")
    parser.add_argument("--palette", default="palettes/Default", type=Path)
    parser.add_argument(
        "--output",
        default=Path("firmware/wled-w-midi/usermods/W_MIDI_USB/w_midi_palette.h"),
        type=Path,
    )
    args = parser.parse_args(argv)

    palette = load_scaled_palette(args.palette)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_palette_header(palette), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
