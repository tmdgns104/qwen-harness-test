# QH-V2-AUTO-005 - Automatic Task Baseline Lifecycle Integration

## Status

COMPLETE - VERIFIED

## Parent

ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints
QH-V2-PRR-001 - Pre-Runner Safety/UX Review
QH-V2-AUTO-004 - Task-Range Scope Review

## Problem

QH-V2-PRR-001 identified Task baseline handling as REQUIRED BEFORE RUNNER. `qh.py start` does not persist the Task baseline, `qh.py review` uses current HEAD when no explicit baseline is supplied, and `qh.py close` therefore cannot independently guarantee review of committed Task-range changes.

## Goal

Make Task lifecycle review automatically use the correct persisted Task baseline so normal `qh.py review` and `qh.py close` cover committed Task-range changes without requiring the Human to remember a commit SHA.

## Scope

V1 must:

1. Capture the current Git HEAD when `qh.py start <TASK-ID>` begins a Task.
2. Persist that baseline in deterministic Repository lifecycle state.
3. Make `qh.py review` with no explicit baseline use the persisted current-Task baseline.
4. Preserve `qh.py review <commit>` as an explicit Human override.
5. Make `qh.py close <commit>` use normal review behavior and therefore include the persisted Task range.
6. Fail closed when the persisted baseline is missing, malformed, not a commit, or otherwise unusable.
7. Preserve current Human Gates and lifecycle behavior.

The persisted baseline represents the Repository HEAD immediately before the lifecycle start mutation for the Task.

## Boundaries

- Reuse existing Harness Core `GitBaseline`, changed-path Evidence, verification, Evidence assembly, and final gate.
- Do not create a second Git/scope/Evidence engine.
- Do not implement Runner, retry, Worker tool execution, qh doctor, Task scaffolding, or UX redesign.
- Do not implement scope-engine unification in this Task; that remains the second REQUIRED BEFORE RUNNER item.
- No automatic commit, automatic Task completion, automatic next-Task selection, or Architecture modification.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `STATUS.md`
- `tasks/QH-V2-AUTO-005.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/repo_tools.py`
- `tools/ollama_worker.py`
- `tests/test_harness_core.py`
- `tests/test_repo_tools.py`
- `tests/test_ollama_worker.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- `start` records the pre-start HEAD as the current Task baseline.
- `review` without an argument reviews from the persisted baseline through current HEAD plus current uncommitted changes.
- `review <commit>` continues to support explicit baseline override.
- `close` cannot silently reduce review to current HEAD only.
- A committed forbidden change since the persisted baseline causes normal `review` and `close` to fail even when the working tree is clean.
- A committed allowed change since the persisted baseline is included without false failure.
- Missing, malformed, invalid, or unusable persisted baseline fails closed without lifecycle mutation.
- Existing lifecycle and explicit Task-range review behavior remains passing.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python -m unittest tests.test_repo_tools`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after focused and regression Verification, independent Task-range review, implementation commit, lifecycle close, completion commit, and clean working tree.

Do not begin scope-engine unification or Single-Task Runner in this Task.
