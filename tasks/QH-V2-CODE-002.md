# QH-V2-CODE-002 - Fix Existing Function Bug

## Goal

Fix the existing `truncate_with_ellipsis(text: str, max_length: int) -> str`
implementation in `src/text_utils.py`.

## Required Behavior

- If `text` already fits within `max_length`, return it unchanged.
- If truncation is required, the entire returned string must be exactly
  `max_length` characters long.
- A truncated result must end with `...`.
- `max_length` is always at least 3.
- Preserve the original text prefix before the ellipsis.

Do not change the function name or signature.

## Allowed Changes

- `src/text_utils.py`

## Forbidden Changes

- `tests/**`
- `tasks/**`
- all other Repository files

## Verification

Run:

`python -m unittest discover -s tests -p "test_*.py"`

## Stop

Fix this bug only.
Do not change tests.
Do not start another Task.
