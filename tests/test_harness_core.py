import unittest

from tools.harness_core import ChangeScope, parse_change_scope


class ParseChangeScopeTests(unittest.TestCase):
    def test_parses_allowed_and_forbidden_sections(self) -> None:
        markdown = """# Task

## Allowed Changes

- `src/app.py`
- `src/utils/**`

## Forbidden Changes

- `tests/**`
- `DECISIONS.md`

## Acceptance Criteria

- something
"""
        self.assertEqual(
            parse_change_scope(markdown),
            ChangeScope(
                allowed=("src/app.py", "src/utils/**"),
                forbidden=("tests/**", "DECISIONS.md"),
            ),
        )

    def test_stops_at_next_level_two_heading(self) -> None:
        markdown = """## Allowed Changes
- `src/app.py`

## Notes
- `must-not-be-parsed.py`

## Forbidden Changes
- `tests/**`

## Verification
- `also-not-a-path.py`
"""
        scope = parse_change_scope(markdown)
        self.assertEqual(scope.allowed, ("src/app.py",))
        self.assertEqual(scope.forbidden, ("tests/**",))

    def test_preserves_order(self) -> None:
        markdown = """## Allowed Changes
- `b.py`
- `a.py`
- `c.py`

## Forbidden Changes
- `z.py`
- `y.py`
"""
        scope = parse_change_scope(markdown)
        self.assertEqual(scope.allowed, ("b.py", "a.py", "c.py"))
        self.assertEqual(scope.forbidden, ("z.py", "y.py"))

    def test_accepts_unquoted_bullet_values(self) -> None:
        markdown = """## Allowed Changes
- src/app.py

## Forbidden Changes
- all other Repository files
"""
        scope = parse_change_scope(markdown)
        self.assertEqual(scope.allowed, ("src/app.py",))
        self.assertEqual(scope.forbidden, ("all other Repository files",))

    def test_trims_outer_whitespace_before_backtick_removal(self) -> None:
        markdown = """## Allowed Changes
-   `src/app.py`   

## Forbidden Changes
-   `tests/**`   
"""
        scope = parse_change_scope(markdown)
        self.assertEqual(scope.allowed, ("src/app.py",))
        self.assertEqual(scope.forbidden, ("tests/**",))

    def test_missing_allowed_section_raises(self) -> None:
        markdown = """## Forbidden Changes
- `tests/**`
"""
        with self.assertRaises(ValueError):
            parse_change_scope(markdown)

    def test_missing_forbidden_section_raises(self) -> None:
        markdown = """## Allowed Changes
- `src/app.py`
"""
        with self.assertRaises(ValueError):
            parse_change_scope(markdown)

    def test_empty_section_raises(self) -> None:
        markdown = """## Allowed Changes

## Forbidden Changes
- `tests/**`
"""
        with self.assertRaises(ValueError):
            parse_change_scope(markdown)


class PathScopeMatcherTests(unittest.TestCase):
    def test_exact_path_match_and_mismatch(self) -> None:
        import tools.harness_core as harness_core
        self.assertTrue(harness_core.path_matches("tools/harness_core.py", "tools/harness_core.py"))
        self.assertFalse(harness_core.path_matches("tools/other.py", "tools/harness_core.py"))

    def test_recursive_direct_and_nested_children(self) -> None:
        import tools.harness_core as harness_core
        self.assertTrue(harness_core.path_matches("src/app.py", "src/**"))
        self.assertTrue(harness_core.path_matches("src/pkg/util.py", "src/**"))

    def test_recursive_pattern_rejects_similar_prefix_and_bare_dir(self) -> None:
        import tools.harness_core as harness_core
        self.assertFalse(harness_core.path_matches("src2/a.py", "src/**"))
        self.assertFalse(harness_core.path_matches("src", "src/**"))

    def test_normalizes_backslashes(self) -> None:
        import tools.harness_core as harness_core
        self.assertTrue(harness_core.path_matches(r"src\pkg\util.py", "src/**"))
        self.assertTrue(harness_core.path_matches("src/app.py", r"src\**"))

    def test_unsupported_wildcard_syntax_does_not_broaden_scope(self) -> None:
        import tools.harness_core as harness_core
        self.assertFalse(harness_core.path_matches("src/app.py", "src/*.py"))
        self.assertFalse(harness_core.path_matches("app.py", "*.py"))

    def test_all_other_repository_files_is_literal(self) -> None:
        import tools.harness_core as harness_core
        self.assertFalse(harness_core.path_matches("README.md", "all other Repository files"))

    def test_forbidden_wins_over_allowed(self) -> None:
        import tools.harness_core as harness_core
        scope = ChangeScope(allowed=("src/**",), forbidden=("src/secret/**",))
        self.assertFalse(harness_core.is_path_allowed("src/secret/key.py", scope))

    def test_allowed_match_returns_true(self) -> None:
        import tools.harness_core as harness_core
        scope = ChangeScope(allowed=("src/**",), forbidden=("tests/**",))
        self.assertTrue(harness_core.is_path_allowed("src/app.py", scope))

    def test_default_deny_when_no_allowed_pattern_matches(self) -> None:
        import tools.harness_core as harness_core
        scope = ChangeScope(allowed=("src/**",), forbidden=())
        self.assertFalse(harness_core.is_path_allowed("README.md", scope))



class GitExecutionAndRootTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tempdir.name)
        self._git("init", "-q")
        self._git("config", "user.email", "hc003a@example.test")
        self._git("config", "user.name", "HC003A Test")
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        self._git("commit", "-q", "-m", "baseline")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _git(self, *args: str) -> str:
        import subprocess

        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _hc(self):
        import tools.harness_core as harness_core
        return harness_core

    def test_actual_git_top_level_is_accepted(self) -> None:
        from pathlib import Path

        hc = self._hc()
        returned = hc._require_git_top_level(str(self.repo))
        self.assertEqual(Path(returned).resolve(), self.repo.resolve())

    def test_valid_worktree_subdirectory_raises_value_error(self) -> None:
        hc = self._hc()
        subdir = self.repo / "subdir"
        subdir.mkdir()
        with self.assertRaises(ValueError):
            hc._require_git_top_level(str(subdir))

    def test_non_repository_directory_raises_runtime_error(self) -> None:
        import tempfile

        hc = self._hc()
        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(RuntimeError):
                hc._require_git_top_level(other)

    def test_unavailable_git_process_creation_raises_runtime_error(self) -> None:
        import os
        from unittest.mock import patch

        hc = self._hc()
        with patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(RuntimeError):
                hc._run_git(str(self.repo), ("rev-parse", "--show-toplevel"))

    def test_windows_slash_spellings_are_equivalent(self) -> None:
        import os
        from pathlib import Path

        if os.name != "nt":
            self.skipTest("Windows path spelling contract")
        hc = self._hc()
        windows_spelling = str(self.repo).replace("/", "\\")
        returned = hc._require_git_top_level(windows_spelling)
        self.assertEqual(Path(returned).resolve(), self.repo.resolve())

    def test_equivalent_dot_path_is_accepted(self) -> None:
        import os
        from pathlib import Path

        hc = self._hc()
        equivalent = str(self.repo) + os.sep + "."
        returned = hc._require_git_top_level(equivalent)
        self.assertEqual(Path(returned).resolve(), self.repo.resolve())

    def test_windows_case_spelling_is_equivalent(self) -> None:
        import os
        from pathlib import Path

        if os.name != "nt":
            self.skipTest("Windows filesystem identity contract")
        hc = self._hc()
        equivalent = str(self.repo).lower()
        returned = hc._require_git_top_level(equivalent)
        self.assertEqual(Path(returned).resolve(), self.repo.resolve())

    def test_run_git_returns_stdout_for_read_only_command(self) -> None:
        hc = self._hc()
        result = hc._run_git(str(self.repo), ("rev-parse", "--show-toplevel"))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip())

    def test_run_git_nonzero_result_raises_runtime_error(self) -> None:
        hc = self._hc()
        with self.assertRaises(RuntimeError):
            hc._run_git(str(self.repo), ("rev-parse", "--verify", "not-a-real-ref"))
class GitBaselineCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tempdir.name)
        self._git("init", "-q")
        self._git("config", "user.email", "hc003b@example.test")
        self._git("config", "user.name", "HC003B Test")
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        (self.repo / "delete.txt").write_text("delete\n", encoding="utf-8")
        self._git("add", "tracked.txt", "delete.txt")
        self._git("commit", "-q", "-m", "baseline")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _git(self, *args: str) -> str:
        import subprocess

        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _hc(self):
        import tools.harness_core as harness_core

        return harness_core

    def test_clean_repository_captures_current_head_and_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError

        hc = self._hc()
        baseline = hc.capture_git_baseline(str(self.repo))

        self.assertEqual(baseline.head, self._git("rev-parse", "HEAD"))
        with self.assertRaises(FrozenInstanceError):
            baseline.head = "changed"

    def test_actual_git_top_level_is_accepted(self) -> None:
        hc = self._hc()

        baseline = hc.capture_git_baseline(str(self.repo))

        self.assertEqual(baseline.head, self._git("rev-parse", "HEAD"))

    def test_valid_worktree_subdirectory_raises_value_error(self) -> None:
        hc = self._hc()
        subdir = self.repo / "subdir"
        subdir.mkdir()

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(subdir))

    def test_non_repository_directory_raises_runtime_error(self) -> None:
        import tempfile

        hc = self._hc()

        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(RuntimeError):
                hc.capture_git_baseline(other)

    def test_unstaged_tracked_modification_rejects_baseline(self) -> None:
        hc = self._hc()
        (self.repo / "tracked.txt").write_text("changed\n", encoding="utf-8")

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))

    def test_staged_tracked_modification_rejects_baseline(self) -> None:
        hc = self._hc()
        (self.repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
        self._git("add", "tracked.txt")

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))

    def test_staged_addition_rejects_baseline(self) -> None:
        hc = self._hc()
        (self.repo / "added.txt").write_text("added\n", encoding="utf-8")
        self._git("add", "added.txt")

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))

    def test_staged_deletion_rejects_baseline(self) -> None:
        hc = self._hc()
        self._git("rm", "-q", "delete.txt")

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))

    def test_untracked_non_ignored_file_rejects_baseline(self) -> None:
        hc = self._hc()
        (self.repo / "untracked.txt").write_text("new\n", encoding="utf-8")

        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))

    def test_untracked_ignored_file_does_not_reject_baseline(self) -> None:
        hc = self._hc()
        (self.repo / ".gitignore").write_text("ignored.tmp\n", encoding="utf-8")
        self._git("add", ".gitignore")
        self._git("commit", "-q", "-m", "ignore rule")
        (self.repo / "ignored.tmp").write_text("ignored\n", encoding="utf-8")

        baseline = hc.capture_git_baseline(str(self.repo))

        self.assertEqual(baseline.head, self._git("rev-parse", "HEAD"))

    def test_required_git_failure_fails_closed(self) -> None:
        import os
        from unittest.mock import patch

        hc = self._hc()

        with patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(RuntimeError):
                hc.capture_git_baseline(str(self.repo))

class GitEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        from pathlib import Path

        self._tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self._tempdir.name)
        self._git("init", "-q")
        self._git("config", "user.email", "hc003@example.test")
        self._git("config", "user.name", "HC003 Test")
        (self.repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        (self.repo / "delete.txt").write_text("delete\n", encoding="utf-8")
        self._git("add", "tracked.txt", "delete.txt")
        self._git("commit", "-q", "-m", "baseline")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _git(self, *args: str) -> str:
        import subprocess

        result = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _hc(self):
        import tools.harness_core as harness_core
        return harness_core

    def test_clean_baseline_captures_head_and_unchanged_is_empty(self) -> None:
        hc = self._hc()
        baseline = hc.capture_git_baseline(str(self.repo))
        self.assertEqual(baseline.head, self._git("rev-parse", "HEAD"))
        self.assertEqual(hc.get_changed_paths(str(self.repo), baseline), ())
        from dataclasses import FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            baseline.head = "changed"

    def test_subdirectory_is_rejected_by_both_public_apis(self) -> None:
        hc = self._hc()
        subdir = self.repo / "subdir"
        subdir.mkdir()
        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(subdir))
        baseline = hc.GitBaseline(head=self._git("rev-parse", "HEAD"))
        with self.assertRaises(ValueError):
            hc.get_changed_paths(str(subdir), baseline)

    def test_dirty_states_reject_baseline(self) -> None:
        hc = self._hc()
        tracked = self.repo / "tracked.txt"
        tracked.write_text("unstaged\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))
        self._git("restore", "tracked.txt")

        tracked.write_text("staged\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))
        self._git("restore", "--staged", "tracked.txt")
        self._git("restore", "tracked.txt")

        (self.repo / "untracked.txt").write_text("new\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            hc.capture_git_baseline(str(self.repo))
        (self.repo / "untracked.txt").unlink()

    def test_ignored_untracked_is_clean_and_tracked_ignore_match_is_evidence(self) -> None:
        hc = self._hc()
        (self.repo / ".gitignore").write_text("ignored.tmp\ntracked.txt\n", encoding="utf-8")
        self._git("add", ".gitignore")
        self._git("commit", "-q", "-m", "ignore rules")
        (self.repo / "ignored.tmp").write_text("ignored\n", encoding="utf-8")

        baseline = hc.capture_git_baseline(str(self.repo))
        self.assertEqual(hc.get_changed_paths(str(self.repo), baseline), ())

        (self.repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
        self.assertEqual(
            hc.get_changed_paths(str(self.repo), baseline),
            ("tracked.txt",),
        )

    def test_changed_paths_cover_staged_unstaged_untracked_deleted_spaces_unique_sorted(self) -> None:
        hc = self._hc()
        baseline = hc.capture_git_baseline(str(self.repo))

        tracked = self.repo / "tracked.txt"
        tracked.write_text("staged version\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        tracked.write_text("unstaged version\n", encoding="utf-8")

        (self.repo / "added.txt").write_text("added\n", encoding="utf-8")
        self._git("add", "added.txt")
        (self.repo / "untracked.txt").write_text("new\n", encoding="utf-8")
        (self.repo / "delete.txt").unlink()

        spaced = self.repo / "dir with space" / "file name.txt"
        spaced.parent.mkdir()
        spaced.write_text("space\n", encoding="utf-8")

        self.assertEqual(
            hc.get_changed_paths(str(self.repo), baseline),
            (
                "added.txt",
                "delete.txt",
                "dir with space/file name.txt",
                "tracked.txt",
                "untracked.txt",
            ),
        )

    def test_committed_change_after_baseline_is_reported(self) -> None:
        hc = self._hc()
        baseline = hc.capture_git_baseline(str(self.repo))
        (self.repo / "tracked.txt").write_text("committed\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        self._git("commit", "-q", "-m", "after baseline")
        self.assertEqual(
            hc.get_changed_paths(str(self.repo), baseline),
            ("tracked.txt",),
        )

    def test_rename_reports_old_and_new_paths(self) -> None:
        hc = self._hc()
        baseline = hc.capture_git_baseline(str(self.repo))
        self._git("mv", "tracked.txt", "renamed.txt")
        self.assertEqual(
            hc.get_changed_paths(str(self.repo), baseline),
            ("renamed.txt", "tracked.txt"),
        )

    def test_non_repository_and_invalid_baseline_fail_closed(self) -> None:
        import tempfile
        from pathlib import Path

        hc = self._hc()

        with tempfile.TemporaryDirectory() as other:
            with self.assertRaises(RuntimeError):
                hc.capture_git_baseline(other)

        baseline = hc.GitBaseline(head="definitely-not-a-valid-commit")
        with self.assertRaises(RuntimeError):
            hc.get_changed_paths(str(self.repo), baseline)

    def test_git_command_failure_fails_closed(self) -> None:
        import os
        from unittest.mock import patch

        hc = self._hc()
        with patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaises(RuntimeError):
                hc.capture_git_baseline(str(self.repo))


if __name__ == "__main__":
    unittest.main()
