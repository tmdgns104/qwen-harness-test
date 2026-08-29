# VNEXT-007G Phase 2 — Auditable Semantic Generalization Benchmark

## Status
ACTIVE

## Task Baseline
75ad0d2

## Allowed Changes
- `tasks/VNEXT-007G2.md`
- `STATUS.md`
- `experiments/vnext-007g2/benchmark.py`
- `experiments/vnext-007g2/result.json`
- `experiments/vnext-007g2/report.md`

## Forbidden Changes
- Official adapter/parser/validator/apply semantics, retry, authority
- Native Agent, larger models, VNEXT-008, Team Project OS, GLOBALIZATION

## Verification
Run:

`python experiments/vnext-007g2/benchmark.py`

Then run:

`git diff --check`

