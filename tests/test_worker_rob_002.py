from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.harness_core import ToolRequest, WorkerStep


TASK_TEMPLATE = """# QH-V2-WORKER-ROB-002 - Example

## Goal

Keep GOAL-EXACT.

## Architecture Basis

Keep ARCH-EXACT.

## Dependencies

Keep DEP-EXACT.

## Scope

Keep SCOPE-EXACT.

## Allowed Changes

- target.txt
- STATUS.md
- tasks/QH-V2-WORKER-ROB-002.md

## Forbidden Changes

- protected.txt

## Acceptance Criteria

1. Keep ACCEPT-EXACT.

## Stop Conditions

STOP on STOP-EXACT.

## Next Task

Do not project this section.
"""


class FakeSession:
    def __init__(self, step):
        self.step = step
        self.start_calls = 0

    def start(self):
        self.start_calls += 1
        return self.step

    def continue_with_tool_result(self, result):
        raise AssertionError("benchmark must not continue or execute tools")


class WorkerRob002Tests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "tasks").mkdir()
        (root / "STATUS.md").write_text(
            "Current Task: QH-V2-WORKER-ROB-002 - ACTIVE\n",
            encoding="utf-8",
        )
        (root / "tasks" / "QH-V2-WORKER-ROB-002.md").write_text(
            TASK_TEMPLATE,
            encoding="utf-8",
        )
        return temp, root

    def test_worker_brief_projects_exact_required_sections_only(self):
        from experiments.worker_rob_002 import (
            BRIEF_AUTHORITY_STATEMENT,
            REQUIRED_BRIEF_SECTIONS,
            build_worker_brief,
        )

        brief = build_worker_brief(TASK_TEMPLATE)

        self.assertTrue(brief.startswith("# QH-V2-WORKER-ROB-002 - Example\n"))
        self.assertIn(BRIEF_AUTHORITY_STATEMENT, brief)
        for marker in (
            "GOAL-EXACT",
            "ARCH-EXACT",
            "DEP-EXACT",
            "SCOPE-EXACT",
            "ACCEPT-EXACT",
            "STOP-EXACT",
        ):
            self.assertIn(marker, brief)
        for section in REQUIRED_BRIEF_SECTIONS:
            self.assertEqual(brief.count(f"## {section}\n"), 1)
        self.assertNotIn("## Next Task", brief)
        self.assertNotIn("Do not project this section.", brief)

    def test_missing_required_section_fails_closed(self):
        from experiments.worker_rob_002 import build_worker_brief

        broken = TASK_TEMPLATE.replace("## Goal\n\nKeep GOAL-EXACT.\n\n", "")
        with self.assertRaisesRegex(ValueError, "missing required Worker Brief sections"):
            build_worker_brief(broken)

    def test_duplicate_required_section_fails_closed(self):
        from experiments.worker_rob_002 import build_worker_brief

        broken = TASK_TEMPLATE + "\n## Goal\n\nSECOND GOAL\n"
        with self.assertRaisesRegex(ValueError, "duplicated required Worker Brief sections"):
            build_worker_brief(broken)

    def test_variant_prompts_use_full_task_brief_and_one_step_instruction(self):
        from experiments.worker_rob_002 import (
            ONE_STEP_INSTRUCTION,
            VARIANT_BRIEF,
            VARIANT_BRIEF_ONE_STEP,
            VARIANT_STABLE,
            build_variant_prompts,
        )

        prompts = build_variant_prompts(TASK_TEMPLATE)

        self.assertEqual(prompts[VARIANT_STABLE], TASK_TEMPLATE)
        self.assertNotIn(ONE_STEP_INSTRUCTION, prompts[VARIANT_BRIEF])
        self.assertTrue(prompts[VARIANT_BRIEF_ONE_STEP].endswith(ONE_STEP_INSTRUCTION + "\n"))
        self.assertIn("GOAL-EXACT", prompts[VARIANT_BRIEF])

    def test_interleaved_plan_has_ten_runs_each_and_rotates_first_variant(self):
        from experiments.worker_rob_002 import VARIANTS, interleaved_plan

        plan = interleaved_plan(10)

        self.assertEqual(len(plan), 30)
        counts = {variant: sum(1 for item in plan if item[0] == variant) for variant in VARIANTS}
        self.assertEqual(counts, {variant: 10 for variant in VARIANTS})
        self.assertEqual(plan[0][0], VARIANTS[0])
        self.assertEqual(plan[3][0], VARIANTS[1])
        self.assertEqual(plan[6][0], VARIANTS[2])

    def test_read_request_inside_repo_is_valid_without_executing_read(self):
        from experiments.worker_rob_002 import review_tool_request
        from tools.harness_core import parse_change_scope

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        review = review_tool_request(
            root,
            "QH-V2-WORKER-ROB-002",
            parse_change_scope(TASK_TEMPLATE),
            ToolRequest("call-1", "read_repo_text", {"relative_path": "missing.txt"}),
        )

        self.assertTrue(review["schema_valid"])
        self.assertTrue(review["path_compatible"])
        self.assertIsNone(review["validation_error"])
        self.assertFalse((root / "missing.txt").exists())

    def test_out_of_scope_write_is_rejected_without_execution(self):
        from experiments.worker_rob_002 import review_tool_request
        from tools.harness_core import parse_change_scope

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        review = review_tool_request(
            root,
            "QH-V2-WORKER-ROB-002",
            parse_change_scope(TASK_TEMPLATE),
            ToolRequest(
                "call-2",
                "write_repo_text",
                {"relative_path": "protected.txt", "content": "NO"},
            ),
        )

        self.assertTrue(review["schema_valid"])
        self.assertFalse(review["path_compatible"])
        self.assertFalse((root / "protected.txt").exists())

    def test_lifecycle_write_is_rejected_even_when_change_scope_allows_it(self):
        from experiments.worker_rob_002 import review_tool_request
        from tools.harness_core import parse_change_scope

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        original = (root / "STATUS.md").read_text(encoding="utf-8")
        review = review_tool_request(
            root,
            "QH-V2-WORKER-ROB-002",
            parse_change_scope(TASK_TEMPLATE),
            ToolRequest(
                "call-status",
                "write_repo_text",
                {"relative_path": "STATUS.md", "content": "HACKED"},
            ),
        )

        self.assertTrue(review["schema_valid"])
        self.assertFalse(review["path_compatible"])
        self.assertIn("lifecycle-control", str(review["validation_error"]))
        self.assertEqual((root / "STATUS.md").read_text(encoding="utf-8"), original)

    def test_write_content_is_hashed_not_persisted_in_argument_evidence(self):
        from experiments.worker_rob_002 import bounded_arguments

        content = "SECRET-LIKE-LONG-CONTENT"
        evidence = bounded_arguments(
            ToolRequest(
                "call-write",
                "write_repo_text",
                {"relative_path": "target.txt", "content": content},
            )
        )

        self.assertEqual(evidence["relative_path"], "target.txt")
        self.assertEqual(evidence["content_length"], len(content))
        self.assertEqual(
            evidence["content_sha256"],
            hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        self.assertNotIn("content", evidence)

    def test_measure_initial_step_records_one_valid_request_without_execution(self):
        from experiments.worker_rob_002 import measure_initial_step

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        session = FakeSession(
            WorkerStep(
                True,
                "",
                (
                    ToolRequest(
                        "call-write",
                        "write_repo_text",
                        {"relative_path": "target.txt", "content": "NEW"},
                    ),
                ),
                None,
            )
        )

        result = measure_initial_step(
            root,
            "QH-V2-WORKER-ROB-002",
            TASK_TEMPLATE,
            "candidate_worker_brief",
            1,
            "prompt",
            session_factory=lambda request, *, tools: session,
        )

        self.assertEqual(session.start_calls, 1)
        self.assertTrue(result["transport_success"])
        self.assertEqual(result["tool_request_count"], 1)
        self.assertTrue(result["valid_bounded_first_step"])
        self.assertFalse(result["write_executed"])
        self.assertFalse((root / "target.txt").exists())

    def test_measure_initial_step_records_multi_tool_safety_shape_without_execution(self):
        from experiments.worker_rob_002 import measure_initial_step

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)
        session = FakeSession(
            WorkerStep(
                True,
                "",
                (
                    ToolRequest("call-1", "read_repo_text", {"relative_path": "a.txt"}),
                    ToolRequest("call-2", "read_repo_text", {"relative_path": "b.txt"}),
                ),
                None,
            )
        )

        result = measure_initial_step(
            root,
            "QH-V2-WORKER-ROB-002",
            TASK_TEMPLATE,
            "stable_full_task",
            1,
            "prompt",
            session_factory=lambda request, *, tools: session,
        )

        self.assertTrue(result["multi_tool_safety_shape"])
        self.assertFalse(result["valid_bounded_first_step"])
        self.assertFalse(result["write_executed"])

    def test_timeout_exception_is_recorded_as_evidence(self):
        from experiments.worker_rob_002 import measure_initial_step

        temp, root = self.make_repo()
        self.addCleanup(temp.cleanup)

        def failing_factory(request, *, tools):
            raise TimeoutError("timed out")

        result = measure_initial_step(
            root,
            "QH-V2-WORKER-ROB-002",
            TASK_TEMPLATE,
            "stable_full_task",
            1,
            "prompt",
            session_factory=failing_factory,
        )

        self.assertFalse(result["transport_success"])
        self.assertTrue(result["timeout_occurrence"])
        self.assertEqual(result["failure_classification"], "timeout_exception")
        self.assertFalse(result["write_executed"])

    def test_summary_and_evidence_include_required_metrics_and_authority_language(self):
        from experiments.worker_rob_002 import (
            ONE_STEP_INSTRUCTION,
            VARIANTS,
            render_evidence,
            summarize_all,
        )

        runs = []
        for variant in VARIANTS:
            for index in range(1, 11):
                runs.append(
                    {
                        "variant": variant,
                        "run_index": index,
                        "elapsed_seconds": 1.0,
                        "transport_success": True,
                        "timeout_occurrence": False,
                        "valid_bounded_first_step": True,
                        "zero_tool_terminal_response": False,
                        "multi_tool_safety_shape": False,
                        "invalid_unknown_tool_request": False,
                        "scope_incompatible_requested_path": False,
                        "write_executed": False,
                    }
                )
        data = {
            "runtime": {"model": "qwen3:8b", "think": False, "timeout_seconds": 30.0},
            "one_step_instruction": ONE_STEP_INSTRUCTION,
            "summary": summarize_all(runs),
        }
        evidence = render_evidence(data)

        for text in (
            "Stable - Full Task",
            "Candidate A - Deterministic Worker Brief",
            "Candidate B - Deterministic Worker Brief + One-Step Instruction",
            "transport-success rate",
            "timeout rate",
            "valid bounded first step",
            "multi-tool",
            "median",
            "Promotion Recommendation",
            "Repository PASS",
            "Final Gate",
            "GLOBALIZATION = NOT AUTHORIZED",
        ):
            self.assertIn(text, evidence)


if __name__ == "__main__":
    unittest.main()
