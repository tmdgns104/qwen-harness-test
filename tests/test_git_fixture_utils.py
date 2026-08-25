from __future__ import annotations

import unittest

from tests.git_fixture_utils import GitSeedRepository, run_git


class GitSeedRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.seed = GitSeedRepository(
            {
                ".gitignore": "ignored.tmp\n",
                "tracked.txt": "base\n",
                "delete.txt": "delete\n",
                "rename.txt": "rename\n",
            },
            user_email="perf005@example.test",
            user_name="PERF-005 Test",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.seed.cleanup()

    def test_empty_seed_repository_supports_independent_clean_copies(self) -> None:
        seed = GitSeedRepository(
            {},
            user_email="perf005-empty@example.test",
            user_name="PERF-005 Empty Seed",
        )
        try:
            first = seed.new_copy()
            second = seed.new_copy()
            try:
                self.assertEqual(run_git(first.path, "status", "--porcelain"), "")
                self.assertEqual(run_git(second.path, "status", "--porcelain"), "")
                self.assertEqual(
                    run_git(first.path, "rev-parse", "HEAD"),
                    run_git(second.path, "rev-parse", "HEAD"),
                )
                (first.path / "only-first.txt").write_text("first\n", encoding="utf-8")
                self.assertNotEqual(run_git(first.path, "status", "--porcelain"), "")
                self.assertEqual(run_git(second.path, "status", "--porcelain"), "")
                self.assertFalse((second.path / "only-first.txt").exists())
            finally:
                first.cleanup()
                second.cleanup()
        finally:
            seed.cleanup()

    def test_copies_are_clean_and_use_independent_git_directories(self) -> None:
        first = self.seed.new_copy()
        second = self.seed.new_copy()
        try:
            self.assertEqual(run_git(first.path, "status", "--porcelain"), "")
            self.assertEqual(run_git(second.path, "status", "--porcelain"), "")
            self.assertNotEqual((first.path / ".git").resolve(), (second.path / ".git").resolve())
            self.assertEqual(
                run_git(first.path, "rev-parse", "HEAD"),
                run_git(second.path, "rev-parse", "HEAD"),
            )
        finally:
            first.cleanup()
            second.cleanup()

    def test_worktree_index_untracked_ignored_delete_and_rename_state_do_not_leak(self) -> None:
        mutated = self.seed.new_copy()
        fresh = self.seed.new_copy()
        try:
            (mutated.path / "tracked.txt").write_text("changed\n", encoding="utf-8")
            run_git(mutated.path, "add", "tracked.txt")
            (mutated.path / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            (mutated.path / "ignored.tmp").write_text("ignored\n", encoding="utf-8")
            run_git(mutated.path, "rm", "-q", "delete.txt")
            run_git(mutated.path, "mv", "rename.txt", "renamed.txt")

            self.assertNotEqual(run_git(mutated.path, "status", "--porcelain"), "")
            self.assertEqual(run_git(fresh.path, "status", "--porcelain"), "")
            self.assertEqual((fresh.path / "tracked.txt").read_text(encoding="utf-8"), "base\n")
            self.assertTrue((fresh.path / "delete.txt").is_file())
            self.assertTrue((fresh.path / "rename.txt").is_file())
            self.assertFalse((fresh.path / "renamed.txt").exists())
            self.assertFalse((fresh.path / "untracked.txt").exists())
            self.assertFalse((fresh.path / "ignored.tmp").exists())
        finally:
            mutated.cleanup()
            fresh.cleanup()

    def test_new_commit_changes_only_one_copy_head(self) -> None:
        mutated = self.seed.new_copy()
        fresh = self.seed.new_copy()
        try:
            original_head = run_git(fresh.path, "rev-parse", "HEAD")
            (mutated.path / "tracked.txt").write_text("committed\n", encoding="utf-8")
            run_git(mutated.path, "add", "tracked.txt")
            run_git(mutated.path, "commit", "-q", "-m", "independent commit")

            self.assertNotEqual(run_git(mutated.path, "rev-parse", "HEAD"), original_head)
            self.assertEqual(run_git(fresh.path, "rev-parse", "HEAD"), original_head)
            self.assertEqual(run_git(fresh.path, "status", "--porcelain"), "")
        finally:
            mutated.cleanup()
            fresh.cleanup()

    def test_branch_ref_and_merge_history_do_not_leak_between_scenario_copies(self) -> None:
        scenario = GitSeedRepository(
            {"base.txt": "base\n"},
            user_email="perf007@example.test",
            user_name="PERF-007 Test",
        )
        try:
            baseline = run_git(scenario.path, "rev-parse", "HEAD")
            run_git(scenario.path, "checkout", "-b", "left", baseline)
            (scenario.path / "left.txt").write_text("left\n", encoding="utf-8")
            run_git(scenario.path, "add", "left.txt")
            run_git(scenario.path, "commit", "-q", "-m", "left")
            run_git(scenario.path, "checkout", "-b", "right", baseline)
            (scenario.path / "right.txt").write_text("right\n", encoding="utf-8")
            run_git(scenario.path, "add", "right.txt")
            run_git(scenario.path, "commit", "-q", "-m", "right")
            run_git(scenario.path, "merge", "--no-ff", "left", "-m", "merge")
            merge_head = run_git(scenario.path, "rev-parse", "HEAD")
            handoff_ref = "refs/remotes/origin/handoff-merge"
            run_git(scenario.path, "update-ref", handoff_ref, merge_head)
            run_git(scenario.path, "reset", "--hard", baseline)

            mutated = scenario.new_copy()
            fresh = scenario.new_copy()
            try:
                run_git(mutated.path, "reset", "--hard", merge_head)
                run_git(mutated.path, "update-ref", handoff_ref, baseline)
                run_git(mutated.path, "checkout", "-b", "local-only", baseline)

                self.assertEqual(run_git(fresh.path, "rev-parse", "HEAD"), baseline)
                self.assertEqual(
                    run_git(fresh.path, "rev-parse", handoff_ref),
                    merge_head,
                )
                self.assertEqual(run_git(fresh.path, "branch", "--list", "local-only"), "")
                merge_parents = run_git(
                    fresh.path,
                    "rev-list",
                    "--parents",
                    "-n",
                    "1",
                    merge_head,
                ).split()
                self.assertEqual(len(merge_parents), 3)
                self.assertEqual(run_git(fresh.path, "status", "--porcelain"), "")
            finally:
                mutated.cleanup()
                fresh.cleanup()
        finally:
            scenario.cleanup()


if __name__ == "__main__":
    unittest.main()
