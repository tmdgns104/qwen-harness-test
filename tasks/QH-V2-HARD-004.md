# QH-V2-HARD-004 - Clean Worktree Lifecycle Invariant

## Status

COMPLETE - VERIFIED

## Problem

`qh start` records HEAD without enforcing the clean baseline required by FR-007.
`qh close` can also review an allowed dirty working tree and close a Task using a
HEAD commit that does not contain those dirty changes. This makes it ambiguous
which Repository state the lifecycle Evidence represents.

## Goal

Require clean, stable Git state for lifecycle start and completion, with rejected
operations producing no lifecycle mutation attributable to qh.

## Architecture Basis

- FR-007 requires a clean Git baseline before Worker execution.
- FR-006 and FR-008 require objective Evidence and safe failure.
- ADR-001 assigns Git baseline and changed-path Evidence to deterministic Harness code.
- ADR-007 makes `qh close` authoritative and prohibits stale Evidence reuse.
- `capture_git_baseline()` already defines clean status including staged,
  unstaged, and non-ignored untracked files.
- This is audit-derived Hardening, not an ADR-010 classified item.

## Dependencies

- QH-V2-HARD-003 must be COMPLETE - VERIFIED.
- The queue order avoids overlapping edits to `tools/qh.py` lifecycle behavior.
- Human approval is required before activation.

## Scope

- Reuse the existing clean-baseline definition for `qh start`.
- Require the requested close commit to resolve to entry HEAD before Verification.
- Require a clean worktree at close entry.
- After review/Verification and immediately before lifecycle writes, recheck that
  HEAD is unchanged and the worktree is clean.
- Reject staged, unstaged, deleted, and non-ignored untracked dirty states.
- Preserve ignored-file semantics and diagnostic `qh review` behavior.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-004.md`

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

1. Dirty unstaged state makes `qh start` return non-zero before lifecycle mutation.
2. Dirty staged state makes `qh start` return non-zero before lifecycle mutation.
3. Non-ignored untracked state makes `qh start` return non-zero before mutation.
4. Ignored artifacts retain existing `capture_git_baseline()` semantics.
5. `qh close` rejects a requested commit that is not entry HEAD before Verification.
6. `qh close` rejects dirty entry state before Verification.
7. After Verification, close rechecks that HEAD still equals the requested commit.
8. After Verification, close rechecks that the worktree remains clean.
9. Verification-created dirt or HEAD movement causes non-zero exit and qh performs
   no lifecycle write. Fixtures whose Verification does not target lifecycle files
   leave STATUS/current Task bytes identical.
10. Clean normal start and close behavior remains compatible.
11. Standalone `qh review` remains usable for dirty intermediate diagnostics.
12. No Verification, Final Gate, Worker, Runner, or Retry semantics change.

## Verification

Run exactly:

`python -m unittest tests.test_qh.QhCleanWorktreeLifecycleTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core.GitBaselineCaptureTests`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED covers unstaged, staged, untracked, Verification-dirty, and HEAD-change cases.
- Focused GREEN records exact test count and exit 0.
- STATUS and current Task byte comparisons prove zero qh lifecycle mutation; focused
  Verification-side-effect fixtures do not directly target those lifecycle files.
- Existing clean baseline and qh lifecycle regression modules pass.
- Ignored-artifact behavior is explicitly tested.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD and clean state are recorded before `qh close`.
- Close reports all Verification exit 0, no unexpected paths, Diff Check 0,
  and Final Gate PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- changing the Git clean definition or ignored-file policy;
- making standalone `qh review` clean-only;
- changing Verification execution, Final Gate, or Evidence schemas;
- rollback or sandboxing of arbitrary Verification-command side effects;
- modifying Worker, Runner, Retry, Adapter, or Repository tools;
- Architecture or Requirements changes.

## Next Task

Queue successor candidate: QH-V2-HARD-005.

Human approval is required. Do not auto-start it.
