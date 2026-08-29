# SHADOW-BATCH-AUTONOMOUS-001

## Status
ACTIVE

Task Baseline: 8e65c2f

## Allowed Changes
- `experiments/shadow-batch-run.py`
- `experiments/shadow-batch-result.json`
- `experiments/shadow-batch-report.md`
- `tasks/SHADOW-BATCH-AUTONOMOUS-001.md`
- `STATUS.md`

## Forbidden Changes
- Original Team Project OS repository
- Official Architecture or VNEXT tasks
- Worker authority, parser/validator policy, timeout, retry, or globalization
- Any path outside Allowed Changes

## Verification
Run:

`git diff --check`

Then run:

`python tools/qh.py status`
