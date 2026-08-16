import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from text_utils import normalize_whitespace


class NormalizeWhitespaceTests(unittest.TestCase):
    def test_empty_string(self) -> None:
        self.assertEqual(normalize_whitespace(""), "")

    def test_trims_outer_whitespace(self) -> None:
        self.assertEqual(normalize_whitespace("   hello world   "), "hello world")

    def test_collapses_repeated_spaces(self) -> None:
        self.assertEqual(normalize_whitespace("hello    world"), "hello world")

    def test_collapses_mixed_whitespace(self) -> None:
        self.assertEqual(
            normalize_whitespace("hello\tworld\npython\r\nqwen"),
            "hello world python qwen",
        )

    def test_preserves_non_whitespace_text(self) -> None:
        self.assertEqual(
            normalize_whitespace("  안녕\tQwen   Harness  "),
            "안녕 Qwen Harness",
        )


if __name__ == "__main__":
    unittest.main()
