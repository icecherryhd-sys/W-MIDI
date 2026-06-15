"""Prepare the W-MIDI ESP32-S3 firmware for the browser flasher."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

FIRMWARE_NAME = "w-midi-usb-esp32s3-merged.bin"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WEB_ROOT = PROJECT_ROOT / "web-flasher"


def build_manifest(version: str = "0.1.0", firmware_name: str = FIRMWARE_NAME) -> dict:
    return {
        "name": "W-MIDI USB Underlight",
        "version": version,
        "new_install_prompt_erase": True,
        "new_install_improv_wait_time": 0,
        "builds": [
            {
                "chipFamily": "ESP32-S3",
                "parts": [
                    {
                        "path": f"firmware/{firmware_name}",
                        "offset": 0,
                    }
                ],
            }
        ],
    }


def prepare_web_flasher(source: Path, web_root: Path = DEFAULT_WEB_ROOT, version: str = "0.1.0") -> Path:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Firmware binary not found: {source}")
    if source.stat().st_size == 0:
        raise ValueError(f"Firmware binary is empty: {source}")

    firmware_dir = web_root / "firmware"
    firmware_dir.mkdir(parents=True, exist_ok=True)
    target = firmware_dir / FIRMWARE_NAME
    shutil.copy2(source, target)

    manifest_path = web_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest(version=version), indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy a merged ESP32-S3 W-MIDI firmware into web-flasher/.")
    parser.add_argument("--source", required=True, type=Path, help="Path to the merged ESP32-S3 firmware .bin")
    parser.add_argument("--web-root", type=Path, default=DEFAULT_WEB_ROOT, help="Path to the web-flasher directory")
    parser.add_argument("--version", default="0.1.0", help="Firmware version to write into manifest.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = prepare_web_flasher(args.source, args.web_root, args.version)
    print(f"Prepared web flasher firmware: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
