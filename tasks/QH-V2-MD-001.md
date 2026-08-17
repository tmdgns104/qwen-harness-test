# QH-V2-MD-001 - Long Markdown Append Regression

## Status

APPROVED - READY FOR REGRESSION

## Goal

Append ADR-016 and ADR-017 to the existing long Markdown file
`docs/long_decisions.md`.

This Task reproduces the long-Markdown append shape that previously caused
exact-string edit failures in real Repository work.

## Required Changes

Append these two new ADRs after the existing ADR-015.

### ADR-016 - Long Markdown Append Regression

- Status: Accepted
- Decision: The Worker must append this ADR after ADR-015.
- Evidence: Git/Test evidence is authoritative; Worker self-reported PASS is not authoritative.
- Scope: Existing ADR-001 through ADR-015 must remain byte-for-byte unchanged.

### ADR-017 - Safe Editing Discipline

- Status: Accepted
- Decision: Long Markdown append work must avoid guessed exact-string edit loops.
- Stop: If the same logical modification fails twice, report BLOCKED and stop.
- Boundary: No file other than `docs/long_decisions.md` may be modified by the Worker.

## Allowed Changes

- `docs/long_decisions.md`

## Forbidden Changes

- `tests/**`
- `tasks/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- all other Repository files

## Acceptance Criteria

- ADR-016 exists exactly once after ADR-015.
- ADR-017 exists exactly once after ADR-016.
- Existing ADR-001 through ADR-015 remain byte-for-byte unchanged.
- Only `docs/long_decisions.md` is modified.
- All tests in `tests/test_markdown_append.py` pass.

## Verification

Run:

`python -m unittest tests.test_markdown_append`

## Stop

Stop after this Task.
Do not modify tests.
Do not modify this Task file.
Do not start another Task.
