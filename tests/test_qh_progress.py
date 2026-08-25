import io
import subprocess
import threading
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tests.git_fixture_utils import GitSeedRepository, run_git


class VerificationProgressTests(unittest.TestCase):
    def _harness_core(self):
        import tools.harness_core as harness_core

        return harness_core

    def test_command_start_is_visible_before_the_child_finishes(self) -> None:
        harness_core = self._harness_core()
        child_started = threading.Event()
        allow_child_to_finish = threading.Event()
        results = []
        errors = []

        def blocking_run(*args, **kwargs):
            child_started.set()
            allow_child_to_finish.wait(timeout=2.0)
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="child stdout\n",
                stderr="",
            )

        def run_verification() -> None:
            try:
                results.extend(
                    harness_core.run_verification_commands(
                        harness_core.VerificationContract(("python check.py",)),
                        r"C:\repo",
                    )
                )
            except BaseException as exc:  # Preserve worker-thread failures for the test.
                errors.append(exc)

        output = io.StringIO()
        with patch("tools.harness_core.subprocess.run", side_effect=blocking_run):
            with redirect_stdout(output):
                worker = threading.Thread(target=run_verification)
                worker.start()
                self.assertTrue(child_started.wait(timeout=1.0))
                try:
                    self.assertIn(
                        "Verification [1/1] START: python check.py",
                        output.getvalue(),
                    )
                finally:
                    allow_child_to_finish.set()
                    worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(results[0].stdout, "child stdout\n")

    def test_long_running_command_emits_elapsed_heartbeat(self) -> None:
        harness_core = self._harness_core()
        heartbeat_seen = threading.Event()
        progress_lines = []

        def blocking_run(*args, **kwargs):
            heartbeat_seen.wait(timeout=0.25)
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="",
                stderr="",
            )

        def record_progress(*args, **kwargs):
            line = " ".join(str(item) for item in args)
            progress_lines.append(line)
            if "HEARTBEAT" in line:
                heartbeat_seen.set()

        with (
            patch("tools.harness_core.subprocess.run", side_effect=blocking_run),
            patch("tools.harness_core.VERIFICATION_HEARTBEAT_SECONDS", 0.01, create=True),
            patch("builtins.print", side_effect=record_progress),
        ):
            harness_core.run_verification_commands(
                harness_core.VerificationContract(("python slow.py",)),
                r"C:\repo",
            )

        heartbeat_lines = [line for line in progress_lines if "HEARTBEAT" in line]
        self.assertTrue(heartbeat_lines, progress_lines)
        self.assertIn("elapsed=", heartbeat_lines[0])
        self.assertIn("s", heartbeat_lines[0])

    def test_completion_preserves_child_output_and_exact_exit_code(self) -> None:
        harness_core = self._harness_core()
        completed = subprocess.CompletedProcess(
            args=["python", "fail.py"],
            returncode=7,
            stdout="preserved stdout\n",
            stderr="preserved stderr\n",
        )
        output = io.StringIO()

        with patch("tools.harness_core.subprocess.run", return_value=completed):
            with redirect_stdout(output):
                results = harness_core.run_verification_commands(
                    harness_core.VerificationContract(("python fail.py",)),
                    r"C:\repo",
                )

        self.assertEqual(results[0].exit_code, 7)
        self.assertEqual(results[0].stdout, "preserved stdout\n")
        self.assertEqual(results[0].stderr, "preserved stderr\n")
        self.assertIn("Verification [1/1] COMPLETE: exit=7 elapsed=", output.getvalue())

    def test_reporting_error_does_not_reinterpret_child_failure(self) -> None:
        harness_core = self._harness_core()
        completed = subprocess.CompletedProcess(
            args=["python", "fail.py"],
            returncode=9,
            stdout="",
            stderr="failure",
        )

        with (
            patch("tools.harness_core.subprocess.run", return_value=completed),
            patch("builtins.print", side_effect=OSError("progress unavailable")),
        ):
            results = harness_core.run_verification_commands(
                harness_core.VerificationContract(("python fail.py",)),
                r"C:\repo",
            )

        self.assertEqual(results[0].exit_code, 9)
        self.assertEqual(results[0].stderr, "failure")

    def test_commands_remain_sequential_and_execute_once(self) -> None:
        harness_core = self._harness_core()
        active_children = 0
        maximum_active_children = 0
        executed = []

        def record_run(tokens, **kwargs):
            nonlocal active_children, maximum_active_children
            active_children += 1
            maximum_active_children = max(maximum_active_children, active_children)
            executed.append(tokens)
            active_children -= 1
            return subprocess.CompletedProcess(tokens, 0, "", "")

        with patch("tools.harness_core.subprocess.run", side_effect=record_run):
            results = harness_core.run_verification_commands(
                harness_core.VerificationContract(
                    ("python first.py", "python second.py")
                ),
                r"C:\repo",
            )

        self.assertEqual(executed, [["python", "first.py"], ["python", "second.py"]])
        self.assertEqual(maximum_active_children, 1)
        self.assertEqual([result.exit_code for result in results], [0, 0])


class CloseProgressAndGitProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.seed = GitSeedRepository(
            {
                "STATUS.md": (
                    "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
                    "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit old\n\n"
                    "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n"
                    "Task Baseline: BASELINE\n"
                ),
                "tasks/QH-V2-TEST-001.md": (
                    "# Test Task\n\n"
                    "## Status\n\nACTIVE\n\n"
                    "## Allowed Changes\n\n"
                    "- `STATUS.md`\n"
                    "- `tasks/QH-V2-TEST-001.md`\n\n"
                    "## Forbidden Changes\n\n"
                    "- `forbidden.txt`\n\n"
                    "## Verification\n\n"
                    "Run exactly:\n\n"
                    "`python -c \"print('ok')\"`\n"
                ),
            }
        )
        self.repo_copy = self.seed.new_copy()
        self.repo = self.repo_copy.path
        baseline = run_git(self.repo, "rev-parse", "HEAD")
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            status_path.read_text(encoding="utf-8").replace("BASELINE", baseline),
            encoding="utf-8",
        )
        run_git(self.repo, "add", "--", "STATUS.md")
        run_git(self.repo, "commit", "-q", "-m", "persist task baseline")
        self.implementation_head = run_git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.repo_copy.cleanup()
        self.seed.cleanup()

    def test_close_reports_major_phases_and_profiles_git_calls(self) -> None:
        import tools.harness_core as harness_core
        import tools.qh as qh

        original_harness_run_git = harness_core._run_git
        original_qh_run_git = qh._run_git
        git_calls = []

        def count_harness_git(*args, **kwargs):
            git_calls.append(args[1])
            return original_harness_run_git(*args, **kwargs)

        def count_qh_git(*args, **kwargs):
            git_calls.append(args[1])
            return original_qh_run_git(*args, **kwargs)

        output = io.StringIO()
        with (
            patch.object(harness_core, "_run_git", side_effect=count_harness_git),
            patch.object(qh, "_run_git", side_effect=count_qh_git),
            redirect_stdout(output),
        ):
            exit_code = qh.command_close(self.repo, self.implementation_head)

        self.assertEqual(exit_code, 0)
        self.assertEqual(len(git_calls), 15, git_calls)
        phase_output = output.getvalue()
        self.assertIn("[qh close] phase=review status=START", phase_output)
        self.assertIn("[qh close] phase=review status=COMPLETE", phase_output)
        self.assertIn(
            "[qh close] phase=post-verification-integrity status=START",
            phase_output,
        )
        self.assertIn(
            "[qh close] phase=final-gate-lifecycle status=COMPLETE",
            phase_output,
        )


if __name__ == "__main__":
    unittest.main()
