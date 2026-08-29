# VNEXT-007S — Semantic E2E & Generalization Verification

## Status
COMPLETE - VERIFIED

## Task Baseline
8a98c28

## Allowed Changes
- `tasks/VNEXT-007S.md`
- `STATUS.md`
- `experiments/vnext-007s/benchmark.py`
- `experiments/vnext-007s/result.json`
- `experiments/vnext-007s/report.md`

## Forbidden Changes
- Parser/Validator/Apply relaxation, retry, authority, Native Agent
- Timeout, Team Project OS, VNEXT-008, GLOBALIZATION

## Verification
Run:

`python experiments/vnext-007s/benchmark.py`

Then run:

`git diff --check`
