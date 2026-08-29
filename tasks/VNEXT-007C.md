# VNEXT-007C — Context / Write-Authority Boundary Hardening

## Status
COMPLETE - VERIFIED

## Task Baseline
2cffd00ec56bd2f303051b4a9b83237ca3b46273

## Allowed Changes
- `tools/ollama_worker.py`
- `tasks/VNEXT-007C.md`
- `STATUS.md`
- `experiments/vnext-007c/benchmark.py`
- `experiments/vnext-007c/result.json`
- `experiments/vnext-007c/report.md`

## Forbidden Changes
- Parser/Validator relaxation or path repair
- Native Agent, retry, timeout, authority, Team Project OS, VNEXT-008

## Verification
Run:

`python experiments/vnext-007c/benchmark.py`

Then run:

`git diff --check`
