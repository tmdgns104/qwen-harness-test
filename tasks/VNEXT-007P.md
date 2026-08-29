# VNEXT-007P — Candidate Path Alignment Investigation & Hardening

## Status
COMPLETE - VERIFIED

## Task Baseline
7c104bedff4396861e8ebc6c2bb1173987d441e3

## Allowed Changes
- `tools/ollama_worker.py`
- `tasks/VNEXT-007P.md`
- `STATUS.md`
- `experiments/vnext-007p/benchmark.py`
- `experiments/vnext-007p/result.json`
- `experiments/vnext-007p/report.md`

## Forbidden Changes
- Parser or Validator relaxation, fuzzy path repair
- Native Agent, retry, self-review, timeout, authority, Team Project OS
- VNEXT-008 and GLOBALIZATION

## Verification
Run:

`python experiments/vnext-007p/benchmark.py`

Then run:

`git diff --check`
