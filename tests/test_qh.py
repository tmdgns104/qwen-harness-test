import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


QH = Path(__file__).resolve().parents[1] / "tools" / "qh.py"


class QhStatusCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")
        (self.repo / "tasks").mkdir()
        (self.repo / "STATUS.md").write_text("Current Task: QH-V2-TEST-001 - ACTIVE\n", encoding="utf-8")
        (self.repo / "tasks" / "QH-V2-TEST-001.md").write_text("## Allowed Changes\n\n- `seed.txt`\n\n## Forbidden Changes\n\n- `forbidden.txt`\n\n## Verification\n\nRun exactly:\n\n`python -c \"print(1)\"`\n", encoding="utf-8")
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "baseline")

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True)

    def test_status_reports_current_task_task_file_clean_git_and_scope(self):
        result = subprocess.run([sys.executable, str(QH), "status"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("QH-V2-TEST-001", result.stdout)
        self.assertIn("tasks/QH-V2-TEST-001.md", result.stdout.replace("\\", "/"))
        self.assertIn("seed.txt", result.stdout)
        self.assertIn("forbidden.txt", result.stdout)
        self.assertIn("clean", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
