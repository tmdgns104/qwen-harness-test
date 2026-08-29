# TP-OS-SHADOW-001R4

## Status
ACTIVE

Task Baseline: 76ba2a7

## Allowed Changes
- `tasks/TP-OS-SHADOW-001R4.md`
- `STATUS.md`
- `experiments/tpos-os-shadow-001r4.py`
- `experiments/tpos-os-shadow-001r4-result.json`
- `experiments/tpos-os-shadow-001r4-report.md`

## Forbidden Changes
- Original Team Project OS repository
- Production code, parser, validator, timeout, retry, or authority
- Any path outside Allowed Changes

## Verification
Run:

`python -m unittest tests.test_ollama_worker tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator -q`

Then run:

`git diff --check`
