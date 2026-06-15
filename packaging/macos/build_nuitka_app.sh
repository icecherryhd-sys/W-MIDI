#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.2.0}"
ARCH="${2:-$(uname -m)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RELEASE_ROOT="$REPO_ROOT/release"
PACKAGE_NAME="W-MIDI-v${VERSION}-macOS-${ARCH}"
PACKAGE_ROOT="$RELEASE_ROOT/$PACKAGE_NAME"
NUITKA_ROOT="$RELEASE_ROOT/.nuitka-build-macos-${ARCH}"
NUITKA_CACHE_ROOT="$RELEASE_ROOT/.nuitka-cache"
ENTRY_POINT="$REPO_ROOT/midi_wled_bridge/frozen_entry.py"
ICON="$REPO_ROOT/assets/windows/w-midi-source.png"

remove_release_child() {
  local target="$1"
  if [[ ! -e "$target" ]]; then
    return
  fi
  local resolved
  resolved="$(cd "$(dirname "$target")" && pwd)/$(basename "$target")"
  case "$resolved" in
    "$RELEASE_ROOT"/*) rm -rf "$resolved" ;;
    *) echo "Refusing to remove a path outside release: $resolved" >&2; exit 1 ;;
  esac
}

remove_release_child "$PACKAGE_ROOT"
remove_release_child "$NUITKA_ROOT"

mkdir -p "$PACKAGE_ROOT" "$NUITKA_CACHE_ROOT"
export NUITKA_CACHE_DIR="$NUITKA_CACHE_ROOT"

"$PYTHON_BIN" -m nuitka \
  --standalone \
  --assume-yes-for-downloads \
  --enable-plugin=pyside6 \
  --macos-create-app-bundle \
  --macos-app-name=W-MIDI \
  --macos-app-icon="$ICON" \
  --include-module=rtmidi \
  --include-module=mido.backends.rtmidi \
  --include-package=serial \
  --output-filename=W-MIDI \
  --output-dir="$NUITKA_ROOT" \
  "$ENTRY_POINT"

APP_BUNDLE="$(find "$NUITKA_ROOT" -maxdepth 2 -type d -name "*.app" | head -n 1)"
if [[ -z "$APP_BUNDLE" ]]; then
  echo "Nuitka did not create a macOS .app bundle in $NUITKA_ROOT." >&2
  exit 1
fi

cp -R "$APP_BUNDLE" "$PACKAGE_ROOT/W-MIDI.app"
if [[ ! -x "$PACKAGE_ROOT/W-MIDI.app/Contents/MacOS/W-MIDI" ]]; then
  echo "Required app executable is missing: $PACKAGE_ROOT/W-MIDI.app/Contents/MacOS/W-MIDI" >&2
  exit 1
fi

VISIBLE_PATHS=(
  "W-MIDI Tutorial Guide.pdf"
  "README.md"
  "README_EN.txt"
  "README.txt"
  "LICENSE.txt"
  "CHANGELOG.md"
  "config.example.json"
  "assets"
  "layouts"
  "palettes"
)

for relative_path in "${VISIBLE_PATHS[@]}"; do
  source_path="$REPO_ROOT/$relative_path"
  if [[ ! -e "$source_path" ]]; then
    echo "Required release file is missing: $relative_path" >&2
    exit 1
  fi
  cp -R "$source_path" "$PACKAGE_ROOT/"
done

remove_release_child "$NUITKA_ROOT"

echo "Created unsigned macOS app folder $PACKAGE_ROOT"
