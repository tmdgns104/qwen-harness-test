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


    def test_status_reports_dirty_changed_paths(self):
        (self.repo / "seed.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "new.txt").write_text("new\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(QH), "status"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dirty", result.stdout.lower())
        self.assertIn("seed.txt", result.stdout)
        self.assertIn("new.txt", result.stdout)


    def test_preflight_accepts_clean_valid_task_without_modifying_repo(self):
        result = subprocess.run([sys.executable, str(QH), "preflight"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("QH-V2-TEST-001", result.stdout)
        self.assertIn("clean", result.stdout.lower())
        self.assertEqual(self._git("status", "--porcelain").stdout, "")


    def test_verify_runs_task_verification_contract_and_reports_result(self):
        result = subprocess.run([sys.executable, str(QH), "verify"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("QH-V2-TEST-001", result.stdout)
        self.assertIn("python -c", result.stdout)
        self.assertIn("exit", result.stdout.lower())
        self.assertIn("0", result.stdout)
        self.assertEqual(self._git("status", "--porcelain").stdout, "")


    def test_verify_returns_failure_when_verification_command_fails(self):
        task = self.repo / "tasks" / "QH-V2-TEST-001.md"
        text = task.read_text(encoding="utf-8")
        text = text.replace("`python -c \"print(1)\"`", "`python -c \"import sys; sys.exit(7)\"`")
        task.write_text(text, encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "failing verification contract")
        result = subprocess.run([sys.executable, str(QH), "verify"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Exit Code: 7", result.stdout)


    def test_review_reports_allowed_change_verification_and_diff_check(self):
        (self.repo / "seed.txt").write_text("changed\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(QH), "review"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.lower()
        self.assertIn("qh-v2-test-001", output)
        self.assertIn("seed.txt", output)
        self.assertIn("allowed", output)
        self.assertIn("verification", output)
        self.assertIn("diff", output)
        self.assertEqual(self._git("status", "--porcelain").stdout, " M seed.txt\n")


    def test_review_rejects_forbidden_changed_path(self):
        (self.repo / "forbidden.txt").write_text("forbidden\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(QH), "review"], cwd=self.repo, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        output = result.stdout.lower()
        self.assertIn("forbidden.txt", output)
        self.assertIn("forbidden", output)
        self.assertIn("final gate: fail", output)
        self.assertIn("scope", output)


    def test_start_updates_only_top_level_lifecycle_fields_and_preserves_handoff_history(self):
        current = "Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234"
        historical = "- Historical note: Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234"
        (self.repo / "STATUS.md").write_text(
            current + "\n\n"
            + "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            + "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n\n"
            + "Handoff:\n"
            + historical + "\n",
            encoding="utf-8",
        )
        (self.repo / "tasks" / "QH-V2-TEST-002.md").write_text(
            "## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "lifecycle start baseline")

        result = subprocess.run(
            [sys.executable, str(QH), "start", "QH-V2-TEST-002"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        status = (self.repo / "STATUS.md").read_text(encoding="utf-8")
        self.assertTrue(status.startswith(
            "Current Task: QH-V2-TEST-002 - ACTIVE\n\n"
            "Previous Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED"
        ))
        self.assertIn(historical, status)
        self.assertEqual(status.count(current), 1)


    def test_start_rejects_duplicate_current_task_without_modifying_status(self):
        original = (
            "Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n\n"
            "Current Task: QH-V2-DUPLICATE-001 - ACTIVE\n"
        )
        status_path = self.repo / "STATUS.md"
        status_path.write_text(original, encoding="utf-8")
        (self.repo / "tasks" / "QH-V2-TEST-002.md").write_text(
            "## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "duplicate lifecycle baseline")

        result = subprocess.run(
            [sys.executable, str(QH), "start", "QH-V2-TEST-002"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Expected exactly one Current Task line", result.stderr)
        self.assertEqual(status_path.read_text(encoding="utf-8"), original)


    def test_start_rejects_missing_target_task_without_modifying_status(self):
        status_path = self.repo / "STATUS.md"
        original = status_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(QH), "start", "QH-V2-MISSING-999"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Task file not found", result.stderr)
        self.assertEqual(status_path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
