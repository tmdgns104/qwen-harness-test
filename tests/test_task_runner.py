from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.harness_core import WorkerStep


class FakeSession:
    def __init__(self, request, *, tools, step):
        self.request = request
        self.tools = tools
        self._step = step
        self.start_calls = 0

    def start(self):
        self.start_calls += 1
        return self._step


class ScriptedSession:
    def __init__(self, steps):
        self.steps = list(steps)
        self.index = 0
        self.start_calls = 0
        self.continue_calls = 0
        self.tool_results = []

    def start(self):
        self.start_calls += 1
        step = self.steps[self.index]
        self.index += 1
        return step

    def continue_with_tool_result(self, result):
        self.continue_calls += 1
        self.tool_results.append(result)
        step = self.steps[self.index]
        self.index += 1
        return step


class TaskRunnerTests(unittest.TestCase):
    def make_repo(
        self,
        *,
        current_line="Current Task: TASK-001 - ACTIVE",
        task_id="TASK-001",
    ):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "tasks").mkdir()
        (root / "STATUS.md").write_text(
            current_line + "\n",
            encoding="utf-8",
        )
        task_markdown = (
            "# TASK-001\n\n"
            "## Allowed Changes\n\n"
            "- target.txt\n\n"
            "## Forbidden Changes\n\n"
            "- protected.txt\n"
        )
        (root / "tasks" / f"{task_id}.md").write_text(
            task_markdown,
            encoding="utf-8",
        )
        return temp, root, task_markdown

    def test_matching_active_task_starts_worker_with_full_task_and_two_tools(self):
        from tools.task_runner import run_single_task

        temp, root, task_markdown = self.make_repo()
        self.addCleanup(temp.cleanup)

        captured = {}

        def session_factory(request, *, tools):
            captured["request"] = request
            captured["tools"] = tools
            session = FakeSession(
                request,
                tools=tools,
                step=WorkerStep(True, "done", (), None),
            )
            captured["session"] = session
            return session

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=session_factory,
        )

        self.assertIn(task_markdown, captured["request"].task_text)
        self.assertEqual(
            tuple(tool.name for tool in captured["tools"]),
            ("read_repo_text", "write_repo_text"),
        )
        self.assertEqual(captured["session"].start_calls, 1)
        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.output_text, "done")
        self.assertEqual(result.steps_consumed, 1)
        self.assertIsNone(result.error)

    def test_mismatched_task_id_fails_before_worker_creation(self):
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        called = False

        def session_factory(request, *, tools):
            nonlocal called
            called = True
            raise AssertionError("worker must not be created")

        result = run_single_task(
            root,
            "TASK-OTHER",
            session_factory=session_factory,
        )

        self.assertFalse(called)
        self.assertFalse(result.interaction_ok)
        self.assertEqual(result.steps_consumed, 0)
        self.assertIsNotNone(result.error)

    def test_non_active_current_task_fails_before_worker_creation(self):
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo(
            current_line="Current Task: TASK-001 - COMPLETE - VERIFIED - commit abc"
        )
        self.addCleanup(temp.cleanup)

        called = False

        def session_factory(request, *, tools):
            nonlocal called
            called = True
            raise AssertionError("worker must not be created")

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=session_factory,
        )

        self.assertFalse(called)
        self.assertFalse(result.interaction_ok)
        self.assertEqual(result.steps_consumed, 0)
        self.assertIsNotNone(result.error)

    def test_terminal_worker_text_is_interaction_output_not_task_pass(self):
        from tools.task_runner import RunnerResult, run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        def session_factory(request, *, tools):
            return FakeSession(
                request,
                tools=tools,
                step=WorkerStep(True, "PASS", (), None),
            )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=session_factory,
        )

        self.assertIsInstance(result, RunnerResult)
        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.output_text, "PASS")
        self.assertFalse(hasattr(result, "task_pass"))
        self.assertFalse(hasattr(result, "verified"))
        self.assertFalse(hasattr(result, "final_gate"))


    def test_valid_read_executes_and_continues(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "note.txt").write_text("HELLO", encoding="utf-8")

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-read",
                            "read_repo_text",
                            {"relative_path": "note.txt"},
                        ),
                    ),
                    None,
                ),
                WorkerStep(True, "done", (), None),
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.steps_consumed, 2)
        self.assertEqual(result.output_text, "done")
        self.assertEqual(session.continue_calls, 1)
        self.assertEqual(len(session.tool_results), 1)
        self.assertEqual(session.tool_results[0].call_id, "call-read")
        self.assertTrue(session.tool_results[0].ok)
        self.assertEqual(session.tool_results[0].output, "HELLO")
        self.assertIsNone(session.tool_results[0].error)

    def test_valid_in_scope_write_executes_and_continues(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-write",
                            "write_repo_text",
                            {
                                "relative_path": "target.txt",
                                "content": "NEW",
                            },
                        ),
                    ),
                    None,
                ),
                WorkerStep(True, "done", (), None),
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.steps_consumed, 2)
        self.assertEqual(
            (root / "target.txt").read_text(encoding="utf-8"),
            "NEW",
        )
        self.assertEqual(session.continue_calls, 1)
        self.assertTrue(session.tool_results[0].ok)
        self.assertEqual(session.tool_results[0].call_id, "call-write")

    def test_multiple_tool_requests_fail_before_any_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-1",
                            "write_repo_text",
                            {
                                "relative_path": "target.txt",
                                "content": "FIRST",
                            },
                        ),
                        ToolRequest(
                            "call-2",
                            "write_repo_text",
                            {
                                "relative_path": "target.txt",
                                "content": "SECOND",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertFalse((root / "target.txt").exists())
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_unknown_tool_fails_before_repository_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-unknown",
                            "delete_repo_text",
                            {"relative_path": "target.txt"},
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertFalse((root / "target.txt").exists())
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_worker_cannot_supply_write_scope_arguments(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-scope",
                            "write_repo_text",
                            {
                                "relative_path": "target.txt",
                                "content": "NEW",
                                "allowed_changes": ("target.txt",),
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertFalse((root / "target.txt").exists())
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_out_of_scope_write_fails_before_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-forbidden",
                            "write_repo_text",
                            {
                                "relative_path": "protected.txt",
                                "content": "NO",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertFalse((root / "protected.txt").exists())
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)


    def test_worker_cannot_write_status_md_even_if_task_allows_it(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        task_path = root / "tasks" / "TASK-001.md"
        task_path.write_text(
            "# TASK-001\n\n"
            "## Allowed Changes\n\n"
            "- STATUS.md\n"
            "- target.txt\n\n"
            "## Forbidden Changes\n\n"
            "- protected.txt\n",
            encoding="utf-8",
        )

        original_status = (root / "STATUS.md").read_text(encoding="utf-8")

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-status",
                            "write_repo_text",
                            {
                                "relative_path": "STATUS.md",
                                "content": "HACKED",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(
            (root / "STATUS.md").read_text(encoding="utf-8"),
            original_status,
        )
        self.assertEqual(session.continue_calls, 0)

    def test_worker_cannot_write_active_task_contract_even_if_allowed(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, task_markdown = self.make_repo()
        self.addCleanup(temp.cleanup)

        task_path = root / "tasks" / "TASK-001.md"
        task_path.write_text(
            task_markdown.replace(
                "- target.txt",
                "- target.txt\n- tasks/TASK-001.md",
            ),
            encoding="utf-8",
        )
        original = task_path.read_text(encoding="utf-8")

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-task",
                            "write_repo_text",
                            {
                                "relative_path": "tasks/TASK-001.md",
                                "content": "HACKED",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(task_path.read_text(encoding="utf-8"), original)
        self.assertEqual(session.continue_calls, 0)

    def test_malformed_read_arguments_fail_before_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-bad",
                            "read_repo_text",
                            {
                                "relative_path": "note.txt",
                                "extra": "not-allowed",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(session.continue_calls, 0)

    def test_parent_directory_escape_fails_before_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-escape",
                            "read_repo_text",
                            {"relative_path": "../outside.txt"},
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(session.continue_calls, 0)

    def test_transport_failure_stops_fail_closed(self):
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(False, "", (), "transport failed"),
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(result.steps_consumed, 1)
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_safe_read_error_becomes_failed_tool_result_and_continues(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-missing",
                            "read_repo_text",
                            {"relative_path": "missing.txt"},
                        ),
                    ),
                    None,
                ),
                WorkerStep(True, "handled", (), None),
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.output_text, "handled")
        self.assertEqual(session.continue_calls, 1)
        self.assertFalse(session.tool_results[0].ok)
        self.assertEqual(session.tool_results[0].output, "")
        self.assertIsNotNone(session.tool_results[0].error)

    def test_eighth_worker_step_may_terminate_normally(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import MAX_WORKER_STEPS, run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "note.txt").write_text("HELLO", encoding="utf-8")

        steps = []
        for index in range(MAX_WORKER_STEPS - 1):
            steps.append(
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            f"call-{index}",
                            "read_repo_text",
                            {"relative_path": "note.txt"},
                        ),
                    ),
                    None,
                )
            )
        steps.append(WorkerStep(True, "done-at-eight", (), None))

        session = ScriptedSession(steps)

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertTrue(result.interaction_ok)
        self.assertEqual(result.steps_consumed, MAX_WORKER_STEPS)
        self.assertEqual(result.output_text, "done-at-eight")
        self.assertEqual(
            session.continue_calls,
            MAX_WORKER_STEPS - 1,
        )

    def test_eighth_worker_step_request_stops_without_execution_or_ninth_step(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import MAX_WORKER_STEPS, run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)
        (root / "note.txt").write_text("HELLO", encoding="utf-8")

        steps = []
        for index in range(MAX_WORKER_STEPS):
            steps.append(
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            f"call-{index}",
                            "read_repo_text",
                            {"relative_path": "note.txt"},
                        ),
                    ),
                    None,
                )
            )

        session = ScriptedSession(steps)

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(result.steps_consumed, MAX_WORKER_STEPS)
        self.assertEqual(
            session.continue_calls,
            MAX_WORKER_STEPS - 1,
        )
        self.assertEqual(
            len(session.tool_results),
            MAX_WORKER_STEPS - 1,
        )
        self.assertIsNotNone(result.error)


    def test_absolute_path_fails_before_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-absolute",
                            "read_repo_text",
                            {"relative_path": str((root / "note.txt").resolve())},
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_write_content_must_be_string(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-content-type",
                            "write_repo_text",
                            {
                                "relative_path": "target.txt",
                                "content": 123,
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertFalse((root / "target.txt").exists())
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)

    def test_empty_tool_call_id_fails_before_execution(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "",
                            "read_repo_text",
                            {"relative_path": "note.txt"},
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(session.continue_calls, 0)
        self.assertIsNotNone(result.error)


    def test_worker_cannot_write_status_case_alias(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        task_path = root / "tasks" / "TASK-001.md"
        task_path.write_text(
            "# TASK-001\n\n"
            "## Allowed Changes\n\n"
            "- status.md\n\n"
            "## Forbidden Changes\n\n"
            "- protected.txt\n",
            encoding="utf-8",
        )

        original_status = (root / "STATUS.md").read_text(encoding="utf-8")

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-status-alias",
                            "write_repo_text",
                            {
                                "relative_path": "status.md",
                                "content": "HACKED",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(
            (root / "STATUS.md").read_text(encoding="utf-8"),
            original_status,
        )
        self.assertEqual(session.continue_calls, 0)

    def test_worker_cannot_write_active_task_case_alias(self):
        from tools.harness_core import ToolRequest
        from tools.task_runner import run_single_task

        temp, root, _ = self.make_repo()
        self.addCleanup(temp.cleanup)

        task_path = root / "tasks" / "TASK-001.md"
        task_path.write_text(
            "# TASK-001\n\n"
            "## Allowed Changes\n\n"
            "- tasks/task-001.md\n\n"
            "## Forbidden Changes\n\n"
            "- protected.txt\n",
            encoding="utf-8",
        )
        original = task_path.read_text(encoding="utf-8")

        session = ScriptedSession(
            [
                WorkerStep(
                    True,
                    "",
                    (
                        ToolRequest(
                            "call-task-alias",
                            "write_repo_text",
                            {
                                "relative_path": "tasks/task-001.md",
                                "content": "HACKED",
                            },
                        ),
                    ),
                    None,
                )
            ]
        )

        result = run_single_task(
            root,
            "TASK-001",
            session_factory=lambda request, *, tools: session,
        )

        self.assertFalse(result.interaction_ok)
        self.assertEqual(
            task_path.read_text(encoding="utf-8"),
            original,
        )
        self.assertEqual(session.continue_calls, 0)


if __name__ == "__main__":
    unittest.main()
