# VNEXT-007V-R — Strong Semantic Benchmark Completion

## Status
COMPLETE - VERIFIED

## Task Baseline
83ae527

## Allowed Changes
- `tasks/VNEXT-007V-R.md`
- `STATUS.md`
- `experiments/vnext-007v-r/benchmark.py`
- `experiments/vnext-007v-r/result.json`
- `experiments/vnext-007v-r/report.md`

## Forbidden Changes
- Parser/Validator/Apply semantics, retry, authority, Native Agent
- Production timeout, larger models, VNEXT-008, Team Project OS, GLOBALIZATION

## Verification
Run:

`python experiments/vnext-007v-r/benchmark.py`

Then run:

`git diff --check`
