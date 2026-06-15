"""Build W-MIDI WLED firmware and prepare the browser flasher binary."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tools.firmware.prepare_web_flasher import prepare_web_flasher

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WLED_ROOT = PROJECT_ROOT / "firmware" / "WLED-main" / "WLED-main"
DEFAULT_ENV = "w_midi_esp32s3_usb"


def find_platformio_command() -> list[str]:
    if shutil.which("pio"):
        return ["pio"]
    if shutil.which("platformio"):
        return ["platformio"]
    return [sys.executable, "-m", "platformio"]


def run_platformio_build(wled_root: Path, env_name: str) -> None:
    cmd = find_platformio_command() + ["run", "-e", env_name]
    subprocess.run(cmd, cwd=wled_root, check=True)


def _candidate_esptool_commands() -> list[list[str]]:
    commands: list[list[str]] = []
    if shutil.which("esptool"):
        commands.append(["esptool"])
    commands.append([sys.executable, "-m", "esptool"])

    user_profile = Path(os.environ.get("USERPROFILE", ""))
    if user_profile:
        pio_python = user_profile / ".platformio" / "penv" / "Scripts" / "python.exe"
        if pio_python.exists():
            commands.append([str(pio_python), "-m", "esptool"])
        esptool_py = user_profile / ".platformio" / "packages" / "tool-esptoolpy" / "esptool.py"
        if esptool_py.exists():
            commands.append([sys.executable, str(esptool_py)])
    return commands


def find_file(name: str, roots: list[Path]) -> Path:
    for root in roots:
        candidate = root / name
        if candidate.is_file():
            return candidate
    for root in roots:
        if root.exists():
            matches = list(root.rglob(name))
            if matches:
                return matches[0]
    raise FileNotFoundError(f"Could not find {name} in: {', '.join(str(root) for root in roots)}")


def merge_firmware(wled_root: Path, env_name: str, output: Path) -> Path:
    build_dir = wled_root / ".pio" / "build" / env_name
    search_roots = [
        build_dir,
        wled_root,
        Path(os.environ.get("USERPROFILE", "")) / ".platformio" / "packages",
    ]

    bootloader = find_file("bootloader.bin", search_roots)
    partitions = find_file("partitions.bin", search_roots)
    boot_app0 = find_file("boot_app0.bin", search_roots)
    app = find_file("firmware.bin", [build_dir])

    output.parent.mkdir(parents=True, exist_ok=True)
    merge_args = [
        "--chip",
        "esp32s3",
        "merge_bin",
        "-o",
        str(output),
        "--flash_mode",
        "dio",
        "--flash_freq",
        "80m",
        "--flash_size",
        "4MB",
        "0x0000",
        str(bootloader),
        "0x8000",
        str(partitions),
        "0xe000",
        str(boot_app0),
        "0x10000",
        str(app),
    ]

    last_error: subprocess.CalledProcessError | FileNotFoundError | None = None
    for command in _candidate_esptool_commands():
        try:
            subprocess.run(command + merge_args, cwd=wled_root, check=True)
            return output
        except (subprocess.CalledProcessError, FileNotFoundError) as error:
            last_error = error
    raise RuntimeError("Could not run esptool to merge the ESP32-S3 firmware") from last_error


def build_and_prepare(wled_root: Path, env_name: str, version: str) -> Path:
    run_platformio_build(wled_root, env_name)
    merged = wled_root / ".pio" / "build" / env_name / "w-midi-usb-esp32s3-merged.bin"
    merge_firmware(wled_root, env_name, merged)
    return prepare_web_flasher(merged, PROJECT_ROOT / "web-flasher", version=version)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build W-MIDI WLED and prepare web-flasher firmware.")
    parser.add_argument("--wled-root", type=Path, default=DEFAULT_WLED_ROOT, help="Path to the WLED source root")
    parser.add_argument("--env", default=DEFAULT_ENV, help="PlatformIO environment to build")
    parser.add_argument("--version", default="0.1.0", help="Firmware version written into web-flasher/manifest.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = build_and_prepare(args.wled_root.resolve(), args.env, args.version)
    print(f"Web flasher firmware ready: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
