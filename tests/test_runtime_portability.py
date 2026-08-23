from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimePortabilityTests(unittest.TestCase):
    def test_documented_run_entry_reaches_runner_without_pythonpath(self) -> None:
        task_id = "QH-V2-PORTABILITY-FIXTURE"

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            shutil.copytree(
                ROOT / "tools",
                repo / "tools",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            (repo / "tasks").mkdir()

            (repo / "STATUS.md").write_text(
                f"Current Task: {task_id} - ACTIVE\n",
                encoding="utf-8",
                newline="\n",
            )
            (repo / "tasks" / f"{task_id}.md").write_text(
                f"""# {task_id} - Runtime Portability Fixture

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Goal

Reach the delayed Runner import chain and fail safely before Worker startup.
""",
                encoding="utf-8",
                newline="\n",
            )

            env = os.environ.copy()
            env.pop("PYTHONPATH", None)

            result = subprocess.run(
                [sys.executable, "tools/qh.py", "run", task_id],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            combined = result.stdout + result.stderr

            self.assertEqual(result.returncode, 1, combined)
            self.assertNotIn("ModuleNotFoundError", combined)
            self.assertNotIn("Traceback", combined)
            self.assertIn(f"Task: {task_id}", result.stdout)
            self.assertIn("Outcome: FAIL", result.stdout)
            self.assertIn("Failure Kind: SAFETY", result.stdout)
            self.assertIn("Write Side Effect Risk: NO", result.stdout)


if __name__ == "__main__":
    unittest.main()
