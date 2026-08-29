# TP-OS-SHADOW-001R2

## Status
ACTIVE

## Allowed Changes
- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tasks/TP-OS-SHADOW-001R2.md`
- `STATUS.md`
- `experiments/tpos-os-shadow-001r2.py`
- `experiments/tpos-os-shadow-001r2-result.json`
- `experiments/tpos-os-shadow-001r2-report.md`

## Verification
Run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator tests.test_ollama_worker -q`

Then run:

`git diff --check`

