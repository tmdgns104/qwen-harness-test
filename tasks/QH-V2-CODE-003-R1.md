# QH-V2-CODE-003-R1 - Retry Small Related Two-File Change

## Status

APPROVED - RETRY OF QH-V2-CODE-003

## Goal

Fix the existing section-identifier behavior across the two allowed source files.

This retry keeps the same implementation problem as QH-V2-CODE-003.
The purpose of the retry is to test whether explicit, task-local editing discipline
prevents the previous edit-loop failure.

## Required Behavior

`src/text_utils.py`

- `slugify_heading(text)` must normalize outer and repeated whitespace.
- It must lowercase the normalized text.
- Each normalized ASCII space must become `-`.

`src/report_utils.py`

- `build_section_anchor(title, prefix)` must call and use `slugify_heading(title)`.
- It must return exactly `<prefix>:<slugified-title>`.

Do not change function names or signatures.

## Execution Discipline

- Read `src/text_utils.py` before modifying it.
- Read `src/report_utils.py` before modifying it.
- Read both target files before the first edit.
- Base edits only on text directly observed in the current file contents.
- Do not guess an `oldString`.
- If an edit fails because the text does not match, re-read that target file before retrying.
- Make at most one retry for the same logical modification.
- If the same logical modification fails twice, stop and report `BLOCKED`.
- Do not repeat guessed edit variants.

## Allowed Changes

- `src/text_utils.py`
- `src/report_utils.py`

## Forbidden Changes

- `tests/**`
- `tasks/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- all other Repository files

## Acceptance Criteria

- `slugify_heading("  Hello   Qwen World  ")` returns exactly `hello-qwen-world`.
- `slugify_heading("  RAG   설계  ")` returns exactly `rag-설계`.
- `build_section_anchor("  Hello   Qwen World  ", "sec")` returns exactly `sec:hello-qwen-world`.
- `build_section_anchor("RAG 설계", "chapter-2")` returns exactly `chapter-2:rag-설계`.
- Only the two files under Allowed Changes may be modified by the Worker.
- All Repository unit tests pass.

## Verification

Run:

`python -m unittest discover -s tests -p "test_*.py"`

The command must exit successfully.

## Stop

Stop after this retry Task.
Do not modify tests.
Do not modify this Task file.
Do not start another Task.
