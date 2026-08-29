# VNEXT-002 — Deterministic Context Pack Builder

## Status
APPROVED - READY FOR CONTRACT BASELINE

## Goal

Implement an immutable Context Pack and deterministic Harness-owned Builder for bounded stateless requests.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md` and ADR-019. Worker receives only supplied context and has no Repository authority.

## Dependencies

VNEXT-001 bounded request/response contracts at baseline `8ed21ff`.

## Scope

Represent task metadata, explicitly selected repository/architecture/decision items, output contract, and character budget. Build only from caller-provided inputs; never enumerate the Repository.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_context_pack.py`
- `tasks/VNEXT-002.md`
- `STATUS.md`
- `experiments/vnext-002/report.md`

## Forbidden Changes

- Native Agent, Ollama adapter, Worker authority, filesystem/Git/shell access
- Candidate validation/application, test orchestration, retry, model inference
- Production timeout, Tool Authority, Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-003+, Team Project OS, unrelated files

## Acceptance Criteria

- Frozen Context Pack and Context Item structures preserve provenance and required fields.
- Builder uses explicit caller-selected items and deterministic ordering.
- Character budget is explicit; overflow and missing required metadata fail closed without blind truncation.
- Same inputs produce equal packs regardless of source insertion order.
- VNEXT-001 contracts and Native Agent regressions remain compatible.

## Verification

Run:

`python -m unittest discover -s tests -p "test_context_pack.py"`

Then run:

`python -m unittest tests.test_harness_core -q`

Then run:

`git diff --check`

## Evidence Requirements

Record focused and regression results, budget/failure behavior, scope, and deterministic ordering.

## Stop Conditions

Stop on any need to enumerate Repository state, change Native Agent boundaries, or broaden scope.
