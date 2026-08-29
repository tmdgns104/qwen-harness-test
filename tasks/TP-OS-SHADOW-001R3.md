# TP-OS-SHADOW-001R3

## Status
ACTIVE

Task Baseline: 89a459d

## Allowed Changes
- `tools/ollama_worker.py`
- `tests/test_ollama_worker.py`
- `tasks/TP-OS-SHADOW-001R3.md`
- `STATUS.md`
- `experiments/tpos-os-shadow-001r3.py`
- `experiments/tpos-os-shadow-001r3-result.json`
- `experiments/tpos-os-shadow-001r3-report.md`

## Forbidden Changes
- Original Team Project OS repository
- Native Agent, authority, timeout, retry, validator, or schema relaxation
- Any path outside Allowed Changes

## Verification
Run:

`python -m unittest tests.test_ollama_worker tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator -q`

Then run:

`git diff --check`
