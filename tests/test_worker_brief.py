from __future__ import annotations

import unittest


TASK_MARKDOWN = """# TASK-001 - Exact projection example

## Status

ACTIVE

## Goal

Keep GOAL-EXACT.

## Architecture Basis

Keep ARCHITECTURE-EXACT.

## Dependencies

Keep DEPENDENCIES-EXACT.

## Scope

Keep SCOPE-EXACT.

## Allowed Changes

- target.txt

## Forbidden Changes

- protected.txt

## Acceptance Criteria

1. Keep ACCEPTANCE-EXACT.

## Verification

Do not project this section.

## Stop Conditions

STOP on STOP-EXACT.

## Next Task

Do not project this section either.
"""


class WorkerBriefTests(unittest.TestCase):
    def test_projects_exact_title_authority_and_required_sections(self):
        from tools.worker_brief import (
            BRIEF_AUTHORITY_STATEMENT,
            REQUIRED_BRIEF_SECTIONS,
            build_worker_brief,
        )

        brief = build_worker_brief(TASK_MARKDOWN)

        self.assertTrue(brief.startswith("# TASK-001 - Exact projection example\n"))
        self.assertIn(BRIEF_AUTHORITY_STATEMENT, brief)
        for marker in (
            "GOAL-EXACT",
            "ARCHITECTURE-EXACT",
            "DEPENDENCIES-EXACT",
            "SCOPE-EXACT",
            "target.txt",
            "protected.txt",
            "ACCEPTANCE-EXACT",
            "STOP-EXACT",
        ):
            self.assertIn(marker, brief)
        for section in REQUIRED_BRIEF_SECTIONS:
            self.assertEqual(brief.count(f"## {section}\n"), 1)
        self.assertNotIn("## Status", brief)
        self.assertNotIn("## Verification", brief)
        self.assertNotIn("## Next Task", brief)

    def test_preserves_each_required_section_body_exactly(self):
        from tools.worker_brief import REQUIRED_BRIEF_SECTIONS, build_worker_brief

        brief = build_worker_brief(TASK_MARKDOWN)

        for section in REQUIRED_BRIEF_SECTIONS:
            original_body = self._section_body(TASK_MARKDOWN, section)
            projected_body = self._section_body(brief, section)
            self.assertEqual(projected_body, original_body.rstrip("\r\n"))

    def test_missing_or_duplicate_title_fails_closed(self):
        from tools.worker_brief import build_worker_brief

        without_title = TASK_MARKDOWN.replace(
            "# TASK-001 - Exact projection example\n",
            "",
            1,
        )
        with_duplicate = TASK_MARKDOWN + "\n# SECOND TASK TITLE\n"

        with self.assertRaisesRegex(ValueError, "exactly one Task title"):
            build_worker_brief(without_title)
        with self.assertRaisesRegex(ValueError, "exactly one Task title"):
            build_worker_brief(with_duplicate)

    def test_missing_or_duplicate_required_section_fails_closed(self):
        from tools.worker_brief import REQUIRED_BRIEF_SECTIONS, build_worker_brief

        for section in REQUIRED_BRIEF_SECTIONS:
            with self.subTest(section=section, case="missing"):
                broken = TASK_MARKDOWN.replace(f"## {section}\n", "## Removed\n", 1)
                with self.assertRaisesRegex(
                    ValueError,
                    "missing required Worker Brief sections",
                ):
                    build_worker_brief(broken)

            with self.subTest(section=section, case="duplicate"):
                broken = TASK_MARKDOWN + f"\n## {section}\n\nDUPLICATE\n"
                with self.assertRaisesRegex(
                    ValueError,
                    "duplicated required Worker Brief sections",
                ):
                    build_worker_brief(broken)

    def test_candidate_b_one_step_instruction_is_not_present(self):
        from tools.worker_brief import build_worker_brief

        brief = build_worker_brief(TASK_MARKDOWN)

        self.assertNotIn("Choose exactly one next Worker action", brief)
        self.assertNotIn("Do not attempt to solve the entire Task", brief)

    @staticmethod
    def _section_body(markdown: str, section: str) -> str:
        marker = f"## {section}\n"
        start = markdown.index(marker) + len(marker)
        following = markdown.find("\n## ", start)
        end = len(markdown) if following == -1 else following
        return markdown[start:end].strip("\n")


if __name__ == "__main__":
    unittest.main()
