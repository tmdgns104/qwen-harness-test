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


if __name__ == "__main__":
    unittest.main()
