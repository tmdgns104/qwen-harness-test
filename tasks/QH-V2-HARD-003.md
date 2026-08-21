# QH-V2-HARD-003 - Duplicate Start / Active Task Lifecycle Guard

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

`command_start()` currently copies the Current Task line into Previous Task and
starts the requested target without first rejecting an already ACTIVE lifecycle.
During QH-V2-E2E-001, a duplicate start produced misleading Current/Previous
history. The existing duplicate test covers two Current Task fields, not repeated
start of a valid ACTIVE Task. The command also does not verify that the target
contract has passed the Human approval gate.

## Goal

Make every `qh start` fail with non-zero exit and zero lifecycle mutation while
any Task is ACTIVE or the target lacks the exact Human-approved contract status,
while preserving the normal approved transition from an exact COMPLETE - VERIFIED
Current Task.

## Architecture Basis

- FR-004 requires exactly one explicitly assigned Task and no automatic next Task.
- FR-008 requires failure to stop rather than corrupt lifecycle state.
- ADR-005 and ADR-006 preserve Human-invoked lifecycle authority.
- ADR-010 classifies Duplicate `qh start` / Lifecycle Guard as the remaining
  REQUIRED-BEFORE-NEXT-MILESTONE item.
- This Task does not change Worker, Runner, Retry, scope, or Verification authority.

## Dependencies

- QH-V2-HARD-002 is COMPLETE - VERIFIED.
- QH-V2-DOC-001 is COMPLETE - VERIFIED and provides the published workflow baseline.
- QH-V2-DOC-002 is COMPLETE - VERIFIED and is the completed first queue stage.
- This is the first unfinished Backlog candidate and requires an explicit Human Task Gate
  before approval or `qh start`.

## Scope

- Add an entry guard to `command_start()` before any lifecycle write.
- Reject same-Task and different-Task starts while Current Task is ACTIVE.
- Reject malformed or non-complete Current lifecycle values fail closed.
- Require the target Task Status to be exactly
  `APPROVED - READY FOR CONTRACT BASELINE` before any lifecycle write.
- Reject PLANNED, DRAFT, COMPLETE, missing, duplicate, or malformed target status.
- Preserve the existing successful start transition from exact
  COMPLETE - VERIFIED state.
- Add focused lifecycle regression tests with byte-for-byte mutation checks.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-003.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `DECISIONS.md`
- `REQUIREMENTS.md`
- `PROJECT.md`
- `BACKLOG.md`

## Acceptance Criteria

1. Starting the same existing Task while Current Task is ACTIVE returns non-zero.
2. Starting a different existing Task while Current Task is ACTIVE returns non-zero.
3. Each rejected start leaves `STATUS.md` byte-for-byte unchanged.
4. Each rejected start leaves the current and target Task documents unchanged.
5. Current, Previous, Next Planned, and Task Baseline values remain unchanged on failure.
6. A malformed or non-COMPLETE - VERIFIED Current lifecycle fails closed before mutation.
7. Only an exact COMPLETE - VERIFIED Current lifecycle and exact target status
   `APPROVED - READY FOR CONTRACT BASELINE` may perform a normal start.
8. PLANNED, DRAFT, COMPLETE, missing, duplicate, or malformed target Task status
   returns non-zero and leaves STATUS/current/target Task bytes unchanged.
9. Normal start still moves Current to Previous, makes the explicit target ACTIVE,
   records the pre-start HEAD as Task Baseline, and clears the consumed Next pointer.
10. Existing missing-target and duplicate-lifecycle-field rejection behavior remains.
11. No Worker, Runner, Retry, Adapter, Repository tool, or Verification behavior changes.

## Verification

Run exactly:

`python -m unittest tests.test_qh.QhLifecycleStartGuardTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED Evidence reproduces same-ACTIVE and different-ACTIVE mutation risk.
- Focused RED Evidence proves DRAFT, PLANNED, COMPLETE, and malformed target
  contracts can reach start before this guard.
- Focused GREEN output records test count and exit 0.
- Before/after SHA-256 or exact bytes prove zero mutation for STATUS and both Task files.
- Full `tests.test_qh` regression passes.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`.
- Close output shows every Verification exit 0, no unexpected path, Diff Check 0,
  and Final Gate PASS.
- Lifecycle commit is separate and final `git status --short` is empty.

## Stop Conditions

STOP if completion requires:

- automatic next-Task selection, approval, or start;
- rewriting Task contracts during a failed lifecycle operation;
- changing Architecture, Requirements, or ADR-010;
- modifying Harness Core, Worker, Runner, Retry, Adapter, or Repository tools;
- weakening existing lifecycle tests or zero-mutation guarantees.

## Next Task

Queue successor candidate: QH-V2-HARD-004.

Human approval is required. Do not auto-start it.
