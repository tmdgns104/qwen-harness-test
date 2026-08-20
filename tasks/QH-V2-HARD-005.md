# QH-V2-HARD-005 - Post-Verification Evidence Refresh

## Status

PLANNED

## Problem

`command_review()` currently collects changed paths before running the Task's
Verification commands and assembles Evidence from that earlier tuple. A zero-exit
Verification command can create, modify, or delete a path after the snapshot.
The Final Gate can therefore describe a Repository state that is no longer final.
`git diff --check` does not make that changed-path Evidence authoritative and may
not report a well-formed forbidden untracked file.

## Goal

Make review and close evaluate authoritative changed-path and scope Evidence from
the Repository state after all Task Verification commands finish.

## Architecture Basis

- FR-005 requires actual Repository changes to be checked against Task scope.
- FR-006 requires independent, objective completion Evidence.
- ADR-001 assigns changed-path Evidence and Final Gate inputs to deterministic Harness code.
- ADR-007 prohibits stale Verification Evidence and keeps `qh close` authoritative.
- The current code order confirms the gap exists.
- This is audit-derived Hardening, not an ADR-010 classified item.

## Dependencies

- QH-V2-HARD-004 must be COMPLETE - VERIFIED.
- The clean lifecycle invariant provides the close-time safety check while this
  Task corrects the content of review Evidence.
- Human approval is required before activation.

## Scope

- Run the parsed Task Verification contract exactly once and in document order.
- Collect the authoritative changed paths after all Task Verification commands.
- Assemble scope Evidence and evaluate Final Gate from that post-Verification tuple.
- Run Diff Check after Task Verification without rerunning the Task contract.
- Add focused regressions for allowed and forbidden Verification side effects.
- Preserve non-mutating review output and behavior.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `STATUS.md`
- `tasks/QH-V2-HARD-005.md`

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

1. A pre-Verification changed-path snapshot is not used as authoritative Evidence.
2. Every Task Verification command executes exactly once and in contract order.
3. Changed paths are collected after the last Task Verification side effect.
4. Evidence assembly and Final Gate use the refreshed changed-path tuple.
5. A zero-exit Verification command that creates a forbidden untracked path makes
   review print that path as forbidden, report Unexpected Changed Paths yes,
   report Final Gate FAIL, and return non-zero.
6. Verification modification or deletion of a forbidden path is likewise detected.
7. A Verification-created allowed path is reported from final Repository state as allowed.
8. Diff Check occurs after Task Verification and remains a separate required success.
9. Non-mutating Verification preserves existing review output and success behavior.
10. A close failure caused by refreshed Evidence leaves lifecycle files unchanged.
11. No Verification command caching, duplicate execution, sandbox expansion, or
    Harness Evidence/Final Gate schema change is introduced.

## Verification

Run exactly:

`python -m unittest tests.test_qh.QhPostVerificationEvidenceRefreshTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED proves a forbidden Verification side effect is absent from old Evidence.
- Focused GREEN proves allowed/forbidden create, modify, and delete cases use final state.
- A call-order test proves one Verification execution followed by Evidence refresh.
- Lifecycle files are byte-identical after rejected close.
- Full qh and Harness Core regression modules pass.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by authoritative `qh close`.
- Close reports every command exit 0, no unexpected path, Diff Check 0,
  and Final Gate PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- changing `HarnessEvidence` or Final Gate semantics;
- new Verification authority, command sandboxing, caching, or persisted receipts;
- rerunning the Task Verification contract to obtain fresh Evidence;
- Worker, Runner, Retry, Adapter, or Repository-tool changes;
- Architecture or Requirements changes.

## Next Task

Queue successor candidate: QH-V2-HARD-006.

Human approval is required. Do not auto-start it.
