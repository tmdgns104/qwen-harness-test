from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


QHOPS_PATH = Path(__file__).resolve().parents[1] / "qh_ops.py"
SPEC = importlib.util.spec_from_file_location("qh_ops_under_test", QHOPS_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load qhops module: {QHOPS_PATH}")
qh_ops = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qh_ops)


def completed(*, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def verification_result(exit_code: int):
    return SimpleNamespace(exit_code=exit_code, stdout="", stderr="")


class Perf004QhopsWorkflowTests(unittest.TestCase):
    def test_red_emits_focused_timing(self):
        root = Path("repo")
        with (
            mock.patch.object(qh_ops, "require_clean"),
            mock.patch.object(qh_ops, "git", return_value=completed()),
            mock.patch.object(
                qh_ops,
                "first_verification",
                return_value=("python -m unittest focused", verification_result(1)),
            ),
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                qh_ops.cmd_red(root, "red-sha")

        self.assertIn("Focused RED Duration:", output.getvalue())

    def test_green_runs_focused_once_without_full_verify_or_push(self):
        root = Path("repo")
        with (
            mock.patch.object(qh_ops, "require_clean"),
            mock.patch.object(qh_ops, "git", return_value=completed()),
            mock.patch.object(
                qh_ops,
                "first_verification",
                return_value=("python -m unittest focused", verification_result(0)),
            ) as focused,
            mock.patch.object(qh_ops, "qh") as qh_call,
            mock.patch.object(qh_ops, "safe_push") as push,
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                qh_ops.cmd_green(root, "green-sha")

        focused.assert_called_once_with(root)
        qh_call.assert_not_called()
        push.assert_not_called()
        self.assertIn("Focused GREEN Duration:", output.getvalue())

    def test_green_focused_failure_stops_before_push(self):
        root = Path("repo")
        with (
            mock.patch.object(qh_ops, "require_clean"),
            mock.patch.object(qh_ops, "git", return_value=completed()),
            mock.patch.object(
                qh_ops,
                "first_verification",
                return_value=("python -m unittest focused", verification_result(1)),
            ) as focused,
            mock.patch.object(qh_ops, "qh") as qh_call,
            mock.patch.object(qh_ops, "safe_push") as push,
        ):
            with self.assertRaises(qh_ops.Stop):
                qh_ops.cmd_green(root, "green-sha")

        focused.assert_called_once_with(root)
        qh_call.assert_not_called()
        push.assert_not_called()

    def test_commit_impl_uses_focused_check_without_full_verify_or_push(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            task_path = root / "tasks" / "QH-V2-PERF-004.md"
            task_path.parent.mkdir(parents=True)
            task_path.write_text("scope", encoding="utf-8")

            def parse_scope(_markdown):
                return object()

            with (
                mock.patch.object(qh_ops, "current_task_id", return_value="QH-V2-PERF-004"),
                mock.patch.object(qh_ops, "current_task_path", return_value=task_path),
                mock.patch.object(
                    qh_ops,
                    "changed_paths",
                    side_effect=[("ops/qhops/qh_ops.py",), ("ops/qhops/qh_ops.py",)],
                ),
                mock.patch.object(
                    qh_ops,
                    "import_harness",
                    return_value=(object(), lambda _path, _scope: True, parse_scope, object(), object()),
                ),
                mock.patch.object(
                    qh_ops,
                    "first_verification",
                    return_value=("python -m unittest focused", verification_result(0)),
                ) as focused,
                mock.patch.object(qh_ops, "cmd_verify") as full_verify,
                mock.patch.object(qh_ops, "git", return_value=completed()) as git_call,
                mock.patch.object(qh_ops, "require_clean"),
                mock.patch.object(qh_ops, "safe_push") as push,
            ):
                qh_ops.cmd_commit_impl(root)

        focused.assert_called_once_with(root)
        full_verify.assert_not_called()
        push.assert_not_called()
        self.assertTrue(
            any(call.args[1:3] == ("commit", "-m") for call in git_call.call_args_list),
            git_call.call_args_list,
        )

    def test_finish_reports_authoritative_close_timing_and_single_full_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            task_path = root / "tasks" / "QH-V2-PERF-004.md"
            task_path.parent.mkdir(parents=True)
            task_path.write_text("task", encoding="utf-8")

            def git_result(_root, *args, **_kwargs):
                if args[:2] == ("rev-parse", "HEAD"):
                    return completed(stdout="abc123\n")
                return completed()

            expected_paths = tuple(sorted(("STATUS.md", "tasks/QH-V2-PERF-004.md")))
            with (
                mock.patch.object(qh_ops, "require_clean"),
                mock.patch.object(qh_ops, "current_task_id", return_value="QH-V2-PERF-004"),
                mock.patch.object(qh_ops, "current_task_path", return_value=task_path),
                mock.patch.object(qh_ops, "git", side_effect=git_result),
                mock.patch.object(qh_ops, "qh") as qh_call,
                mock.patch.object(qh_ops, "changed_paths", return_value=expected_paths),
                mock.patch.object(qh_ops, "safe_push") as push,
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    qh_ops.cmd_finish(root)

        qh_call.assert_called_once_with(root, "close", "abc123")
        push.assert_called_once_with(root)
        text = output.getvalue()
        self.assertIn("Authoritative Close Duration:", text)
        self.assertIn("Finish Total Duration:", text)
        self.assertIn("Authoritative Full Verification Count: 1", text)

    def test_finish_close_failure_never_commits_or_pushes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            task_path = root / "tasks" / "QH-V2-PERF-004.md"
            task_path.parent.mkdir(parents=True)
            task_path.write_text("task", encoding="utf-8")

            def git_result(_root, *args, **_kwargs):
                if args[:2] == ("rev-parse", "HEAD"):
                    return completed(stdout="abc123\n")
                return completed()

            with (
                mock.patch.object(qh_ops, "require_clean"),
                mock.patch.object(qh_ops, "current_task_id", return_value="QH-V2-PERF-004"),
                mock.patch.object(qh_ops, "current_task_path", return_value=task_path),
                mock.patch.object(qh_ops, "git", side_effect=git_result) as git_call,
                mock.patch.object(qh_ops, "qh", side_effect=qh_ops.Stop("close failed")),
                mock.patch.object(qh_ops, "safe_push") as push,
            ):
                with self.assertRaises(qh_ops.Stop):
                    qh_ops.cmd_finish(root)

        push.assert_not_called()
        self.assertFalse(
            any(call.args[1:2] == ("commit",) for call in git_call.call_args_list),
            git_call.call_args_list,
        )


if __name__ == "__main__":
    unittest.main()
