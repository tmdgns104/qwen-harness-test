# QH-V2-PRR-001 - Pre-Runner Safety/UX Review

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints
QH-V2-ARCH-004 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints

## Goal

Review known safety, usability, automation, and troubleshooting candidates before Single-Task Runner implementation and classify each candidate without implementing it.

## Scope

Classify each known candidate as one of:

- REQUIRED BEFORE RUNNER
- SAFE TO DEFER UNTIL AFTER E2E
- DEFERRED PENDING MORE EVIDENCE

Candidates:

1. Automatic Task baseline recording and reuse by review.
2. Unification of Harness Core and Repository Edit Tool scope evaluation.
3. Reduction of long Windows CMD / inline Python workflows.
4. Deterministic qh doctor environment/state troubleshooting.
5. Clearer qh status current-state, progress, next-gate, and historical-handoff presentation.
6. Human-approved Task scaffold generation.
7. Worker smoke-test standardization after sufficient repeated Evidence.

The review must use existing Repository Evidence and current interfaces. It must identify any candidate whose absence creates a concrete safety or correctness risk for Single-Task Runner.

## Boundaries

- No candidate is implemented in this Task.
- No Runner, retry, CLI, E2E, Worker Adapter, Repository tool, or Harness Core code is changed.
- No Architecture is changed unless a conflict is discovered; if a conflict is found, STOP and report it instead of changing Architecture.
- Human approval remains required for any follow-up implementation Task.

## Allowed Changes

- `STATUS.md`
- `tasks/QH-V2-PRR-001.md`

## Forbidden Changes

- `DECISIONS.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `tools/**`
- `tests/**`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- All seven candidates are classified.
- Every REQUIRED BEFORE RUNNER classification includes concrete Repository Evidence or interface risk.
- Every deferred classification states why Runner safety/correctness does not currently depend on it.
- Follow-up implementation Tasks are identified only where justified.
- No implementation occurs.
- No file outside Allowed Changes is modified.
- The review produces an explicit GO or BLOCKED recommendation for Single-Task Runner.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after classification, recommendation, independent review, commit, lifecycle close, and clean working tree.

Do not begin Single-Task Runner or any improvement implementation in this Task.
