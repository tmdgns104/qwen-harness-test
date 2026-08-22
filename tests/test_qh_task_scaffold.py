from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.harness_core import parse_change_scope, parse_verification_commands


ROOT = Path(__file__).resolve().parents[1]
QH = ROOT / "tools" / "qh.py"
QUICKSTART = ROOT / "docs" / "QUICKSTART.md"


REQUIRED_HEADINGS = [
    "## Status",
    "## Problem",
    "## Goal",
    "## Architecture Basis",
    "## Dependencies",
    "## Scope",
    "## Allowed Changes",
    "## Forbidden Changes",
    "## Acceptance Criteria",
    "## Verification",
    "## Evidence Requirements",
    "## Stop Conditions",
    "## Next Task",
]


class QhTaskScaffoldTests(unittest.TestCase):
    def _run(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(QH), *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

    def _create_draft(self, repo: Path, task_id: str = "QH-V2-DEMO-001") -> Path:
        (repo / "tasks").mkdir(exist_ok=True)
        result = self._run(repo, "task-new", task_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return repo / "tasks" / f"{task_id}.md"

    def test_valid_task_id_creates_unapproved_draft_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            task_path = self._create_draft(repo)

            self.assertTrue(task_path.is_file())
            markdown = task_path.read_text(encoding="utf-8")
            self.assertIn("## Status\n\nDRAFT - HUMAN REVIEW REQUIRED", markdown)
            self.assertEqual(
                sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file()),
                ["tasks/QH-V2-DEMO-001.md"],
            )

    def test_draft_has_required_sections_in_stable_order_and_bytes(self) -> None:
        payloads = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                task_path = self._create_draft(repo)
                payloads.append(task_path.read_bytes())
                headings = [
                    line
                    for line in task_path.read_text(encoding="utf-8").splitlines()
                    if line.startswith("## ")
                ]
                self.assertEqual(headings, REQUIRED_HEADINGS)
                self.assertNotIn(b"\r\n", payloads[-1])
        self.assertEqual(payloads[0], payloads[1])

    def test_untouched_draft_fails_closed_in_scope_and_verification_parsers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            markdown = self._create_draft(repo).read_text(encoding="utf-8")

            with self.assertRaises(ValueError):
                parse_change_scope(markdown)
            with self.assertRaises(ValueError):
                parse_verification_commands(markdown)

    def test_invalid_traversal_and_existing_targets_leave_existing_bytes_unchanged(self) -> None:
        invalid_ids = ("../ESCAPE", "QH/V2", r"QH\V2", ".", "-BAD", "")
        for task_id in invalid_ids:
            with self.subTest(task_id=task_id), tempfile.TemporaryDirectory() as tmp:
                repo = Path(tmp)
                tasks = repo / "tasks"
                tasks.mkdir()
                sentinel = repo / "STATUS.md"
                sentinel.write_bytes(b"sentinel\n")
                before = sentinel.read_bytes()

                result = self._run(repo, "task-new", task_id)

                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(sentinel.read_bytes(), before)
                self.assertEqual(list(tasks.iterdir()), [])

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            tasks = repo / "tasks"
            tasks.mkdir()
            target = tasks / "QH-V2-DEMO-001.md"
            target.write_bytes(b"keep-me\n")
            status = repo / "STATUS.md"
            status.write_bytes(b"status-stays\n")
            before_target = target.read_bytes()
            before_status = status.read_bytes()

            result = self._run(repo, "task-new", "QH-V2-DEMO-001")

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), before_target)
            self.assertEqual(status.read_bytes(), before_status)

    def test_generated_draft_cannot_be_started_and_lifecycle_bytes_do_not_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            task_path = self._create_draft(repo)
            status = repo / "STATUS.md"
            status.write_text(
                "Current Task: QH-V2-OLD-001 - COMPLETE - VERIFIED - commit deadbeef\n\n"
                "Previous Task: QH-V2-OLDER-001 - COMPLETE - VERIFIED - commit cafebabe\n\n"
                "Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED\n",
                encoding="utf-8",
                newline="\n",
            )
            before_status = status.read_bytes()
            before_task = task_path.read_bytes()

            result = self._run(repo, "start", "QH-V2-DEMO-001")

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(status.read_bytes(), before_status)
            self.assertEqual(task_path.read_bytes(), before_task)

    def test_task_new_does_not_commit_or_modify_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Fixture"], check=True)
            (repo / "tasks").mkdir()
            status = repo / "STATUS.md"
            status.write_bytes(b"status-before\n")
            subprocess.run(["git", "-C", str(repo), "add", "STATUS.md"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "baseline"], check=True)
            before_head = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            before_status = status.read_bytes()

            result = self._run(repo, "task-new", "QH-V2-DEMO-001")

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            after_head = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(after_head, before_head)
            self.assertEqual(status.read_bytes(), before_status)

    def test_quickstart_documents_task_new_human_review_boundary(self) -> None:
        quickstart = QUICKSTART.read_text(encoding="utf-8")
        self.assertIn("task-new", quickstart)
        self.assertIn("DRAFT - HUMAN REVIEW REQUIRED", quickstart)
        self.assertIn("Human", quickstart)
        self.assertIn("start", quickstart)


if __name__ == "__main__":
    unittest.main()
