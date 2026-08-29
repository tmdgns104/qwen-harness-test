# TP-OS-SHADOW-001R2F

## Status
COMPLETE - VERIFIED

Task Baseline: ff6632d

## Allowed Changes
- `tasks/TP-OS-SHADOW-001R2F.md`
- `experiments/tpos-os-shadow-001r2f.py`
- `experiments/tpos-os-shadow-001r2f-result.json`
- `experiments/tpos-os-shadow-001r2f-report.md`
- `STATUS.md`

## Forbidden Changes
- Production adapter, parser, schema, timeout, retry, or authority
- Original Team Project OS repository
- Any path outside Allowed Changes

## Verification
Run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator tests.test_ollama_worker -q`

Then run:

`git diff --check`
