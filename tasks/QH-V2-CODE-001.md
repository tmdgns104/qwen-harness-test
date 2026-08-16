# QH-V2-CODE-001 - Implement Small Python Function

## Status

APPROVED - READY FOR IMPLEMENTATION

## Goal

Implement the existing `normalize_whitespace(text: str) -> str` function in
`src/text_utils.py`.

This is a coding capability regression test for the OpenCode + Qwen Worker.

## Required Behavior

The function must:

- return an empty string for an empty string
- remove leading and trailing whitespace
- collapse each run of whitespace characters to one ASCII space
- handle spaces, tabs, and line breaks
- preserve the order and content of non-whitespace text

Do not change the function name or signature.

## Allowed Changes

- `src/text_utils.py`

## Forbidden Changes

- `tests/**`
- `tasks/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- all other Repository files

## Acceptance Criteria

- `src/text_utils.py` no longer raises `NotImplementedError`.
- All tests in `tests/test_text_utils.py` pass.
- Only `src/text_utils.py` is modified by the Worker.
- No third-party dependency is added.
- No unrelated helper, framework, or architecture change is introduced.

## Verification

Run:

`python -m unittest discover -s tests -p "test_*.py"`

The command must exit successfully.

## Stop Condition

Stop immediately after implementing `normalize_whitespace`.

Do not modify tests.
Do not modify this Task file.
Do not start another Task.
