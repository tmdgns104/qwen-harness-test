# QH-V2-CODE-003 - Small Related Two-File Change

## Goal

Fix the related section-identifier behavior across two existing source files.

## Required Behavior

`src/text_utils.py`
- `slugify_heading(text)` must normalize outer/repeated whitespace.
- It must lowercase the normalized text.
- Each normalized ASCII space must become `-`.

`src/report_utils.py`
- `build_section_anchor(title, prefix)` must use `slugify_heading(title)`.
- It must return exactly `<prefix>:<slugified-title>`.

Do not change function names or signatures.

## Allowed Changes

- `src/text_utils.py`
- `src/report_utils.py`

## Forbidden Changes

- `tests/**`
- `tasks/**`
- all other Repository files

## Verification

Run:

`python -m unittest discover -s tests -p "test_*.py"`

## Stop

Fix this Task only.
Do not modify tests.
Do not start another Task.
