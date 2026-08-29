# VNEXT Partial Edit — Bounded REPLACE_TEXT Operation

## Status
COMPLETE - VERIFIED

## Task Baseline
de47bac

## Allowed Changes
- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tests/test_bounded_stateless_contract.py`
- `tests/test_candidate_apply.py`
- `tasks/VNEXT-PARTIAL-EDIT.md`
- `STATUS.md`
- `experiments/tpos-shadow-partial-edit.py`
- `experiments/tpos-shadow-partial-edit-result.json`
- `experiments/tpos-shadow-partial-edit-report.md`

## Forbidden Changes
- Native Agent, timeout, retry, authority, Target repository, VNEXT-008, GLOBALIZATION

## Verification
Run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator tests.test_ollama_worker -q`

Then run:

`git diff --check`
