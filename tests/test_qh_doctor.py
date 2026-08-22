from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QH = ROOT / "tools" / "qh.py"


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


def _git_status() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _prepare_contract_repo(repo: Path) -> None:
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


def _run_doctor_at(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(QH), "doctor"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


class QhDoctorCliTests(unittest.TestCase):
    def _run_doctor(self) -> subprocess.CompletedProcess[str]:
        return _run_doctor_at(ROOT)

    def test_doctor_command_is_recognized_and_reports_python_runtime(self) -> None:
        result = self._run_doctor()

        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 2, combined)
        self.assertIn("PYTHON_RUNTIME", combined)
        self.assertRegex(combined, r"PYTHON_RUNTIME:\s+(PASS|WARN|FAIL)\b")

    def test_doctor_reports_local_repository_checks_without_mutation(self) -> None:
        before_status = _git_status()

        result = self._run_doctor()
        combined = result.stdout + result.stderr

        self.assertEqual(result.returncode, 0, combined)
        for label in (
            "GIT_AVAILABLE",
            "REPOSITORY_ROOT",
            "SOURCE_OF_TRUTH",
            "WORKTREE",
            "GIT_REMOTE",
        ):
            with self.subTest(label=label):
                self.assertRegex(combined, rf"{label}:\s+(PASS|WARN|FAIL)\b")

        self.assertEqual(_git_status(), before_status)

    def test_valid_contract_reports_lifecycle_task_scope_and_verification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _prepare_contract_repo(repo)
            before_status = (repo / "STATUS.md").read_bytes()
            before_task = (repo / "tasks" / "QH-V2-DEMO-001.md").read_bytes()

            result = _run_doctor_at(repo)
            combined = result.stdout + result.stderr

            self.assertEqual(result.returncode, 0, combined)
            for label in (
                "LIFECYCLE",
                "CURRENT_TASK",
                "CHANGE_SCOPE",
                "VERIFICATION_CONTRACT",
            ):
                with self.subTest(label=label):
                    self.assertRegex(combined, rf"{label}:\s+PASS\b")
            self.assertEqual((repo / "STATUS.md").read_bytes(), before_status)
            self.assertEqual(
                (repo / "tasks" / "QH-V2-DEMO-001.md").read_bytes(),
                before_task,
            )

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
            lifecycle_result = _run_doctor_at(repo)
            lifecycle_output = lifecycle_result.stdout + lifecycle_result.stderr
            self.assertNotEqual(lifecycle_result.returncode, 0, lifecycle_output)
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
            scope_result = _run_doctor_at(repo)
            scope_output = scope_result.stdout + scope_result.stderr
            self.assertNotEqual(scope_result.returncode, 0, scope_output)
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
            verification_result = _run_doctor_at(repo)
            verification_output = verification_result.stdout + verification_result.stderr
            self.assertNotEqual(
                verification_result.returncode,
                0,
                verification_output,
            )
            self.assertRegex(
                verification_output,
                r"VERIFICATION_CONTRACT:\s+FAIL\b",
            )


if __name__ == "__main__":
    unittest.main()
