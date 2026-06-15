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


if __name__ == "__main__":
    unittest.main()
