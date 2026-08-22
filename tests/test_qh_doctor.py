from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
import qh as qh_module


VALID_STATUS = (
    "Current Task: QH-V2-DEMO-001 - ACTIVE\n\n"
    "Previous Task: QH-V2-DEMO-000 - COMPLETE - VERIFIED - commit deadbeef\n\n"
    "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n"
    "Task Baseline: deadbeef\n"
)
VALID_TASK = """# QH-V2-DEMO-001 - Doctor Fixture

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Exercise doctor parsing.

## Allowed Changes

- `STATUS.md`
- `tasks/QH-V2-DEMO-001.md`

## Forbidden Changes

- `tools/**`

## Verification

Run exactly:

`python -c "print('ok')"`
"""


class FakeJsonResponse:
    def __init__(self, payload: object) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.payload


def _fake_success_opener(request, timeout):
    return FakeJsonResponse({"models": [{"name": "qwen3:8b"}]})


def _git_status(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _prepare_contract_repo(repo: Path, *, clean: bool = False, remote: bool = False) -> None:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "tasks").mkdir()
    for name in ("PROJECT.md", "REQUIREMENTS.md", "DECISIONS.md"):
        (repo / name).write_text(f"# {name}\n", encoding="utf-8", newline="\n")
    (repo / "STATUS.md").write_text(VALID_STATUS, encoding="utf-8", newline="\n")
    (repo / "tasks" / "QH-V2-DEMO-001.md").write_text(
        VALID_TASK,
        encoding="utf-8",
        newline="\n",
    )
    if remote:
        subprocess.run(
            ["git", "-C", str(repo), "remote", "add", "origin", "https://example.invalid/demo.git"],
            check=True,
        )
    if clean:
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "-c",
                "user.name=Doctor Fixture",
                "-c",
                "user.email=doctor@example.invalid",
                "commit",
                "-qm",
                "fixture baseline",
            ],
            check=True,
        )


def _run_doctor_direct(repo: Path, opener=_fake_success_opener) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output):
        result = qh_module.command_doctor(repo, ollama_opener=opener)
    return result, output.getvalue()


class QhDoctorCliTests(unittest.TestCase):
    def test_doctor_command_is_recognized_without_live_backend(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch.object(sys, "argv", ["qh.py", "doctor"]),
            patch.object(qh_module, "command_doctor", return_value=0) as doctor,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = qh_module.main()

        self.assertEqual(result, 0, stdout.getvalue() + stderr.getvalue())
        doctor.assert_called_once()

    def test_doctor_reports_python_and_local_repository_checks_without_mutation(self) -> None:
        before_status = _git_status(ROOT)

        result, output = _run_doctor_direct(ROOT)

        self.assertEqual(result, 0, output)
        for label in (
            "PYTHON_RUNTIME",
            "GIT_AVAILABLE",
            "REPOSITORY_ROOT",
            "SOURCE_OF_TRUTH",
            "WORKTREE",
            "GIT_REMOTE",
        ):
            with self.subTest(label=label):
                self.assertRegex(output, rf"{label}:\s+(PASS|WARN|FAIL)\b")
        self.assertEqual(_git_status(ROOT), before_status)

    def test_valid_contract_reports_lifecycle_task_scope_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_contract_repo(repo)
            before_status = (repo / "STATUS.md").read_bytes()
            before_task = (repo / "tasks" / "QH-V2-DEMO-001.md").read_bytes()
            before_git = _git_status(repo)

            result, output = _run_doctor_direct(repo)

            self.assertEqual(result, 0, output)
            for label in (
                "LIFECYCLE",
                "CURRENT_TASK",
                "CHANGE_SCOPE",
                "VERIFICATION_CONTRACT",
            ):
                with self.subTest(label=label):
                    self.assertRegex(output, rf"{label}:\s+PASS\b")
            self.assertEqual((repo / "STATUS.md").read_bytes(), before_status)
            self.assertEqual(
                (repo / "tasks" / "QH-V2-DEMO-001.md").read_bytes(),
                before_task,
            )
            self.assertEqual(_git_status(repo), before_git)

    def test_contract_failures_are_nonzero_and_later_checks_still_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_contract_repo(repo)
            status_path = repo / "STATUS.md"
            task_path = repo / "tasks" / "QH-V2-DEMO-001.md"

            status_path.write_text(
                VALID_STATUS + "Current Task: DUPLICATE - ACTIVE\n",
                encoding="utf-8",
                newline="\n",
            )
            lifecycle_result, lifecycle_output = _run_doctor_direct(repo)
            self.assertNotEqual(lifecycle_result, 0, lifecycle_output)
            self.assertRegex(lifecycle_output, r"LIFECYCLE:\s+FAIL\b")
            self.assertRegex(
                lifecycle_output,
                r"VERIFICATION_CONTRACT:\s+(PASS|WARN|FAIL)\b",
            )

            status_path.write_text(VALID_STATUS, encoding="utf-8", newline="\n")
            task_path.write_text(
                VALID_TASK.replace("## Allowed Changes\n\n- `STATUS.md`\n- `tasks/QH-V2-DEMO-001.md`\n\n", ""),
                encoding="utf-8",
                newline="\n",
            )
            scope_result, scope_output = _run_doctor_direct(repo)
            self.assertNotEqual(scope_result, 0, scope_output)
            self.assertRegex(scope_output, r"CHANGE_SCOPE:\s+FAIL\b")
            self.assertRegex(scope_output, r"VERIFICATION_CONTRACT:\s+PASS\b")

            task_path.write_text(
                VALID_TASK.replace(
                    "Run exactly:\n\n`python -c \"print('ok')\"`",
                    "`python -c \"print('ok')\"`",
                ),
                encoding="utf-8",
                newline="\n",
            )
            verification_result, verification_output = _run_doctor_direct(repo)
            self.assertNotEqual(verification_result, 0, verification_output)
            self.assertRegex(
                verification_output,
                r"VERIFICATION_CONTRACT:\s+FAIL\b",
            )

    def test_ollama_reachable_and_default_model_present_are_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_contract_repo(repo)
            captured: dict[str, object] = {}

            def fake_opener(request, timeout):
                captured["url"] = request.full_url
                captured["method"] = request.get_method()
                captured["timeout"] = timeout
                return FakeJsonResponse({"models": [{"name": "qwen3:8b"}]})

            result, output = _run_doctor_direct(repo, fake_opener)

            self.assertEqual(result, 0, output)
            self.assertRegex(output, r"OLLAMA_ENDPOINT:\s+PASS\b")
            self.assertRegex(output, r"OLLAMA_MODEL:\s+PASS\b")
            self.assertEqual(captured["method"], "GET")
            self.assertTrue(str(captured["url"]).endswith("/api/tags"))
            self.assertGreater(float(captured["timeout"]), 0.0)

    def test_ollama_model_missing_is_fail_and_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_contract_repo(repo)

            def fake_opener(request, timeout):
                return FakeJsonResponse({"models": [{"name": "other-model:latest"}]})

            result, output = _run_doctor_direct(repo, fake_opener)

            self.assertNotEqual(result, 0, output)
            self.assertRegex(output, r"OLLAMA_ENDPOINT:\s+PASS\b")
            self.assertRegex(output, r"OLLAMA_MODEL:\s+FAIL\b")

    def test_ollama_unreachable_timeout_and_backend_errors_are_sanitized(self) -> None:
        cases = (
            URLError("connection refused"),
            TimeoutError("timed out"),
            RuntimeError(
                "Bearer supersecret http://user:password@127.0.0.1:11434/api/tags"
            ),
        )
        for error in cases:
            with self.subTest(error=type(error).__name__):
                with tempfile.TemporaryDirectory() as tmp:
                    repo = Path(tmp)
                    _prepare_contract_repo(repo)

                    def fake_opener(request, timeout, error=error):
                        raise error

                    result, output = _run_doctor_direct(repo, fake_opener)

                    self.assertNotEqual(result, 0, output)
                    self.assertRegex(output, r"OLLAMA_ENDPOINT:\s+FAIL\b")
                    self.assertRegex(output, r"OLLAMA_MODEL:\s+FAIL\b")
                    self.assertNotIn("supersecret", output)
                    self.assertNotIn("password", output)
                    self.assertNotIn("Bearer", output)
                    self.assertNotIn("user:", output)

    def test_overall_status_distinguishes_pass_warn_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pass_repo = Path(tmp) / "pass"
            pass_repo.mkdir()
            _prepare_contract_repo(pass_repo, clean=True, remote=True)
            result, output = _run_doctor_direct(pass_repo)
            self.assertEqual(result, 0, output)
            self.assertRegex(output, r"OVERALL:\s+PASS\b")

        with tempfile.TemporaryDirectory() as tmp:
            warn_repo = Path(tmp)
            _prepare_contract_repo(warn_repo)
            result, output = _run_doctor_direct(warn_repo)
            self.assertEqual(result, 0, output)
            self.assertRegex(output, r"WORKTREE:\s+WARN\b")
            self.assertRegex(output, r"GIT_REMOTE:\s+WARN\b")
            self.assertRegex(output, r"OVERALL:\s+WARN\b")

        with tempfile.TemporaryDirectory() as tmp:
            fail_repo = Path(tmp)
            _prepare_contract_repo(fail_repo)
            (fail_repo / "STATUS.md").write_text(
                VALID_STATUS + "Current Task: DUPLICATE - ACTIVE\n",
                encoding="utf-8",
                newline="\n",
            )
            result, output = _run_doctor_direct(fail_repo)
            self.assertNotEqual(result, 0, output)
            self.assertRegex(output, r"LIFECYCLE:\s+FAIL\b")
            self.assertRegex(output, r"OVERALL:\s+FAIL\b")


if __name__ == "__main__":
    unittest.main()
