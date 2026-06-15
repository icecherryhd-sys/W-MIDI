#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.2.0}"
ARCH="${2:-$(uname -m)}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RELEASE_ROOT="$REPO_ROOT/release"
PACKAGE_NAME="W-MIDI-v${VERSION}-macOS-${ARCH}"
PACKAGE_ROOT="$RELEASE_ROOT/$PACKAGE_NAME"
ARCHIVE_PATH="$RELEASE_ROOT/$PACKAGE_NAME.zip"

bash "$SCRIPT_DIR/build_nuitka_app.sh" "$VERSION" "$ARCH"

if [[ ! -d "$PACKAGE_ROOT/W-MIDI.app" ]]; then
  echo "Required app bundle is missing: $PACKAGE_ROOT/W-MIDI.app" >&2
  exit 1
fi

rm -f "$ARCHIVE_PATH"
(
  cd "$RELEASE_ROOT"
  ditto -c -k --sequesterRsrc --keepParent "$PACKAGE_NAME" "$ARCHIVE_PATH"
)

echo "Created $ARCHIVE_PATH"
