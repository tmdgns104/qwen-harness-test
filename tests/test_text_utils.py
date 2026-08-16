import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from text_utils import normalize_whitespace, slugify_heading, truncate_with_ellipsis


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


class TruncateWithEllipsisTests(unittest.TestCase):
    def test_returns_original_when_it_fits(self) -> None:
        self.assertEqual(truncate_with_ellipsis("abc", 3), "abc")

    def test_truncated_result_respects_max_length(self) -> None:
        self.assertEqual(truncate_with_ellipsis("abcdef", 5), "ab...")

    def test_minimum_supported_length(self) -> None:
        self.assertEqual(truncate_with_ellipsis("abcdef", 3), "...")

    def test_preserves_prefix_before_ellipsis(self) -> None:
        self.assertEqual(truncate_with_ellipsis("안녕하세요Qwen", 6), "안녕하...")


class SlugifyHeadingTests(unittest.TestCase):
    def test_normalizes_case_and_whitespace(self) -> None:
        self.assertEqual(
            slugify_heading("  Hello   Qwen World  "),
            "hello-qwen-world",
        )

    def test_preserves_non_whitespace_characters(self) -> None:
        self.assertEqual(slugify_heading("  RAG   설계  "), "rag-설계")


if __name__ == "__main__":
    unittest.main()
