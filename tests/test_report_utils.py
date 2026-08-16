import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from report_utils import build_section_anchor


class BuildSectionAnchorTests(unittest.TestCase):
    def test_uses_slugified_title(self) -> None:
        self.assertEqual(
            build_section_anchor("  Hello   Qwen World  ", "sec"),
            "sec:hello-qwen-world",
        )

    def test_preserves_prefix(self) -> None:
        self.assertEqual(
            build_section_anchor("RAG 설계", "chapter-2"),
            "chapter-2:rag-설계",
        )


if __name__ == "__main__":
    unittest.main()
