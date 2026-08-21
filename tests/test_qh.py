import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


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
        current_task_before = self.current_task_path.read_bytes()
        target_task_before = self._target_task_path().read_bytes()

        result = self._run_start(self.TARGET_TASK_ID)

        self.assertEqual(result.returncode, 0, result.stderr)
        status = self.status_path.read_text(encoding="utf-8")
        self.assertIn(f"Current Task: {self.TARGET_TASK_ID} - ACTIVE", status)
        self.assertIn(f"Previous Task: {completed_current}", status)
        self.assertIn("Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED", status)
        self.assertIn(f"Task Baseline: {self.seed_head}", status)
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


if __name__ == "__main__":
    unittest.main()
