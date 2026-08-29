# QWEN25-CODER-PROFILE-001

## Status
COMPLETE - VERIFIED

Task Baseline: 3e93284

## Allowed Changes
- `tasks/QWEN25-CODER-PROFILE-001.md`
- `STATUS.md`
- `experiments/qwen25-coder-profile-run.py`
- `experiments/qwen25-coder-profile-result.json`
- `experiments/qwen25-coder-profile-report.md`

## Forbidden Changes
- Original Team Project OS repository; Harness Core contracts and safety policy
- Model installation, authority, timeout, retry, parser/validator changes
- Any path outside Allowed Changes

## Verification
Run:

`python -m unittest tests.test_ollama_worker tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator -q`

Then run:

`git diff --check`
