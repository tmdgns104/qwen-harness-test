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


if __name__ == "__main__":
    unittest.main()
