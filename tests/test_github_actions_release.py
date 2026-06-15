import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-release.yml"


class GitHubActionsReleaseTests(unittest.TestCase):
    def test_windows_release_workflow_builds_nuitka_zip(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Build W-MIDI Release", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("tags:", text)
        self.assertIn("'v*'", text)
        self.assertIn("runs-on: windows-2022", text)
        self.assertIn("actions/checkout@v4", text)
        self.assertIn("actions/setup-python@v5", text)
        self.assertIn("python-version: '3.12'", text)
        self.assertIn("pip install -r requirements.txt nuitka ordered-set zstandard", text)
        self.assertIn("python -m unittest discover -s tests", text)
        self.assertIn("python -m compileall -q midi_wled_bridge tests", text)
        self.assertIn("packaging/windows/build_release_archive.ps1", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertIn("release/W-MIDI-v${{ steps.version.outputs.version }}.zip", text)

    def test_tagged_release_uploads_github_release_asset(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("permissions:", text)
        self.assertIn("contents: write", text)
        self.assertIn("if: startsWith(github.ref, 'refs/tags/v')", text)
        self.assertIn("gh release upload", text)
        self.assertIn("--clobber", text)

    def test_macos_release_workflow_builds_unsigned_app_artifacts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("macos:", text)
        self.assertIn("name: macOS Nuitka", text)
        self.assertIn("runs-on: ${{ matrix.runner }}", text)
        self.assertIn("macos-latest", text)
        self.assertIn("macos-15-intel", text)
        self.assertIn("arch: arm64", text)
        self.assertIn("arch: x64", text)
        self.assertIn("bash packaging/macos/build_release_archive.sh", text)
        self.assertIn("release/W-MIDI-v${{ steps.version.outputs.version }}-macOS-${{ matrix.arch }}.zip", text)
        self.assertIn("W-MIDI-v${{ steps.version.outputs.version }}-macOS-${{ matrix.arch }}", text)

    def test_macos_unsigned_release_script_exists_and_uses_app_bundle(self) -> None:
        script = ROOT / "packaging" / "macos" / "build_nuitka_app.sh"
        archive = ROOT / "packaging" / "macos" / "build_release_archive.sh"

        self.assertTrue(script.is_file())
        self.assertTrue(archive.is_file())

        text = script.read_text(encoding="utf-8")
        archive_text = archive.read_text(encoding="utf-8")

        self.assertIn("--macos-create-app-bundle", text)
        self.assertIn("--macos-app-name=W-MIDI", text)
        self.assertIn("--macos-app-icon=", text)
        self.assertIn("--enable-plugin=pyside6", text)
        self.assertIn("--include-package=serial", text)
        self.assertIn("W-MIDI.app", text)
        self.assertIn("palettes", text)
        self.assertIn("layouts", text)
        self.assertIn("assets", text)
        self.assertIn("ditto -c -k --sequesterRsrc --keepParent", archive_text)


if __name__ == "__main__":
    unittest.main()
