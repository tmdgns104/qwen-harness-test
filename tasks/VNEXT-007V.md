# VNEXT-007V — Strong Semantic Verification Benchmark

## Status
COMPLETE - VERIFIED

## Task Baseline
1f498c1

## Allowed Changes
- `tasks/VNEXT-007V.md`
- `STATUS.md`
- `experiments/vnext-007v/benchmark.py`
- `experiments/vnext-007v/result.json`
- `experiments/vnext-007v/report.md`

## Forbidden Changes
- Existing Worker pipeline, parser, validator, apply semantics, retry, authority
- Native Agent, larger models, VNEXT-008, Team Project OS, GLOBALIZATION

## Verification
Run:

`python experiments/vnext-007v/benchmark.py`

Then run:

`git diff --check`
