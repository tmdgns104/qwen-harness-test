# QH-V2-ARCH-004 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints

## Status

COMPLETE - VERIFIED

## Parent

ADR-004 - Post-HC-007 Worker Integration Architecture
ADR-005 - Repetitive Harness Workflow Automation Priority
QH-V2-AUTO-004 - Task-Range Scope Review

## Problem

Milestone 1 currently proceeds from Scoped Edit Tools directly toward Single-Task Runner and ends at E2E Regression. Repository work has now produced concrete safety, usability, automation, and troubleshooting improvement candidates, but there is no explicit checkpoint for deciding which must be addressed before Runner integration and which should be deferred until after Milestone 1 E2E.

## Goal

Add explicit Repository planning checkpoints for a Pre-Runner Safety/UX Review and a Post-Milestone 1 Hardening & UX Improvement phase without implementing those improvements in this Task.

## Scope

Review and document the appropriate placement of two checkpoints:

1. Pre-Runner Safety/UX Review before Single-Task Runner implementation.
2. Post-Milestone 1 Hardening & UX Improvement after E2E Regression.

The Pre-Runner review must classify known improvement candidates into:

- required before Runner
- safe to defer until after E2E
- deferred pending more Evidence

Known candidates to review:

- automatic Task baseline recording and reuse by review
- unification of Harness Core and Repository Edit Tool scope evaluation
- reduction of long Windows CMD / inline `python -c` workflows
- deterministic `qh doctor` environment/state troubleshooting
- clearer `qh status` current-state, progress, next-gate, and historical-handoff presentation
- Human-approved Task scaffold generation
- Worker smoke-test standardization after sufficient repeated Evidence

## Human Gate

This Task does not automatically approve or implement any improvement candidate.

Human approval remains required for Architecture changes, implementation Tasks, commits, Task completion, and next-Task selection.

## Allowed Changes

- `DECISIONS.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-004.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- Repository planning explicitly contains a Pre-Runner Safety/UX Review checkpoint before Single-Task Runner.
- Repository planning explicitly contains a Post-Milestone 1 Hardening & UX Improvement phase after E2E Regression.
- Known improvement candidates are preserved for later classification.
- No improvement implementation is performed in this Task.
- No Runner, retry, CLI, E2E, Ollama, or Repository tool code is changed.
- Human Gate remains explicit.
- Important sequencing decision is recorded in DECISIONS.md.
- STATUS.md reflects the resulting next-step plan.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after the planning decision is documented, reviewed, committed, lifecycle closed, and the working tree is clean.

Do not begin improvement implementation or Single-Task Runner in this Task.
