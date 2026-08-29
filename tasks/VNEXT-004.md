# VNEXT-004 — Temporary Candidate Apply

## Status
APPROVED - READY FOR CONTRACT BASELINE

## Goal

Apply a validated passive Candidate atomically to a fresh temporary snapshot without modifying the original Repository.

## Architecture Basis

`docs/ARCHITECTURE-VNEXT.md`, ADR-019, and VNEXT-003 validator. Application authority remains Harness-owned.

## Dependencies

VNEXT-003 completion commit `f69d66d5c0c8affc5b2872f02ad1ec0bbf0ee3c4`.

## Scope

Implement temporary directory snapshot copy and deterministic CREATE_FILE/REPLACE_FILE application with defense-in-depth path containment and atomic failure behavior.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_candidate_apply.py`
- `tasks/VNEXT-004.md`
- `STATUS.md`
- `experiments/vnext-004/report.md`

## Forbidden Changes

- Native Agent, Ollama adapter, Worker authority, Git/shell/test authority
- Candidate validator weakening, Candidate retry, verification orchestration
- Production timeout, Tool Authority, Write Authority, Security Boundary
- `docs/**`, `DECISIONS.md`, VNEXT-005+, Team Project OS, unrelated files

## Acceptance Criteria

- Only validator-PASS Candidates can be applied.
- CREATE_FILE rejects existing targets; REPLACE_FILE rejects missing targets.
- Absolute/traversal/symlink escape is rejected; original Repository remains unchanged.
- Multi-operation failure is atomic and never reported as success.
- Structured result records success, snapshot path, applied operations, and error.

## Verification

Run:

`python -m unittest discover -s tests -p "test_candidate_apply.py"`

Then run:

`python -m unittest tests.test_bounded_stateless_contract tests.test_context_pack tests.test_candidate_validator tests.test_harness_core -q`

Then run:

`git diff --check`

## Evidence Requirements

Record isolation, operation semantics, containment, atomicity, and regression results.

## Stop Conditions

Stop if applying requires original Repository mutation, Worker authority, or verification orchestration.
