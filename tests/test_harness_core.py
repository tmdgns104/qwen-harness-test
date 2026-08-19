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

class VerificationCommandContractTests(unittest.TestCase):
    def _hc(self):
        import tools.harness_core as harness_core
        return harness_core

    def test_parses_run_exactly_inline_code(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run exactly:

`python -m unittest tests.test_harness_core`
"""
        result = hc.parse_verification_commands(markdown)
        self.assertEqual(result.commands, ("python -m unittest tests.test_harness_core",))

    def test_parses_run_exactly_single_line_fenced_block(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run exactly:

```text
python -m unittest tests.test_harness_core
```
"""
        result = hc.parse_verification_commands(markdown)
        self.assertEqual(result.commands, ("python -m unittest tests.test_harness_core",))

    def test_run_then_run_preserves_command_order(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run:

`python check_docs.py`

Then run:

`git diff --check`
"""
        result = hc.parse_verification_commands(markdown)
        self.assertEqual(result.commands, ("python check_docs.py", "git diff --check"))

    def test_prose_after_valid_command_is_not_executed(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run exactly:

`python -m unittest tests.test_harness_core`

Then verify actual changed paths against scope.
"""
        result = hc.parse_verification_commands(markdown)
        self.assertEqual(result.commands, ("python -m unittest tests.test_harness_core",))

    def test_verify_with_descriptive_bullets_fails_closed(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Verify with:

- content assertions;
- `git diff --check`;
- changed-path comparison.
"""
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)


    def test_missing_verification_section_fails(self) -> None:
        hc = self._hc()
        with self.assertRaises(ValueError):
            hc.parse_verification_commands("## Goal\nNothing here\n")

    def test_empty_verification_section_fails(self) -> None:
        hc = self._hc()
        with self.assertRaises(ValueError):
            hc.parse_verification_commands("## Verification\n\n## Notes\nNothing\n")

    def test_marker_without_command_fails(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run exactly:

Then verify something else.
"""
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)

    def test_multi_command_fenced_block_fails(self) -> None:
        hc = self._hc()
        markdown = """## Verification

Run exactly:

```text
python first.py
python second.py
```
"""
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)

    def test_marker_with_leading_space_fails_closed(self) -> None:
        hc = self._hc()
        markdown = "## Verification\n\n Run exactly:\n\n`echo ok`\n"
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)

    def test_marker_with_trailing_space_fails_closed(self) -> None:
        hc = self._hc()
        markdown = "## Verification\n\nRun exactly: \n\n`echo ok`\n"
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)

    def test_verification_heading_with_leading_space_fails_closed(self) -> None:
        hc = self._hc()
        markdown = " ## Verification\n\nRun exactly:\n\n`echo ok`\n"
        with self.assertRaises(ValueError):
            hc.parse_verification_commands(markdown)


    def test_verification_contract_is_frozen(self) -> None:
        from dataclasses import FrozenInstanceError
        hc = self._hc()
        contract = hc.VerificationContract(commands=("python check.py",))
        with self.assertRaises(FrozenInstanceError):
            contract.commands = ()



class VerificationCommandExecutionTests(unittest.TestCase):
    def _hc(self):
        import tools.harness_core as harness_core

        return harness_core

    def test_successful_command_captures_result_and_execution_contract(self) -> None:
        import subprocess
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("python -m unittest tests.test_harness_core",))
        completed = subprocess.CompletedProcess(
            args=["python", "-m", "unittest", "tests.test_harness_core"],
            returncode=0,
            stdout="stdout text\n",
            stderr="stderr text\n",
        )
        with patch("tools.harness_core.subprocess.run", return_value=completed) as run:
            results = hc.run_verification_commands(contract, r"C:\repo")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].command, "python -m unittest tests.test_harness_core")
        self.assertEqual(results[0].exit_code, 0)
        self.assertEqual(results[0].stdout, "stdout text\n")
        self.assertEqual(results[0].stderr, "stderr text\n")
        run.assert_called_once_with(
            ["python", "-m", "unittest", "tests.test_harness_core"],
            cwd=r"C:\repo",
            shell=False,
            capture_output=True,
            text=True,
            check=False,
        )


    def test_multiple_commands_execute_in_contract_order(self) -> None:
        import subprocess
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("python first.py", "python second.py"))
        completed = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="first", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="second", stderr=""),
        ]
        with patch("tools.harness_core.subprocess.run", side_effect=completed) as run:
            results = hc.run_verification_commands(contract, r"C:\repo")

        self.assertEqual([r.command for r in results], ["python first.py", "python second.py"])
        self.assertEqual(run.call_count, 2)

    def test_nonzero_exit_code_is_returned_unchanged(self) -> None:
        import subprocess
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("python fail.py",))
        completed = subprocess.CompletedProcess(args=[], returncode=7, stdout="out", stderr="err")
        with patch("tools.harness_core.subprocess.run", return_value=completed):
            results = hc.run_verification_commands(contract, r"C:\repo")

        self.assertEqual(results[0].exit_code, 7)
        self.assertEqual(results[0].stdout, "out")
        self.assertEqual(results[0].stderr, "err")

    def test_execution_continues_after_nonzero_exit(self) -> None:
        import subprocess
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("python fail.py", "python next.py"))
        completed = [
            subprocess.CompletedProcess(args=[], returncode=3, stdout="", stderr="fail"),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="next", stderr=""),
        ]
        with patch("tools.harness_core.subprocess.run", side_effect=completed) as run:
            results = hc.run_verification_commands(contract, r"C:\repo")

        self.assertEqual([r.exit_code for r in results], [3, 0])
        self.assertEqual(run.call_count, 2)


    def test_empty_contract_fails_before_process_execution(self):
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=())
        with patch("tools.harness_core.subprocess.run") as run:
            with self.assertRaises(ValueError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_not_called()

    def test_malformed_quoting_fails_before_process_execution(self):
        from unittest.mock import patch

        hc = self._hc()
        command = "python script.py " + chr(34) + "unterminated"
        contract = hc.VerificationContract(commands=(command,))
        with patch("tools.harness_core.subprocess.run") as run:
            with self.assertRaises(ValueError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_not_called()

    def test_shell_control_operator_fails_before_process_execution(self):
        from unittest.mock import patch

        hc = self._hc()
        operator = chr(38) * 2
        command = "python first.py " + operator + " python second.py"
        contract = hc.VerificationContract(commands=(command,))
        with patch("tools.harness_core.subprocess.run") as run:
            with self.assertRaises(ValueError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_not_called()

    def test_quoted_argument_with_spaces_is_one_argv_element(self):
        import subprocess
        from unittest.mock import patch

        hc = self._hc()
        quote = chr(34)
        command = "python script.py " + quote + "two words" + quote
        contract = hc.VerificationContract(commands=(command,))
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("tools.harness_core.subprocess.run", return_value=completed) as run:
            hc.run_verification_commands(contract, r"C:\repo")

        self.assertEqual(run.call_args.args[0], ["python", "script.py", "two words"])

    def test_process_start_oserror_becomes_runtime_error(self):
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("missing-command",))
        with patch("tools.harness_core.subprocess.run", side_effect=OSError("cannot start")) as run:
            with self.assertRaises(RuntimeError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_called_once()

    def test_verification_command_result_is_frozen(self):
        from dataclasses import FrozenInstanceError

        hc = self._hc()
        result = hc.VerificationCommandResult(
            command="python check.py",
            exit_code=0,
            stdout="out",
            stderr="",
        )
        with self.assertRaises(FrozenInstanceError):
            result.exit_code = 1

    def test_whitespace_only_command_fails_before_process_execution(self):
        from unittest.mock import patch

        hc = self._hc()
        contract = hc.VerificationContract(commands=("   ",))
        with patch("tools.harness_core.subprocess.run") as run:
            with self.assertRaises(ValueError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_not_called()

    def test_invalid_later_command_fails_before_any_process_execution(self):
        from unittest.mock import patch

        hc = self._hc()
        operator = chr(38) * 2
        invalid = "python second.py " + operator + " python third.py"
        contract = hc.VerificationContract(commands=("python first.py", invalid))
        with patch("tools.harness_core.subprocess.run") as run:
            with self.assertRaises(ValueError):
                hc.run_verification_commands(contract, r"C:\repo")
        run.assert_not_called()


class InvariantCheckTests(unittest.TestCase):
    def _hc(self):
        import tools.harness_core as harness_core

        return harness_core

    def test_exact_utf8_content_match(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.txt").write_bytes("WORKER-OK".encode("utf-8"))
            result = hc.check_exact_content(str(root), "target.txt", "WORKER-OK")

        self.assertEqual(
            result,
            hc.ExactContentResult(
                path="target.txt",
                expected_content="WORKER-OK",
                exists=True,
                matches=True,
            ),
        )

    def test_exact_content_mismatch(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.txt").write_bytes(b"ACTUAL")
            result = hc.check_exact_content(str(root), "target.txt", "EXPECTED")

        self.assertTrue(result.exists)
        self.assertFalse(result.matches)

    def test_exact_content_does_not_normalize_newlines_or_whitespace(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.txt").write_bytes(b"VALUE\n")
            result = hc.check_exact_content(str(root), "target.txt", "VALUE")

        self.assertTrue(result.exists)
        self.assertFalse(result.matches)

    def test_missing_exact_content_target_is_mismatch_evidence(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = hc.check_exact_content(str(root), "missing.txt", "EXPECTED")

        self.assertEqual(result.path, "missing.txt")
        self.assertEqual(result.expected_content, "EXPECTED")
        self.assertFalse(result.exists)
        self.assertFalse(result.matches)


    def test_sha256_match(self):
        import hashlib
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        data = b"HASH-CONTENT"
        expected = hashlib.sha256(data).hexdigest()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.bin").write_bytes(data)
            result = hc.check_sha256(str(root), "target.bin", expected)

        self.assertEqual(result.actual_sha256, expected)
        self.assertTrue(result.exists)
        self.assertTrue(result.matches)

    def test_sha256_mismatch(self):
        import hashlib
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        data = b"ACTUAL"
        actual = hashlib.sha256(data).hexdigest()
        expected = hashlib.sha256(b"EXPECTED").hexdigest()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.bin").write_bytes(data)
            result = hc.check_sha256(str(root), "target.bin", expected)

        self.assertEqual(result.actual_sha256, actual)
        self.assertTrue(result.exists)
        self.assertFalse(result.matches)

    def test_sha256_expected_digest_is_case_insensitive(self):
        import hashlib
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        data = b"CASE"
        expected = hashlib.sha256(data).hexdigest().upper()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.bin").write_bytes(data)
            result = hc.check_sha256(str(root), "target.bin", expected)

        self.assertTrue(result.exists)
        self.assertTrue(result.matches)


    def test_malformed_sha256_fails_before_missing_file_result(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                hc.check_sha256(str(root), "missing.bin", "not-a-sha256")

    def test_missing_sha256_target_is_mismatch_evidence(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        expected = "0" * 64
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = hc.check_sha256(str(root), "missing.bin", expected)

        self.assertEqual(result.path, "missing.bin")
        self.assertEqual(result.expected_sha256, expected)
        self.assertIsNone(result.actual_sha256)
        self.assertFalse(result.exists)
        self.assertFalse(result.matches)

    def test_absolute_and_escaping_paths_fail_closed(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = (str(root / "target.txt"), "../outside.txt")
            for candidate in cases:
                with self.subTest(path=candidate):
                    with self.assertRaises(ValueError):
                        hc.check_exact_content(str(root), candidate, "EXPECTED")


    def test_non_file_targets_fail_closed(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "directory"
            target.mkdir()
            with self.assertRaises(ValueError):
                hc.check_exact_content(str(root), "directory", "EXPECTED")
            with self.assertRaises(ValueError):
                hc.check_sha256(str(root), "directory", "0" * 64)

    def test_invariant_result_objects_are_frozen(self):
        from dataclasses import FrozenInstanceError

        hc = self._hc()
        exact = hc.ExactContentResult("target.txt", "EXPECTED", True, True)
        digest = hc.Sha256Result("target.bin", "0" * 64, "0" * 64, True, True)
        with self.assertRaises(FrozenInstanceError):
            exact.matches = False
        with self.assertRaises(FrozenInstanceError):
            digest.matches = False

    def test_file_read_oserror_becomes_runtime_error(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch

        hc = self._hc()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.bin"
            target.write_bytes(b"DATA")
            with patch("pathlib.Path.read_bytes", side_effect=OSError("read failed")):
                with self.assertRaises(RuntimeError):
                    hc.check_exact_content(str(root), "target.bin", "DATA")
                with self.assertRaises(RuntimeError):
                    hc.check_sha256(str(root), "target.bin", "0" * 64)


if __name__ == "__main__":
    unittest.main()
