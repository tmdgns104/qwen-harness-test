from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


QH = Path(__file__).resolve().parents[1] / "tools" / "qh.py"


class QhTaskScaffoldTests(unittest.TestCase):
    def test_valid_task_id_creates_unapproved_draft_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "tasks").mkdir()

            result = subprocess.run(
                [sys.executable, str(QH), "task-new", "QH-V2-DEMO-001"],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            task_path = repo / "tasks" / "QH-V2-DEMO-001.md"
            self.assertTrue(task_path.is_file())
            markdown = task_path.read_text(encoding="utf-8")
            self.assertIn("## Status\n\nDRAFT - HUMAN REVIEW REQUIRED", markdown)
            self.assertEqual(
                sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file()),
                ["tasks/QH-V2-DEMO-001.md"],
            )


if __name__ == "__main__":
    unittest.main()
