# VNEXT-005 — Verification Outcomes and Evidence

## Status
APPROVED - READY FOR CONTRACT BASELINE

## Goal

Implement deterministic Verification Result and bounded Outcome mapping for validated Candidates applied to isolated snapshots.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md`, ADR-019, and VNEXT-001 through VNEXT-004. Worker self-report is never completion authority.

## Dependencies

VNEXT-004 completion commit `6f260b66f1c03dce3ad24fe12986d2bce61421d8`.

## Scope

Represent approved verification commands/results, expected versus actual changed paths, original-repository invariance, and deterministic mapping to `BoundedOutcome`. No Worker inference, retry, or apply orchestration.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_bounded_verification.py`
- `tasks/VNEXT-005.md`
- `STATUS.md`
- `experiments/vnext-005/report.md`

## Forbidden Changes

- Native Agent, Ollama adapter, Worker authority, Candidate apply, retry, model inference
- Final Gate or existing evidence semantics, semantic LLM test weakening judgment
- Production timeout, Tool Authority, Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-006+, Team Project OS, unrelated files

## Acceptance Criteria

- Structured verification result preserves outcome, tests, paths, diff summary, errors, and metadata.
- Invalid Candidate, failed apply, failed tests, unexpected paths, and original mutation map to non-success outcomes.
- All required checks passing maps to `COMPLETED`; empty Candidate is not implicitly success.
- Failure Evidence is structured and bounded; no retry loop is implemented.

## Verification

Run:

`python -m unittest discover -s tests -p "test_bounded_verification.py"`

Then run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_context_pack tests.test_candidate_validator tests.test_candidate_apply tests.test_harness_core -q`

Then run:

`git diff --check`

## Evidence Requirements

Record outcome mappings, deterministic path checks, test result handling, original invariance, and regression results.

## Stop Conditions

Stop if implementation requires Worker retry/inference, hidden-test orchestration, or authority expansion.
