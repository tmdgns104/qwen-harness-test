# QH-V2-OPS-005 - qh status UX

## Status

PLANNED

## Problem

The current read-only status command shows the current Task ID/file, HEAD-relative
dirty paths, and scope, but beginners must manually combine STATUS fields, persisted
baseline, and Git output to understand lifecycle state. Mixing worktree changes with
baseline-to-current-state Task-range Evidence can also produce incorrect conclusions.

## Goal

Extend `qh status` as a read-only factual view that clearly separates lifecycle,
persisted baseline, current HEAD/worktree state, Task-range paths, scope classification,
and non-authoritative next-step guidance.

## Architecture Basis

- ADR-005 defines Human-driven automation and lifecycle authority.
- Completed QH-V2-AUTO-002, QH-V2-AUTO-003, and QH-V2-AUTO-005 define the
  implemented lifecycle, failure, and persisted-baseline facts shown by status.
- ADR-006 identifies status UX as a deferred operations improvement.
- ADR-007 distinguishes persisted baseline, changed-path Evidence, review, and close.
- ADR-010 classifies qh status UX as SAFE-TO-DEFER.
- Status remains presentation only and does not own Verification or completion authority.

## Dependencies

- QH-V2-OPS-004 must be COMPLETE - VERIFIED in the deterministic queue.
- The dependency is governance ordering rather than a technical dependency on live smoke.
- Human approval is required before activation.

## Scope

- Display the full Current lifecycle value and state, Previous Task, and Next Planned Task.
- Display Task Baseline and whether it resolves, current HEAD, and working-tree clean/dirty.
- Separately display baseline-to-current-state Task-range changed paths and
  HEAD-relative worktree paths using unambiguous labels.
- Classify reported Task-range paths as Allowed or Forbidden using existing scope authority.
- Preserve existing status labels where compatibility matters.
- If guidance is shown, label it as non-authoritative safe guidance rather than PASS prediction.
- Fail closed and without mutation for malformed lifecycle or invalid baseline state.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `README.md`
- `docs/QUICKSTART.md`
- `docs/HOW_IT_WORKS.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-005.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/qh_doctor.py`
- `tools/ollama_worker.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/repo_tools.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. Status displays Current lifecycle/state, Previous, Next Planned, Task Baseline,
   current HEAD, and baseline validity with stable labels.
2. HEAD-relative working-tree cleanliness and persisted-baseline Task-range paths are
   visually and semantically distinct.
3. Allowed and Forbidden classification is shown for Task-range changed paths.
4. Existing core status labels and direct CLI use remain compatible.
5. Success, dirty, malformed, and invalid-baseline paths leave all Repository bytes unchanged.
6. Malformed lifecycle or invalid baseline returns non-zero and fails closed.
7. Status does not run Verification, contact Ollama/network, cache Evidence, mutate
   lifecycle, or call start/close.
8. Status does not infer Task PASS, Final Gate PASS, COMPLETE, or approval.
9. Any next-step text is explicitly non-authoritative guidance derived from visible state.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python tools/qh.py status`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Fixture coverage includes complete/active lifecycle, clean/dirty worktree, committed
  Task range, forbidden path, malformed lifecycle, and invalid baseline.
- Before/after byte and Git-status snapshots prove read-only behavior on success and failure.
- Tests prove Verification, Ollama, and network subprocesses are not invoked.
- Output assertions distinguish worktree paths from baseline-range paths.
- Existing qh and Harness Core regressions pass.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by `qh close`; all Verification exits are 0,
  unexpected paths are absent, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- mutating Repository or lifecycle state from status;
- executing/caching Verification or predicting Final Gate/completion;
- automatic Task selection, start, review, or close;
- merging doctor with status through a broad CLI redesign;
- Harness, Worker, Runner, Retry, Adapter, Repository-tool, or Architecture changes.

## Next Task

Queue successor candidate: QH-V2-OPS-006.

Human approval is required. Do not auto-start it.
