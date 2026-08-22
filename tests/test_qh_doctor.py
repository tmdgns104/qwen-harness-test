from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QH = ROOT / "tools" / "qh.py"


class QhDoctorCliTests(unittest.TestCase):
    def test_doctor_command_is_recognized_and_reports_python_runtime(self) -> None:
        result = subprocess.run(
            [sys.executable, str(QH), "doctor"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        combined = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 2, combined)
        self.assertIn("PYTHON_RUNTIME", combined)
        self.assertRegex(combined, r"PYTHON_RUNTIME:\s+(PASS|WARN|FAIL)\b")


if __name__ == "__main__":
    unittest.main()
