# VNEXT-007A — Candidate Apply Semantics Investigation & Hardening

## Status
COMPLETE - VERIFIED

## Task Baseline
d18d16d

## Allowed Changes
- `tools/ollama_worker.py`
- `tasks/VNEXT-007A.md`
- `STATUS.md`
- `experiments/vnext-007a/benchmark.py`
- `experiments/vnext-007a/result.json`
- `experiments/vnext-007a/report.md`

## Forbidden Changes
- CREATE/REPLACE auto-correction, parser/validator/apply relaxation
- Retry, Native Agent, authority, timeout, Team Project OS, VNEXT-008

## Verification
Run:

`python experiments/vnext-007a/benchmark.py`

Then run:

`git diff --check`
