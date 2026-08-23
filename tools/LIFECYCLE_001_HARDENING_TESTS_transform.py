from pathlib import Path

path = Path("tests/test_qh.py")
text = path.read_text(encoding="utf-8")
marker = "    def _prepare_unsuccessful_close_fixture(self):\n"
if marker in text:
    raise SystemExit("hardening tests already present")

addition = r'''

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
'''

path.write_text(text.rstrip("\n") + addition + "\n", encoding="utf-8", newline="\n")
print("updated tests/test_qh.py with hardening cases")
