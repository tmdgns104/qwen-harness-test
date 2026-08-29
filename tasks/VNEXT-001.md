# VNEXT-001 — Bounded Stateless Worker Contract

## Status
ACTIVE

Define backend-neutral request/response, Candidate operation schema, limits, and outcome enum without changing native Agent behavior. Add focused contract tests and evidence. Forbidden: production scope expansion, direct Worker tools, prompt tuning, or Team Project OS writes.

## Goal

Freeze the bounded_stateless contract as a backend-neutral, machine-validatable boundary.

## Allowed Changes

- `tools/` contract records and focused tests only
- `tasks/VNEXT-001.md`, `STATUS.md`, and evidence for this Task

## Forbidden Changes

- Native Agent behavior, tool authority, filesystem/Git/shell access
- Production timeout/retry policy, Architecture outside this Task
- Team Project OS or unrelated files

## Acceptance Criteria

- Request/response and Candidate schemas are explicit and reject unknown operations.
- Limits and all eight outcomes are represented deterministically.
- Existing native tests remain green; no Worker receives direct side-effect authority.
- Contract permits capable reasoning and failure-guided retries while preserving stateless Worker ownership and Harness-managed state.
- Evidence and diff show only allowed files.

## Verification

Run:

`python -m unittest discover -s tests -p "test_bounded_stateless_contract.py"`

`python -m unittest tests.test_harness_core -q`

`python -m unittest discover -s tests -q`

`git diff --check`

Focused contract tests and existing Harness regression must pass. Full-suite failures unrelated to this Task are recorded in Evidence.

## Stop Conditions

Stop on architecture conflict, scope ambiguity, or any need to alter native Agent boundaries.
