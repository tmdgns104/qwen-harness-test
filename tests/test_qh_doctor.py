from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QH = ROOT / "tools" / "qh.py"


def _git_status() -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


class QhDoctorCliTests(unittest.TestCase):
    def _run_doctor(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(QH), "doctor"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

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


if __name__ == "__main__":
    unittest.main()
