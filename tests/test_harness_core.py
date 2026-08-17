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


if __name__ == "__main__":
    unittest.main()
