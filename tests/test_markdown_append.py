import hashlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "long_decisions.md"

BASELINE_SHA256 = "fa708f6aeab5a69a373002dab57a742d91d53619dd15999493deb9d41bbd25ed"
EXPECTED_APPEND = '\n## ADR-016 - Long Markdown Append Regression\n\n- Status: Accepted\n- Decision: The Worker must append this ADR after ADR-015.\n- Evidence: Git/Test evidence is authoritative; Worker self-reported PASS is not authoritative.\n- Scope: Existing ADR-001 through ADR-015 must remain byte-for-byte unchanged.\n\n## ADR-017 - Safe Editing Discipline\n\n- Status: Accepted\n- Decision: Long Markdown append work must avoid guessed exact-string edit loops.\n- Stop: If the same logical modification fails twice, report BLOCKED and stop.\n- Boundary: No file other than `docs/long_decisions.md` may be modified by the Worker.\n'


class LongMarkdownAppendTests(unittest.TestCase):
    def test_existing_baseline_is_preserved_exactly(self) -> None:
        content = TARGET.read_text(encoding="utf-8")
        self.assertTrue(content.endswith(EXPECTED_APPEND))
        prefix = content[: -len(EXPECTED_APPEND)]
        self.assertEqual(
            hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
            BASELINE_SHA256,
        )

    def test_new_adrs_exist_once_and_in_order(self) -> None:
        content = TARGET.read_text(encoding="utf-8")
        self.assertEqual(content.count("## ADR-016 - Long Markdown Append Regression"), 1)
        self.assertEqual(content.count("## ADR-017 - Safe Editing Discipline"), 1)
        self.assertLess(
            content.index("## ADR-015 - Baseline Decision 015"),
            content.index("## ADR-016 - Long Markdown Append Regression"),
        )
        self.assertLess(
            content.index("## ADR-016 - Long Markdown Append Regression"),
            content.index("## ADR-017 - Safe Editing Discipline"),
        )

    def test_required_content_is_exact(self) -> None:
        content = TARGET.read_text(encoding="utf-8")
        self.assertTrue(content.endswith(EXPECTED_APPEND))


if __name__ == "__main__":
    unittest.main()
