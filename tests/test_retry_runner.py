from __future__ import annotations

import unittest
from unittest.mock import patch

from tools.task_runner import RunnerFailureKind, RunnerResult


class RetryRunnerTests(unittest.TestCase):
    def make_result(
        self,
        *,
        interaction_ok=False,
        output_text="",
        steps_consumed=1,
        error="error",
        failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
        write_attempted=False,
    ):
        return RunnerResult(
            interaction_ok=interaction_ok,
            output_text=output_text,
            steps_consumed=steps_consumed,
            error=error,
            failure_kind=failure_kind,
            write_attempted=write_attempted,
        )

    def test_first_attempt_normal_returns_normal_without_retry(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        calls = []
        normal = self.make_result(
            interaction_ok=True,
            output_text="done",
            error=None,
            failure_kind=None,
        )

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return normal

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.NORMAL)
        self.assertEqual(result.attempts_consumed, 1)
        self.assertIs(result.runner_result, normal)
        self.assertFalse(result.write_side_effect_risk)
        self.assertEqual(len(calls), 1)

    def test_first_safety_failure_returns_fail_without_retry(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        calls = []
        safety = self.make_result(
            failure_kind=RunnerFailureKind.SAFETY,
            error="any safety wording",
        )

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return safety

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.FAIL)
        self.assertEqual(result.attempts_consumed, 1)
        self.assertEqual(len(calls), 1)

    def test_step_budget_returns_fail_without_retry(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        calls = []
        exhausted = self.make_result(
            failure_kind=RunnerFailureKind.STEP_BUDGET,
            error="budget wording irrelevant",
        )

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return exhausted

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.FAIL)
        self.assertEqual(result.attempts_consumed, 1)
        self.assertEqual(len(calls), 1)

    def test_transient_without_write_retries_once_then_normal(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        transient = self.make_result(
            failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
            error="first arbitrary wording",
        )
        normal = self.make_result(
            interaction_ok=True,
            output_text="done",
            error=None,
            failure_kind=None,
        )
        results = [transient, normal]
        calls = []

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return results.pop(0)

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.NORMAL)
        self.assertEqual(result.attempts_consumed, 2)
        self.assertIs(result.runner_result, normal)
        self.assertEqual(len(calls), 2)

    def test_two_transient_failures_become_blocked(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        results = [
            self.make_result(error="first wording"),
            self.make_result(error="completely different second wording"),
        ]
        calls = []

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return results.pop(0)

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.BLOCKED)
        self.assertEqual(result.attempts_consumed, 2)
        self.assertEqual(len(calls), 2)

    def test_transient_after_write_is_blocked_without_retry(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        calls = []
        result_with_write = self.make_result(
            failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
            write_attempted=True,
            error="continuation disconnected",
        )

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return result_with_write

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.BLOCKED)
        self.assertEqual(result.attempts_consumed, 1)
        self.assertTrue(result.write_side_effect_risk)
        self.assertEqual(len(calls), 1)

    def test_no_third_runner_attempt_occurs(self):
        from tools.retry_runner import MAX_RUNNER_ATTEMPTS, RetryOutcomeKind, run_with_retry

        calls = []

        def fake_run(repo_root, task_id):
            calls.append((repo_root, task_id))
            return self.make_result(
                failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
                error=f"failure-{len(calls)}",
            )

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(MAX_RUNNER_ATTEMPTS, 2)
        self.assertEqual(result.outcome_kind, RetryOutcomeKind.BLOCKED)
        self.assertEqual(result.attempts_consumed, 2)
        self.assertEqual(len(calls), 2)

    def test_retry_decision_does_not_depend_on_error_wording(self):
        from tools.retry_runner import RetryOutcomeKind, run_with_retry

        transient = self.make_result(
            failure_kind=RunnerFailureKind.TRANSIENT_WORKER,
            error="this text contains scope forbidden unknown tool but is transient",
        )
        normal = self.make_result(
            interaction_ok=True,
            output_text="PASS",
            error=None,
            failure_kind=None,
        )
        results = [transient, normal]

        def fake_run(repo_root, task_id):
            return results.pop(0)

        with patch("tools.retry_runner.run_single_task", side_effect=fake_run):
            result = run_with_retry("repo", "TASK-001")

        self.assertEqual(result.outcome_kind, RetryOutcomeKind.NORMAL)
        self.assertEqual(result.attempts_consumed, 2)
        self.assertEqual(result.runner_result.output_text, "PASS")
        self.assertFalse(hasattr(result, "task_pass"))
        self.assertFalse(hasattr(result, "verified"))
        self.assertFalse(hasattr(result, "final_gate"))


if __name__ == "__main__":
    unittest.main()
