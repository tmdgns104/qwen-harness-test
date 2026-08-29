# VNEXT-003 — Structured Candidate Validator

## Status
APPROVED - READY FOR CONTRACT BASELINE

## Goal

Implement deterministic validation for passive Candidate operations before any future apply.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md`, ADR-019, and VNEXT-001 Candidate contracts. Validation is Harness-owned; semantic quality remains verification responsibility.

## Dependencies

VNEXT-001 completion commit `52607dee2cf7ec696e961072db40fcea869f3da0` and VNEXT-002 completion commit `07d64952e9b23d7726d2dccdfe680ac5626acc1e`.

## Scope

Validate Candidate schema, supported operation types, normalized relative paths, allowed/forbidden scope, protected lifecycle paths, operation count, content size, duplicates, and unsupported deletes. Do not apply candidates.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_candidate_validator.py`
- `tasks/VNEXT-003.md`
- `STATUS.md`
- `experiments/vnext-003/report.md`

## Forbidden Changes

- Native Agent, Ollama adapter, Worker authority, filesystem/Git/shell access
- Candidate application, temporary snapshot, test orchestration, retry, model inference
- Semantic LLM test weakening judgment or parser fallback
- Production timeout, Tool Authority, Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-004+, Team Project OS, unrelated files

## Acceptance Criteria

- Valid CREATE_FILE/REPLACE_FILE candidates within explicit scope are accepted.
- Invalid operation type, absolute/traversal path, forbidden/protected path, duplicate path, count/size overflow, and malformed candidate are rejected fail-closed.
- No apply/execute/write/save/filesystem/Git/shell method is introduced.
- Existing Native Agent and VNEXT-001/002 contracts remain green.

## Verification

Run:

`python -m unittest discover -s tests -p "test_candidate_validator.py"`

Then run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_context_pack tests.test_harness_core -q`

Then run:

`git diff --check`

## Evidence Requirements

Record validator acceptance/rejection cases, limits, scope behavior, and regression results.

## Stop Conditions

Stop if validation requires semantic LLM judgment, Candidate application, or authority expansion.
