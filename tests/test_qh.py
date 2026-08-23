import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.git_fixture_utils import GitSeedRepository


QH = Path(__file__).resolve().parents[1] / "tools" / "qh.py"


class QhStatusCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_tmp = tempfile.TemporaryDirectory()
        cls.seed_repo = Path(cls.seed_tmp.name)

        def git(*args):
            return subprocess.run(
                ["git", *args],
                cwd=cls.seed_repo,
                capture_output=True,
                text=True,
                check=True,
            )

        git("init")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test User")

        (cls.seed_repo / "tasks").mkdir()
        (cls.seed_repo / "STATUS.md").write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n",
            encoding="utf-8",
        )
        (cls.seed_repo / "tasks" / "QH-V2-TEST-001.md").write_text(
            "## Allowed Changes\n\n"
            "- `seed.txt`\n"
            "- `STATUS.md`\n\n"
            "## Forbidden Changes\n\n"
            "- `forbidden.txt`\n\n"
            "## Verification\n\n"
            "Run exactly:\n\n"
            "`python -c \"print(1)\"`\n",
            encoding="utf-8",
        )
        (cls.seed_repo / "seed.txt").write_text(
            "seed\n",
            encoding="utf-8",
        )

        git("add", ".")
        git("commit", "-m", "baseline")
        baseline = git("rev-parse", "HEAD").stdout.strip()

        (cls.seed_repo / "STATUS.md").write_text(
            f"Current Task: QH-V2-TEST-001 - ACTIVE\n"
            f"Task Baseline: {baseline}\n",
            encoding="utf-8",
        )

        git("add", "STATUS.md")
        git("commit", "-m", "persist task baseline")

    @classmethod
    def tearDownClass(cls):
        cls.seed_tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        shutil.copytree(
            self.seed_repo,
            self.repo,
            dirs_exist_ok=True,
        )

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
            "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED"
        ))
        self.assertIn(historical, status)
        self.assertEqual(status.count(current), 1)

    def test_start_records_pre_start_head_as_task_baseline(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        (self.repo / "tasks" / "QH-V2-TEST-002.md").write_text(
            "## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "task baseline persistence fixture")
        expected_baseline = self._git("rev-parse", "HEAD").stdout.strip()

        result = subprocess.run(
            [sys.executable, str(QH), "start", "QH-V2-TEST-002"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        status = status_path.read_text(encoding="utf-8")
        self.assertIn(f"Task Baseline: {expected_baseline}", status)
        self.assertEqual(status.count("Task Baseline:"), 1)

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

    def test_close_marks_explicit_current_task_complete_without_committing(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n\n"
            "Handoff:\n- preserve this history\n",
            encoding="utf-8",
        )
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n- `seed.txt`\n- `STATUS.md`\n\n"
            "## Forbidden Changes\n\n- `forbidden.txt`\n\n"
            '## Verification\n\nRun exactly:\n\n`python -c "print(1)"`\n',
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "close lifecycle baseline")
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        status_path.write_text(status_path.read_text(encoding="utf-8").rstrip("\n") + f"\nTask Baseline: {baseline}\n", encoding="utf-8")
        self._git("add", "STATUS.md")
        self._git("commit", "-m", "persist close baseline")
        commit = self._git("rev-parse", "HEAD").stdout.strip()

        result = subprocess.run(
            [sys.executable, str(QH), "close", commit],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Final Gate: PASS", result.stdout)
        status = status_path.read_text(encoding="utf-8")
        self.assertIn(f"Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit {commit}", status)
        self.assertIn("Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678", status)
        self.assertIn("Next Planned Task: QH-V2-TEST-002 - NOT STARTED", status)
        self.assertIn("- preserve this history", status)
        self.assertIn("## Status\n\nCOMPLETE - VERIFIED", task_path.read_text(encoding="utf-8"))
        self.assertNotEqual(self._git("status", "--porcelain").stdout, "")

    def test_close_review_failure_does_not_modify_lifecycle_files(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n- `seed.txt`\n- `STATUS.md`\n\n"
            "## Forbidden Changes\n\n- `forbidden.txt`\n\n"
            '## Verification\n\nRun exactly:\n\n`python -c "import sys; sys.exit(7)"`\n',
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "failing close review baseline")
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        status_path.write_text(status_path.read_text(encoding="utf-8").rstrip("\n") + f"\nTask Baseline: {baseline}\n", encoding="utf-8")
        self._git("add", "STATUS.md")
        self._git("commit", "-m", "persist failing close baseline")
        commit = self._git("rev-parse", "HEAD").stdout.strip()
        original_status = status_path.read_text(encoding="utf-8")
        original_task = task_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(QH), "close", commit],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Final Gate: FAIL", result.stdout)
        self.assertEqual(status_path.read_text(encoding="utf-8"), original_status)
        self.assertEqual(task_path.read_text(encoding="utf-8"), original_task)

    def test_close_rejects_unmarked_verification_command_without_modifying_lifecycle_files(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        verification_side_effect = self.repo / "verification-ran.txt"
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n- `seed.txt`\n- `STATUS.md`\n\n"
            "## Forbidden Changes\n\n- `forbidden.txt`\n\n"
            "## Verification\n\nRun exactly:\n\n"
            "`python -c \"from pathlib import Path; "
            "Path('verification-ran.txt').write_text('ran', encoding='utf-8')\"`\n\n"
            '`python -c "print(2)"`\n',
            encoding="utf-8",
        )

        self._git("add", ".")
        self._git("commit", "-m", "malformed verification close baseline")
        baseline = self._git("rev-parse", "HEAD").stdout.strip()

        status_path.write_text(
            status_path.read_text(encoding="utf-8").rstrip("\n")
            + f"\nTask Baseline: {baseline}\n",
            encoding="utf-8",
        )
        self._git("add", "STATUS.md")
        self._git("commit", "-m", "persist malformed verification baseline")
        commit = self._git("rev-parse", "HEAD").stdout.strip()

        original_status = status_path.read_text(encoding="utf-8")
        original_task = task_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(QH), "close", commit],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("Unmarked verification command", result.stderr)
        self.assertFalse(verification_side_effect.exists())
        self.assertEqual(status_path.read_text(encoding="utf-8"), original_status)
        self.assertEqual(task_path.read_text(encoding="utf-8"), original_task)

    def test_close_rejects_non_head_commit_without_modifying_lifecycle_files(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n- `seed.txt`\n- `STATUS.md`\n\n"
            "## Forbidden Changes\n\n- `forbidden.txt`\n\n"
            "## Verification\n\nRun exactly:\n\n`python --version`\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "older completion candidate")
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        status_path.write_text(status_path.read_text(encoding="utf-8").rstrip("\n") + f"\nTask Baseline: {baseline}\n", encoding="utf-8")
        self._git("add", "STATUS.md")
        self._git("commit", "-m", "persist non-head close baseline")
        old_commit = self._git("rev-parse", "HEAD").stdout.strip()
        (self.repo / "seed.txt").write_text("newer head\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "newer verified head")
        original_status = status_path.read_text(encoding="utf-8")
        original_task = task_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(QH), "close", old_commit],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("HEAD", result.stderr)
        self.assertEqual(status_path.read_text(encoding="utf-8"), original_status)
        self.assertEqual(task_path.read_text(encoding="utf-8"), original_task)

    def test_start_clears_consumed_next_planned_task_without_selecting_future_task(self):
        status_path = self.repo / "STATUS.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n\n"
            "Handoff:\n- preserve this history\n",
            encoding="utf-8",
        )
        (self.repo / "tasks" / "QH-V2-TEST-002.md").write_text(
            "## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "next planned consistency baseline")

        result = subprocess.run(
            [sys.executable, str(QH), "start", "QH-V2-TEST-002"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        status = status_path.read_text(encoding="utf-8")
        self.assertIn("Current Task: QH-V2-TEST-002 - ACTIVE", status)
        self.assertIn("Previous Task: QH-V2-TEST-001 - COMPLETE - VERIFIED - commit abc1234", status)
        self.assertIn("Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED", status)
        self.assertNotIn("Next Planned Task: QH-V2-TEST-002 - NOT STARTED", status)
        self.assertIn("- preserve this history", status)

    def test_review_rejects_committed_forbidden_path_since_explicit_baseline(self):
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        (self.repo / "forbidden.txt").write_text("forbidden\n", encoding="utf-8")
        self._git("add", "forbidden.txt")
        self._git("commit", "-m", "commit forbidden task change")
        self.assertEqual(self._git("status", "--porcelain").stdout, "")

        result = subprocess.run(
            [sys.executable, str(QH), "review", baseline],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        output = result.stdout.lower()
        self.assertIn("forbidden.txt", output)
        self.assertIn("forbidden", output)
        self.assertIn("unexpected changed paths: yes", output)
        self.assertIn("final gate: fail", output)

    def test_review_without_argument_rejects_committed_forbidden_path_since_persisted_baseline(self):
        status = (self.repo / "STATUS.md").read_text(encoding="utf-8")
        self.assertEqual(status.count("Task Baseline:"), 1)

        (self.repo / "forbidden.txt").write_text("forbidden\n", encoding="utf-8")
        self._git("add", "forbidden.txt")
        self._git("commit", "-m", "commit forbidden change after persisted baseline")
        self.assertEqual(self._git("status", "--porcelain").stdout, "")

        result = subprocess.run(
            [sys.executable, str(QH), "review"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        output = result.stdout.lower()
        self.assertIn("forbidden.txt", output)
        self.assertIn("forbidden", output)
        self.assertIn("unexpected changed paths: yes", output)
        self.assertIn("final gate: fail", output)

    def test_close_rejects_committed_forbidden_change_since_persisted_baseline(self):
        status_path = self.repo / "STATUS.md"
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        before_status = status_path.read_text(encoding="utf-8")
        before_task = task_path.read_text(encoding="utf-8")
        (self.repo / "forbidden.txt").write_text("forbidden\n", encoding="utf-8")
        self._git("add", "forbidden.txt")
        self._git("commit", "-m", "committed forbidden before close")
        head = self._git("rev-parse", "HEAD").stdout.strip()

        result = subprocess.run([sys.executable, str(QH), "close", head], cwd=self.repo, capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 1)
        self.assertIn("Final Gate: FAIL", result.stdout)
        self.assertIn("forbidden.txt", result.stdout)
        self.assertEqual(status_path.read_text(encoding="utf-8"), before_status)
        self.assertEqual(task_path.read_text(encoding="utf-8"), before_task)

    def test_review_rejects_invalid_persisted_baseline_without_modifying_repo(self):
        status_path = self.repo / "STATUS.md"
        original = status_path.read_text(encoding="utf-8")
        line = next(x for x in original.splitlines() if x.startswith("Task Baseline:"))
        invalid = original.replace(line, "Task Baseline: definitely-not-a-commit", 1)
        status_path.write_text(invalid, encoding="utf-8")
        before = self._git("status", "--porcelain").stdout

        result = subprocess.run([sys.executable, str(QH), "review"], cwd=self.repo, capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr.lower())
        self.assertEqual(status_path.read_text(encoding="utf-8"), invalid)
        self.assertEqual(self._git("status", "--porcelain").stdout, before)

    def test_review_rejects_invalid_explicit_baseline_without_modifying_repo(self):
        before = self._git("status", "--porcelain").stdout

        result = subprocess.run(
            [sys.executable, str(QH), "review", "definitely-not-a-commit"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr.lower())
        self.assertEqual(self._git("status", "--porcelain").stdout, before)

    def test_review_accepts_committed_allowed_path_since_explicit_baseline(self):
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        (self.repo / "seed.txt").write_text("changed\n", encoding="utf-8")
        self._git("add", "seed.txt")
        self._git("commit", "-m", "commit allowed task change")
        self.assertEqual(self._git("status", "--porcelain").stdout, "")

        result = subprocess.run(
            [sys.executable, str(QH), "review", baseline],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.lower()
        self.assertIn("seed.txt", output)
        self.assertIn("allowed", output)
        self.assertIn("unexpected changed paths: no", output)
        self.assertIn("final gate: pass", output)

    def test_review_combines_committed_range_and_current_uncommitted_changes(self):
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        (self.repo / "seed.txt").write_text("committed change\n", encoding="utf-8")
        self._git("add", "seed.txt")
        self._git("commit", "-m", "commit allowed task change")
        (self.repo / "forbidden.txt").write_text("uncommitted forbidden\n", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(QH), "review", baseline],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        output = result.stdout.lower()
        self.assertIn("seed.txt", output)
        self.assertIn("forbidden.txt", output)
        self.assertIn("allowed", output)
        self.assertIn("forbidden", output)
        self.assertIn("unexpected changed paths: yes", output)
        self.assertIn("final gate: fail", output)


class QhLifecycleStartGuardTests(unittest.TestCase):
    CURRENT_TASK_ID = "QH-V2-CURRENT-001"
    TARGET_TASK_ID = "QH-V2-TARGET-002"

    @classmethod
    def setUpClass(cls):
        cls.seed_tmp = tempfile.TemporaryDirectory()
        cls.seed_repo = Path(cls.seed_tmp.name)

        def git(*args):
            return subprocess.run(
                ["git", *args],
                cwd=cls.seed_repo,
                capture_output=True,
                text=True,
                check=True,
            )

        git("init")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test User")

        (cls.seed_repo / "tasks").mkdir()
        (cls.seed_repo / "STATUS.md").write_text(
            f"Current Task: {cls.CURRENT_TASK_ID} - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            f"Next Planned Task: {cls.TARGET_TASK_ID} - PLANNED\n"
            "Task Baseline: previous-baseline\n\n"
            "Handoff:\n- preserve lifecycle history\n",
            encoding="utf-8",
        )
        (cls.seed_repo / "tasks" / f"{cls.CURRENT_TASK_ID}.md").write_text(
            "# Current Task\n\n## Status\n\nACTIVE\n\n"
            "## Evidence\n\n- preserve current Task bytes\n",
            encoding="utf-8",
        )
        (cls.seed_repo / "tasks" / f"{cls.TARGET_TASK_ID}.md").write_text(
            "# Target Task\n\n## Status\n\n"
            "APPROVED - READY FOR CONTRACT BASELINE\n\n"
            "## Evidence\n\n- preserve target Task bytes\n",
            encoding="utf-8",
        )

        git("add", ".")
        git("commit", "-m", "lifecycle start guard seed")
        cls.seed_head = git("rev-parse", "HEAD").stdout.strip()

    @classmethod
    def tearDownClass(cls):
        cls.seed_tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        shutil.copytree(self.seed_repo, self.repo, dirs_exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    @property
    def status_path(self):
        return self.repo / "STATUS.md"

    @property
    def current_task_path(self):
        return self.repo / "tasks" / f"{self.CURRENT_TASK_ID}.md"

    def _target_task_path(self, task_id=None):
        return self.repo / "tasks" / f"{task_id or self.TARGET_TASK_ID}.md"

    def _write_status(self, current_value):
        self.status_path.write_text(
            f"Current Task: {current_value}\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            f"Next Planned Task: {self.TARGET_TASK_ID} - PLANNED\n"
            "Task Baseline: previous-baseline\n\n"
            "Handoff:\n- preserve lifecycle history\n",
            encoding="utf-8",
        )

    def _run_start(self, target_task_id):
        return subprocess.run(
            [sys.executable, str(QH), "start", target_task_id],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _lifecycle_file_bytes(self, target_task_id):
        paths = {
            self.status_path,
            self.current_task_path,
            self._target_task_path(target_task_id),
        }
        return {
            path.relative_to(self.repo).as_posix(): (
                path.read_bytes() if path.exists() else None
            )
            for path in paths
        }

    def _lifecycle_lines(self):
        labels = (
            "Current Task:",
            "Previous Task:",
            "Next Planned Task:",
            "Task Baseline:",
        )
        return tuple(
            line
            for line in self.status_path.read_text(encoding="utf-8").splitlines()
            if line.startswith(labels)
        )

    def _assert_start_rejected_without_mutation(self, target_task_id):
        before_bytes = self._lifecycle_file_bytes(target_task_id)
        before_lifecycle = self._lifecycle_lines()

        result = self._run_start(target_task_id)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self._lifecycle_file_bytes(target_task_id), before_bytes)
        self.assertEqual(self._lifecycle_lines(), before_lifecycle)
        return result

    def test_rejects_starting_same_active_task_without_mutation(self):
        self._assert_start_rejected_without_mutation(self.CURRENT_TASK_ID)

    def test_rejects_starting_different_task_while_current_is_active_without_mutation(self):
        self._assert_start_rejected_without_mutation(self.TARGET_TASK_ID)

    def test_rejects_non_complete_or_malformed_current_lifecycle_without_mutation(self):
        invalid_current_values = (
            f"{self.CURRENT_TASK_ID} - PLANNED",
            f"{self.CURRENT_TASK_ID} - COMPLETE",
            f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED",
            f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234 extra",
        )

        for current_value in invalid_current_values:
            with self.subTest(current_value=current_value):
                self._write_status(current_value)
                self._assert_start_rejected_without_mutation(self.TARGET_TASK_ID)

    def test_rejects_unapproved_or_malformed_target_status_without_mutation(self):
        invalid_target_markdown = {
            "draft": "# Target Task\n\n## Status\n\nDRAFT\n",
            "planned": "# Target Task\n\n## Status\n\nPLANNED\n",
            "complete": "# Target Task\n\n## Status\n\nCOMPLETE\n",
            "complete_verified": "# Target Task\n\n## Status\n\nCOMPLETE - VERIFIED\n",
            "missing_heading": "# Target Task\n\n## Goal\n\nNo status heading.\n",
            "missing_value": "# Target Task\n\n## Status\n\n## Goal\n\nNo status value.\n",
            "duplicate_heading": (
                "# Target Task\n\n## Status\n\n"
                "APPROVED - READY FOR CONTRACT BASELINE\n\n"
                "## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n"
            ),
            "malformed_value": (
                "# Target Task\n\n## Status\n\n"
                "APPROVED - READY FOR CONTRACT BASELINE - EXTRA\n"
            ),
        }

        for case, task_markdown in invalid_target_markdown.items():
            with self.subTest(case=case):
                self._write_status(
                    f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234"
                )
                self._target_task_path().write_text(task_markdown, encoding="utf-8")
                self._assert_start_rejected_without_mutation(self.TARGET_TASK_ID)

    def test_exact_complete_current_and_approved_target_start_normally(self):
        completed_current = (
            f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234"
        )
        self._write_status(completed_current)
        subprocess.run(
            ["git", "add", "STATUS.md"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "clean completed lifecycle fixture"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )
        expected_baseline = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        current_task_before = self.current_task_path.read_bytes()
        target_task_before = self._target_task_path().read_bytes()

        result = self._run_start(self.TARGET_TASK_ID)

        self.assertEqual(result.returncode, 0, result.stderr)
        status = self.status_path.read_text(encoding="utf-8")
        self.assertIn(f"Current Task: {self.TARGET_TASK_ID} - ACTIVE", status)
        self.assertIn(f"Previous Task: {completed_current}", status)
        self.assertIn("Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED", status)
        self.assertIn(f"Task Baseline: {expected_baseline}", status)
        self.assertEqual(self.current_task_path.read_bytes(), current_task_before)
        self.assertEqual(self._target_task_path().read_bytes(), target_task_before)

    def test_duplicate_current_lifecycle_field_still_fails_without_mutation(self):
        self._write_status(
            f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234"
        )
        duplicate = self.status_path.read_text(encoding="utf-8") + (
            "Current Task: QH-V2-DUPLICATE-999 - ACTIVE\n"
        )
        self.status_path.write_text(duplicate, encoding="utf-8")

        self._assert_start_rejected_without_mutation(self.TARGET_TASK_ID)

    def test_missing_target_still_fails_without_mutation(self):
        self._write_status(
            f"{self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234"
        )
        self._assert_start_rejected_without_mutation("QH-V2-MISSING-999")


class QhCleanWorktreeLifecycleTests(unittest.TestCase):
    CURRENT_TASK_ID = "QH-V2-CURRENT-001"
    TARGET_TASK_ID = "QH-V2-TARGET-002"

    @classmethod
    def setUpClass(cls):
        cls.seed = GitSeedRepository(
            {
                ".gitignore": "ignored.tmp\n",
                "seed.txt": "seed\n",
                f"tasks/{cls.CURRENT_TASK_ID}.md": (
                    "# Current Task\n\n## Status\n\nCOMPLETE - VERIFIED\n"
                ),
                f"tasks/{cls.TARGET_TASK_ID}.md": (
                    "# Target Task\n\n## Status\n\n"
                    "APPROVED - READY FOR CONTRACT BASELINE\n"
                ),
                "STATUS.md": (
                    f"Current Task: {cls.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit abc1234\n\n"
                    "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
                    f"Next Planned Task: {cls.TARGET_TASK_ID} - PLANNED\n"
                ),
            },
            user_email="test@example.com",
            user_name="Test User",
        )

    @classmethod
    def tearDownClass(cls):
        cls.seed.cleanup()

    def setUp(self):
        self._repo_copy = self.seed.new_copy()
        self.repo = self._repo_copy.path

    def tearDown(self):
        self._repo_copy.cleanup()

    @property
    def status_path(self):
        return self.repo / "STATUS.md"

    @property
    def current_task_path(self):
        return self.repo / "tasks" / f"{self.CURRENT_TASK_ID}.md"

    @property
    def target_task_path(self):
        return self.repo / "tasks" / f"{self.TARGET_TASK_ID}.md"

    def _git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )

    def _run_qh(self, *args):
        return subprocess.run(
            [sys.executable, str(QH), *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _start_bytes(self):
        return (
            self.status_path.read_bytes(),
            self.current_task_path.read_bytes(),
            self.target_task_path.read_bytes(),
        )

    def _close_bytes(self):
        return (
            self.status_path.read_bytes(),
            self.current_task_path.read_bytes(),
        )

    def _assert_start_rejected_without_mutation(self):
        before = self._start_bytes()
        result = self._run_qh("start", self.TARGET_TASK_ID)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self._start_bytes(), before)

    def _prepare_active_close(self, verification_command='python -c "print(1)"'):
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        self.status_path.write_text(
            f"Current Task: {self.CURRENT_TASK_ID} - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            f"Next Planned Task: {self.TARGET_TASK_ID} - PLANNED\n"
            f"Task Baseline: {baseline}\n",
            encoding="utf-8",
        )
        self.current_task_path.write_text(
            "# Current Task\n\n"
            "## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n"
            "- `STATUS.md`\n"
            f"- `tasks/{self.CURRENT_TASK_ID}.md`\n"
            "- `seed.txt`\n"
            "- `generated.txt`\n"
            "- `verification_ran.txt`\n"
            "- `head.txt`\n\n"
            "## Forbidden Changes\n\n"
            "- `forbidden.txt`\n\n"
            "## Verification\n\n"
            "Run exactly:\n\n"
            f"`{verification_command}`\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "active close fixture")
        return self._git("rev-parse", "HEAD").stdout.strip(), baseline

    def test_start_rejects_unstaged_dirty_state_without_lifecycle_mutation(self):
        (self.repo / "seed.txt").write_text("unstaged\n", encoding="utf-8")
        self._assert_start_rejected_without_mutation()

    def test_start_rejects_staged_dirty_state_without_lifecycle_mutation(self):
        (self.repo / "seed.txt").write_text("staged\n", encoding="utf-8")
        self._git("add", "seed.txt")
        self._assert_start_rejected_without_mutation()

    def test_start_rejects_deleted_tracked_state_without_lifecycle_mutation(self):
        (self.repo / "seed.txt").unlink()
        self._assert_start_rejected_without_mutation()

    def test_start_rejects_nonignored_untracked_state_without_lifecycle_mutation(self):
        (self.repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")
        self._assert_start_rejected_without_mutation()

    def test_start_preserves_ignored_artifact_semantics(self):
        (self.repo / "ignored.tmp").write_text("ignored\n", encoding="utf-8")
        self.assertEqual(self._git("status", "--porcelain").stdout, "")
        result = self._run_qh("start", self.TARGET_TASK_ID)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_close_rejects_non_head_commit_before_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('verification_ran.txt').write_text('ran', encoding='utf-8')\""
        )
        head, baseline = self._prepare_active_close(command)
        self.assertNotEqual(head, baseline)
        before = self._close_bytes()

        result = self._run_qh("close", baseline)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / "verification_ran.txt").exists())
        self.assertEqual(self._close_bytes(), before)

    def test_close_rejects_dirty_entry_before_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('verification_ran.txt').write_text('ran', encoding='utf-8')\""
        )
        head, _ = self._prepare_active_close(command)
        (self.repo / "seed.txt").write_text("dirty\n", encoding="utf-8")
        before = self._close_bytes()

        result = self._run_qh("close", head)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / "verification_ran.txt").exists())
        self.assertEqual(self._close_bytes(), before)

    def test_close_rejects_verification_created_dirt_without_lifecycle_write(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('generated.txt').write_text('dirty', encoding='utf-8')\""
        )
        head, _ = self._prepare_active_close(command)
        before = self._close_bytes()

        result = self._run_qh("close", head)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.repo / "generated.txt").exists())
        self.assertEqual(self._close_bytes(), before)

    def test_close_rejects_verification_head_change_without_lifecycle_write(self):
        command = (
            'python -c "import subprocess; from pathlib import Path; '
            "Path('head.txt').write_text('changed', encoding='utf-8'); "
            "subprocess.run(['git','add','head.txt'], check=True); "
            "subprocess.run(['git','commit','-m','move-head'], check=True)\""
        )
        head, _ = self._prepare_active_close(command)
        before = self._close_bytes()

        result = self._run_qh("close", head)

        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self._git("rev-parse", "HEAD").stdout.strip(), head)
        self.assertEqual(self._close_bytes(), before)

    def test_clean_normal_start_remains_compatible(self):
        result = self._run_qh("start", self.TARGET_TASK_ID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"Current Task: {self.TARGET_TASK_ID} - ACTIVE",
            self.status_path.read_text(encoding="utf-8"),
        )

    def test_clean_normal_close_remains_compatible(self):
        head, _ = self._prepare_active_close()
        result = self._run_qh("close", head)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"Current Task: {self.CURRENT_TASK_ID} - COMPLETE - VERIFIED - commit {head}",
            self.status_path.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "## Status\n\nCOMPLETE - VERIFIED",
            self.current_task_path.read_text(encoding="utf-8"),
        )

    def test_review_remains_usable_for_dirty_intermediate_diagnostics(self):
        self._prepare_active_close()
        (self.repo / "seed.txt").write_text("dirty but allowed\n", encoding="utf-8")
        before = self._close_bytes()

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Final Gate: PASS", result.stdout)
        self.assertEqual(self._close_bytes(), before)


class QhPostVerificationEvidenceRefreshTests(unittest.TestCase):
    TASK_ID = "QH-V2-EVIDENCE-001"

    @classmethod
    def setUpClass(cls):
        cls.seed = GitSeedRepository(
            {},
            user_email="test@example.com",
            user_name="Test User",
        )

    @classmethod
    def tearDownClass(cls):
        cls.seed.cleanup()

    def setUp(self):
        self._repo_copy = self.seed.new_copy()
        self.repo = self._repo_copy.path
        (self.repo / "tasks").mkdir()

    def tearDown(self):
        self._repo_copy.cleanup()

    @property
    def status_path(self):
        return self.repo / "STATUS.md"

    @property
    def task_path(self):
        return self.repo / "tasks" / f"{self.TASK_ID}.md"

    def _git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )

    def _run_qh(self, *args):
        return subprocess.run(
            [sys.executable, str(QH), *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _prepare(self, verification_command):
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        (self.repo / "forbidden_existing.txt").write_text(
            "original\n",
            encoding="utf-8",
        )
        self.status_path.write_text(
            f"Current Task: {self.TASK_ID} - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n",
            encoding="utf-8",
        )
        self.task_path.write_text(
            "# Evidence Refresh Fixture\n\n"
            "## Status\n\nACTIVE\n\n"
            "## Allowed Changes\n\n"
            "- `STATUS.md`\n"
            f"- `tasks/{self.TASK_ID}.md`\n"
            "- `seed.txt`\n"
            "- `allowed_generated.txt`\n"
            "- `counter.txt`\n\n"
            "## Forbidden Changes\n\n"
            "- `forbidden_generated.txt`\n"
            "- `forbidden_existing.txt`\n\n"
            "## Verification\n\n"
            "Run exactly:\n\n"
            f"`{verification_command}`\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "evidence refresh baseline")
        baseline = self._git("rev-parse", "HEAD").stdout.strip()
        self.status_path.write_text(
            self.status_path.read_text(encoding="utf-8").rstrip("\n")
            + f"\nTask Baseline: {baseline}\n",
            encoding="utf-8",
        )
        self._git("add", "STATUS.md")
        self._git("commit", "-m", "persist evidence refresh baseline")
        return self._git("rev-parse", "HEAD").stdout.strip()

    def _lifecycle_bytes(self):
        return self.status_path.read_bytes(), self.task_path.read_bytes()

    def test_review_detects_forbidden_untracked_created_by_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('forbidden_generated.txt').write_text('bad', encoding='utf-8')\""
        )
        self._prepare(command)

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("forbidden_generated.txt: forbidden", result.stdout)
        self.assertIn("Unexpected Changed Paths: yes", result.stdout)
        self.assertIn("Final Gate: FAIL", result.stdout)

    def test_review_reports_allowed_path_created_by_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('allowed_generated.txt').write_text('ok', encoding='utf-8')\""
        )
        self._prepare(command)

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("allowed_generated.txt: allowed", result.stdout)
        self.assertIn("Unexpected Changed Paths: no", result.stdout)
        self.assertIn("Final Gate: PASS", result.stdout)

    def test_review_detects_forbidden_modification_by_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('forbidden_existing.txt').write_text('changed', encoding='utf-8')\""
        )
        self._prepare(command)

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("forbidden_existing.txt: forbidden", result.stdout)
        self.assertIn("Final Gate: FAIL", result.stdout)

    def test_review_detects_forbidden_deletion_by_verification(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('forbidden_existing.txt').unlink()\""
        )
        self._prepare(command)

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("forbidden_existing.txt: forbidden", result.stdout)
        self.assertIn("Final Gate: FAIL", result.stdout)

    def test_verification_runs_once_before_evidence_refresh(self):
        command = (
            'python -c "from pathlib import Path; p=Path(\'counter.txt\'); '
            "p.write_text(p.read_text(encoding='utf-8') + 'x' if p.exists() else 'x', encoding='utf-8')\""
        )
        self._prepare(command)

        result = self._run_qh("review")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.repo / "counter.txt").read_text(encoding="utf-8"), "x")
        self.assertIn("counter.txt: allowed", result.stdout)
        self.assertEqual(result.stdout.count(command + ": exit 0"), 1)

    def test_close_refreshed_evidence_failure_preserves_lifecycle_bytes(self):
        command = (
            'python -c "from pathlib import Path; '
            "Path('forbidden_generated.txt').write_text('bad', encoding='utf-8')\""
        )
        head = self._prepare(command)
        before = self._lifecycle_bytes()

        result = self._run_qh("close", head)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden_generated.txt: forbidden", result.stdout)
        self.assertIn("Final Gate: FAIL", result.stdout)
        self.assertEqual(self._lifecycle_bytes(), before)


if __name__ == "__main__":
    unittest.main()


class QhUnsuccessfulLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        (self.repo / "tasks").mkdir()
        (self.repo / "docs").mkdir()
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )

    def _run_qh(self, *args):
        return subprocess.run(
            [sys.executable, str(QH), *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_close_unsuccessful_records_terminal_state_and_evidence_without_final_gate_pass(self):
        status_path = self.repo / "STATUS.md"
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        evidence_path = self.repo / "docs" / "failure.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n",
            encoding="utf-8",
        )
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n",
            encoding="utf-8",
        )
        evidence_path.write_text("objective failure evidence\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "unsuccessful close baseline")

        result = self._run_qh("close-unsuccessful", "docs/failure.md")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Final Gate: PASS", result.stdout)
        status = status_path.read_text(encoding="utf-8")
        self.assertIn(
            "Current Task: QH-V2-TEST-001 - CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED - evidence docs/failure.md",
            status,
        )
        self.assertIn(
            "## Status\n\nCLOSED - UNSUCCESSFUL - EVIDENCE RECORDED",
            task_path.read_text(encoding="utf-8"),
        )

    def test_start_accepts_evidence_backed_unsuccessful_predecessor(self):
        status_path = self.repo / "STATUS.md"
        evidence_path = self.repo / "docs" / "failure.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED - evidence docs/failure.md\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        (self.repo / "tasks" / "QH-V2-TEST-001.md").write_text(
            "# Test Task\n\n## Status\n\nCLOSED - UNSUCCESSFUL - EVIDENCE RECORDED\n",
            encoding="utf-8",
        )
        (self.repo / "tasks" / "QH-V2-TEST-002.md").write_text(
            "# Next Task\n\n## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        evidence_path.write_text("objective failure evidence\n", encoding="utf-8")
        self._git("add", ".")
        self._git("commit", "-m", "unsuccessful predecessor baseline")

        result = self._run_qh("start", "QH-V2-TEST-002")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        status = status_path.read_text(encoding="utf-8")
        self.assertIn("Current Task: QH-V2-TEST-002 - ACTIVE", status)
        self.assertIn(
            "Previous Task: QH-V2-TEST-001 - CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED - evidence docs/failure.md",
            status,
        )

    def _prepare_unsuccessful_close_fixture(self):
        status_path = self.repo / "STATUS.md"
        task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - ACTIVE\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n",
            encoding="utf-8",
        )
        task_path.write_text(
            "# Test Task\n\n## Status\n\nACTIVE\n",
            encoding="utf-8",
        )
        (self.repo / "docs" / "failure.md").write_text(
            "objective failure evidence\n",
            encoding="utf-8",
        )
        (self.repo / "docs" / "directory").mkdir()
        (self.repo / "docs" / "directory" / "inside.txt").write_text(
            "tracked directory child\n",
            encoding="utf-8",
        )
        (self.repo / ".gitignore").write_text(
            "docs/untracked.md\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "unsuccessful hardening fixture")
        return status_path, task_path

    def _lifecycle_bytes(self, status_path, task_path):
        return status_path.read_bytes(), task_path.read_bytes()

    def _assert_unsuccessful_close_rejected_without_mutation(
        self,
        evidence_arg,
        status_path,
        task_path,
    ):
        before = self._lifecycle_bytes(status_path, task_path)
        result = self._run_qh("close-unsuccessful", evidence_arg)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self._lifecycle_bytes(status_path, task_path), before)

    def test_close_unsuccessful_rejects_invalid_evidence_paths_without_mutation(self):
        status_path, task_path = self._prepare_unsuccessful_close_fixture()
        ignored_untracked = self.repo / "docs" / "untracked.md"
        ignored_untracked.write_text("not in HEAD\n", encoding="utf-8")
        self.assertEqual(self._git("status", "--porcelain").stdout, "")

        invalid_paths = (
            "docs/missing.md",
            str((self.repo / "docs" / "failure.md").resolve()),
            "../outside.md",
            "docs/directory",
            "docs/untracked.md",
        )
        for evidence_arg in invalid_paths:
            with self.subTest(evidence_arg=evidence_arg):
                self._assert_unsuccessful_close_rejected_without_mutation(
                    evidence_arg,
                    status_path,
                    task_path,
                )

    def test_close_unsuccessful_rejects_lifecycle_control_evidence_without_mutation(self):
        status_path, task_path = self._prepare_unsuccessful_close_fixture()
        for evidence_arg in (
            "STATUS.md",
            "tasks/QH-V2-TEST-001.md",
        ):
            with self.subTest(evidence_arg=evidence_arg):
                self._assert_unsuccessful_close_rejected_without_mutation(
                    evidence_arg,
                    status_path,
                    task_path,
                )

    def test_close_unsuccessful_rejects_dirty_worktree_without_mutation(self):
        status_path, task_path = self._prepare_unsuccessful_close_fixture()
        (self.repo / "docs" / "failure.md").write_text(
            "dirty evidence\n",
            encoding="utf-8",
        )
        self._assert_unsuccessful_close_rejected_without_mutation(
            "docs/failure.md",
            status_path,
            task_path,
        )

    def _prepare_unsuccessful_start_fixture(self, evidence_arg):
        status_path = self.repo / "STATUS.md"
        current_task_path = self.repo / "tasks" / "QH-V2-TEST-001.md"
        target_task_path = self.repo / "tasks" / "QH-V2-TEST-002.md"
        status_path.write_text(
            "Current Task: QH-V2-TEST-001 - CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED "
            f"- evidence {evidence_arg}\n\n"
            "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit def5678\n\n"
            "Next Planned Task: QH-V2-TEST-002 - NOT STARTED\n",
            encoding="utf-8",
        )
        current_task_path.write_text(
            "# Test Task\n\n## Status\n\nCLOSED - UNSUCCESSFUL - EVIDENCE RECORDED\n",
            encoding="utf-8",
        )
        target_task_path.write_text(
            "# Next Task\n\n## Status\n\nAPPROVED - READY FOR CONTRACT BASELINE\n",
            encoding="utf-8",
        )
        if evidence_arg == "docs/failure.md":
            (self.repo / "docs" / "failure.md").write_text(
                "objective failure evidence\n",
                encoding="utf-8",
            )
        self._git("add", ".")
        self._git("commit", "-m", "unsuccessful start hardening fixture")
        return status_path, current_task_path, target_task_path

    def _assert_start_rejected_without_lifecycle_mutation(self, evidence_arg):
        status_path, current_task_path, target_task_path = (
            self._prepare_unsuccessful_start_fixture(evidence_arg)
        )
        before = (
            status_path.read_bytes(),
            current_task_path.read_bytes(),
            target_task_path.read_bytes(),
        )
        result = self._run_qh("start", "QH-V2-TEST-002")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            (
                status_path.read_bytes(),
                current_task_path.read_bytes(),
                target_task_path.read_bytes(),
            ),
            before,
        )

    def test_start_rejects_missing_unsuccessful_evidence_without_mutation(self):
        self._assert_start_rejected_without_lifecycle_mutation("docs/missing.md")

    def test_start_rejects_lifecycle_control_as_unsuccessful_evidence_without_mutation(self):
        self._assert_start_rejected_without_lifecycle_mutation("STATUS.md")


class HandoffCheckTests(unittest.TestCase):
    HANDOFF_REF = "refs/remotes/origin/handoff"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")
        (self.repo / "seed.txt").write_text("seed\n", encoding="utf-8")
        self._git("add", "seed.txt")
        self._git("commit", "-m", "baseline")
        self.baseline = self._git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.tmp.cleanup()

    def _git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )

    def _run_check(self):
        return subprocess.run(
            [sys.executable, str(QH), "handoff-check", "origin/handoff"],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _snapshot(self):
        return (
            self._git("rev-parse", "HEAD").stdout,
            self._git("status", "--porcelain=v1").stdout,
            self._git("for-each-ref", "--format=%(refname):%(objectname)").stdout,
        )

    def _assert_read_only(self, expected_code=None):
        before = self._snapshot()
        result = self._run_check()
        after = self._snapshot()
        self.assertEqual(after, before)
        if expected_code is not None:
            self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        return result

    def _prepare_single_handoff(self):
        (self.repo / "handoff.txt").write_text("handoff\n", encoding="utf-8")
        self._git("add", "handoff.txt")
        self._git("commit", "-m", "atomic handoff")
        handoff = self._git("rev-parse", "HEAD").stdout.strip()
        self._git("update-ref", self.HANDOFF_REF, handoff)
        self._git("reset", "--hard", self.baseline)
        return handoff

    def test_fast_forward_safe_reports_exact_parent_and_changed_path_without_mutation(self):
        handoff = self._prepare_single_handoff()

        result = self._assert_read_only(expected_code=0)

        self.assertIn(f"Local HEAD: {self.baseline}", result.stdout)
        self.assertIn(f"Handoff Commit: {handoff}", result.stdout)
        self.assertIn(f"Handoff Parent: {self.baseline}", result.stdout)
        self.assertIn("- handoff.txt", result.stdout)
        self.assertIn("Classification: FAST_FORWARD_SAFE", result.stdout)

    def test_already_applied_exact_is_distinct_and_read_only(self):
        handoff = self._prepare_single_handoff()
        self._git("reset", "--hard", handoff)

        result = self._assert_read_only(expected_code=0)

        self.assertIn("Classification: ALREADY_APPLIED_EXACT", result.stdout)

    def test_already_contained_is_distinct_and_read_only(self):
        handoff = self._prepare_single_handoff()
        self._git("reset", "--hard", handoff)
        (self.repo / "later.txt").write_text("later\n", encoding="utf-8")
        self._git("add", "later.txt")
        self._git("commit", "-m", "local descendant")

        result = self._assert_read_only(expected_code=0)

        self.assertIn("Classification: ALREADY_CONTAINED", result.stdout)

    def test_dirty_worktree_stops_without_mutation(self):
        self._prepare_single_handoff()
        (self.repo / "seed.txt").write_text("dirty\n", encoding="utf-8")

        result = self._assert_read_only(expected_code=1)

        self.assertIn("Worktree: dirty", result.stdout)
        self.assertIn("Classification: STOP_DIRTY", result.stdout)

    def test_diverged_history_stops_without_mutation(self):
        self._prepare_single_handoff()
        (self.repo / "local.txt").write_text("local\n", encoding="utf-8")
        self._git("add", "local.txt")
        self._git("commit", "-m", "diverged local commit")

        result = self._assert_read_only(expected_code=1)

        self.assertIn("Classification: STOP_NON_ATOMIC_OR_DIVERGED", result.stdout)

    def test_multi_commit_handoff_stops_without_mutation(self):
        (self.repo / "one.txt").write_text("one\n", encoding="utf-8")
        self._git("add", "one.txt")
        self._git("commit", "-m", "handoff part one")
        (self.repo / "two.txt").write_text("two\n", encoding="utf-8")
        self._git("add", "two.txt")
        self._git("commit", "-m", "handoff part two")
        handoff = self._git("rev-parse", "HEAD").stdout.strip()
        self._git("update-ref", self.HANDOFF_REF, handoff)
        self._git("reset", "--hard", self.baseline)

        result = self._assert_read_only(expected_code=1)

        self.assertIn("Classification: STOP_NON_ATOMIC_OR_DIVERGED", result.stdout)

    def test_merge_commit_handoff_stops_without_mutation(self):
        self._git("checkout", "-b", "left", self.baseline)
        (self.repo / "left.txt").write_text("left\n", encoding="utf-8")
        self._git("add", "left.txt")
        self._git("commit", "-m", "left")
        self._git("checkout", "-b", "right", self.baseline)
        (self.repo / "right.txt").write_text("right\n", encoding="utf-8")
        self._git("add", "right.txt")
        self._git("commit", "-m", "right")
        self._git("merge", "--no-ff", "left", "-m", "merge handoff")
        merge_commit = self._git("rev-parse", "HEAD").stdout.strip()
        self._git("update-ref", self.HANDOFF_REF, merge_commit)
        self._git("reset", "--hard", self.baseline)

        result = self._assert_read_only(expected_code=1)

        self.assertIn("Handoff Parent: MULTIPLE ", result.stdout)
        self.assertIn("Classification: STOP_NON_ATOMIC_OR_DIVERGED", result.stdout)
