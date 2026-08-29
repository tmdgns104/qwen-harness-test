# MODEL-DECISION-BENCHMARK-001

## Status
ACTIVE

Task Baseline: 3e93284

## Allowed Changes
- `tasks/MODEL-DECISION-BENCHMARK-001.md`
- `STATUS.md`
- `experiments/model-decision-benchmark.py`
- `experiments/model-decision-result.json`
- `experiments/model-decision-report.md`

## Forbidden Changes
- Original Team Project OS repository
- Official Architecture/VNext tasks, model installation, authority, timeout, retry, parser/validator policy
- Any path outside Allowed Changes

## Verification
Run:

`python -m unittest tests.test_ollama_worker tests.test_bounded_stateless_contract tests.test_candidate_apply tests.test_candidate_validator -q`

Then run:

`git diff --check`
