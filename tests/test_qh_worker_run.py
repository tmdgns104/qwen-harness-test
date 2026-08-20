from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qh as qh_cli

from tools.retry_runner import RetryOutcome, RetryOutcomeKind
from tools.task_runner import RunnerFailureKind, RunnerResult


class QhWorkerRunTests(unittest.TestCase):
    def make_outcome(
        self,
        *,
        outcome_kind=RetryOutcomeKind.NORMAL,
        attempts=1,
        interaction_ok=True,
        output_text="",
        error=None,
        failure_kind=None,
        write_attempted=False,
        write_risk=False,
    ):
        runner_result = RunnerResult(
            interaction_ok=interaction_ok,
            output_text=output_text,
            steps_consumed=1,
            error=error,
            failure_kind=failure_kind,
            write_attempted=write_attempted,
        )
        return RetryOutcome(
            outcome_kind=outcome_kind,
            attempts_consumed=attempts,
            runner_result=runner_result,
            error=error,
            write_side_effect_risk=write_risk,
        )

    def run_command(self, outcome, task_id="TASK-001"):
        seen = []

        def fake_retry(repo_root, supplied_task_id):
            seen.append((repo_root, supplied_task_id))
            return outcome

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = qh_cli.command_run(
                Path("repo"),
                task_id,
                retry_callable=fake_retry,
            )

        return code, stdout.getvalue(), seen

    def test_main_accepts_run_and_passes_task_id_unchanged(self):
        with patch.object(qh_cli, "command_run", return_value=0) as command:
            with patch.object(sys, "argv", ["qh.py", "run", "QH-V2-TEST-123"]):
                code = qh_cli.main()

        self.assertEqual(code, 0)
        command.assert_called_once()
        self.assertEqual(command.call_args.args[1], "QH-V2-TEST-123")

    def test_run_requires_explicit_task_id(self):
        stderr = io.StringIO()

        with patch.object(sys, "argv", ["qh.py", "run"]):
            with redirect_stderr(stderr):
                code = qh_cli.main()

        self.assertEqual(code, 1)
        self.assertIn("run requires a Task ID", stderr.getvalue())

    def test_normal_reports_structured_result_and_exit_zero(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.NORMAL,
            attempts=1,
            output_text="done",
        )

        code, output, seen = self.run_command(outcome, "TASK-ABC")

        self.assertEqual(code, 0)
        self.assertEqual(seen[0][1], "TASK-ABC")
        self.assertIn("Task: TASK-ABC", output)
        self.assertIn("Outcome: NORMAL", output)
        self.assertIn("Attempts: 1", output)
        self.assertIn("Failure Kind: NONE", output)
        self.assertIn("Write Side Effect Risk: NO", output)
        self.assertIn("Worker Output: done", output)

    def test_fail_reports_failure_kind_and_nonzero(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.FAIL,
            attempts=1,
            interaction_ok=False,
            error="arbitrary safety wording",
            failure_kind=RunnerFailureKind.SAFETY,
        )

        code, output, _ = self.run_command(outcome)

        self.assertNotEqual(code, 0)
        self.assertIn("Outcome: FAIL", output)
        self.assertIn("Failure Kind: SAFETY", output)
        self.assertIn("Error: arbitrary safety wording", output)

    def test_blocked_reports_write_risk_and_nonzero(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.BLOCKED,
            attempts=2,
            interaction_ok=False,
            error="worker unavailable",
            failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
            write_attempted=True,
            write_risk=True,
        )

        code, output, _ = self.run_command(outcome)

        self.assertNotEqual(code, 0)
        self.assertIn("Outcome: BLOCKED", output)
        self.assertIn("Attempts: 2", output)
        self.assertIn("Failure Kind: TRANSIENT_WORKER", output)
        self.assertIn("Write Side Effect Risk: YES", output)

    def test_worker_pass_text_remains_only_worker_output(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.NORMAL,
            output_text="PASS",
        )

        code, output, _ = self.run_command(outcome)

        self.assertEqual(code, 0)
        self.assertIn("Worker Output: PASS", output)
        self.assertNotIn("Repository PASS", output)
        self.assertNotIn("Final Gate: PASS", output)
        self.assertNotIn("COMPLETE", output)
        self.assertNotIn("VERIFIED", output)

    def test_empty_worker_output_is_not_printed(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.NORMAL,
            output_text="",
        )

        _, output, _ = self.run_command(outcome)

        self.assertNotIn("Worker Output:", output)

    def test_error_wording_does_not_change_provided_outcome(self):
        outcome = self.make_outcome(
            outcome_kind=RetryOutcomeKind.FAIL,
            interaction_ok=False,
            error="transient retry transport write PASS BLOCKED",
            failure_kind=RunnerFailureKind.SAFETY,
        )

        code, output, _ = self.run_command(outcome)

        self.assertNotEqual(code, 0)
        self.assertIn("Outcome: FAIL", output)
        self.assertNotIn("Outcome: BLOCKED", output)


if __name__ == "__main__":
    unittest.main()
