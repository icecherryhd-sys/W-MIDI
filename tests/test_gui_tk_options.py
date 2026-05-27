import ast
import unittest
from pathlib import Path


class GuiTkOptionTests(unittest.TestCase):
    def test_tk_frame_constructors_use_scalar_padding(self) -> None:
        source = Path("midi_wled_bridge/gui.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        offenders: list[int] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "Frame":
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "tk":
                continue
            for keyword in node.keywords:
                if keyword.arg in {"padx", "pady"} and isinstance(keyword.value, ast.Tuple):
                    offenders.append(node.lineno)

        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
