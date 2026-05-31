"""Entry point for the portable Windows executable."""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--bridge-cli":
        from midi_wled_bridge.cli import main as cli_main

        return cli_main(sys.argv[2:])

    from midi_wled_bridge.qt_gui import main as gui_main

    gui_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
