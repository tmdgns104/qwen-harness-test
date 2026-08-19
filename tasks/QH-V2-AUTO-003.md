# QH-V2-AUTO-003 - Lifecycle Next-Planned Consistency Fix

## Status

COMPLETE - VERIFIED

## Parent

QH-V2-AUTO-002 - Deterministic Task Lifecycle Assistance
Deferred automation follow-up from real `qh.py start` usage

## Problem

The first real transition attempt from QH-V2-AUTO-002 to QH-V2-READ-001 exposed a lifecycle inconsistency. `qh.py start QH-V2-READ-001` correctly changed Current Task and Previous Task but left `Next Planned Task: Harness-owned Repository Read Tools - NOT STARTED` unchanged. This made the same work simultaneously ACTIVE and NOT STARTED. The transition was reverted before implementation continued.

## Goal

Make explicit Human-invoked `qh.py start` leave STATUS.md in a non-contradictory lifecycle state without automatically selecting the next Task.

## Required Behavior

After a successful `start <TASK-ID>` transition:

- Current Task becomes the explicitly requested Task with ACTIVE state
- Previous Task becomes the former Current Task
- Next Planned Task is replaced with the neutral value `Next Planned Task: NOT SET - HUMAN SELECTION REQUIRED`
- historical Handoff text remains unchanged
- no next Task is automatically selected

## Human Gate

The Human still explicitly chooses which Task to start. This Task must not infer or select a future Task.

## Failure Boundary

If lifecycle structure is missing, duplicated, or otherwise ambiguous, `start` must fail before modifying STATUS.md. Existing missing-target and duplicate-field fail-closed behavior must remain intact.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `tasks/QH-V2-AUTO-003.md`
- `STATUS.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `tests/test_harness_core.py`
- `tests/test_ollama_worker.py`
- `tests/test_repo_tools.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- Real failure class discovered during the QH-V2-READ-001 transition is reproduced by a focused test.
- Successful start cannot leave the started work described as NOT STARTED in Next Planned Task.
- Next Planned Task becomes exactly `NOT SET - HUMAN SELECTION REQUIRED`.
- No automatic next-Task selection is introduced.
- Current and Previous lifecycle behavior remains correct.
- Historical Handoff content remains unchanged.
- Duplicate or malformed lifecycle structure remains fail-closed.
- Missing target Task remains fail-closed.
- Existing close deterministic Final Gate behavior remains passing.
- Existing qh regression remains passing.
- Harness Core regression remains passing.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after implementation, Verification, independent review, lifecycle close, commit, and clean working tree.

Do not start QH-V2-READ-001 until this lifecycle inconsistency is fixed and verified.
