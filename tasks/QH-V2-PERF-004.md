# QH-V2-PERF-004 - Verification Workflow Deduplication and Timing

## Status

COMPLETE - VERIFIED

## Parent

ADR-007 - Pre-Runner Verification Performance Optimization

## Problem

The normal human-invoked `qhops` workflow currently performs the Task's full
Verification during `qhops green` and then performs the same authoritative full
Verification again during `qhops finish` because `finish` invokes `qh close`.
As the regression suite grows, this duplicate execution materially increases Task
completion latency without adding stronger final Evidence.

Historical performance work already established two important facts:

- QH-V2-PERF-001 tested parallel Verification and measured only about 0.7% wall-clock
  improvement while individual suites slowed substantially, so concurrency was rejected.
- QH-V2-PERF-002 profiled `tests.test_qh`, and QH-V2-PERF-003 reduced the then-current
  22-test qh suite from 90.110 seconds to 46.899 seconds (about 48%) by reusing isolated
  seed Git Repository fixtures.

The suite has since grown materially. During QH-V2-HARD-005 GREEN, current Evidence
recorded:

- focused HARD-005 tests: 6 tests in 84.507 seconds;
- `tests.test_qh`: 48 tests in 414.872 seconds;
- `tests.test_harness_core`: 117 tests in 224.129 seconds;
- test-process time alone: approximately 723.508 seconds before command overhead.

The same full Task Verification then ran again inside authoritative `qh close` during
`qhops finish`.

## Goal

Reduce normal Task completion wall-clock time by removing duplicate full Verification
from the operator workflow while preserving the exact authoritative `qh close`
Verification, scope Evidence, Diff Check, clean-worktree invariant, and Final Gate.
Add lightweight wall-clock timing so future performance work is Evidence-driven.

## Architecture Basis

- ADR-007 is Accepted and defines `qh close` as the authoritative final lifecycle
  operation because it runs full Task Verification, scope Evidence, and Final Gate.
- ADR-007 recommends focused development tests and explicitly prioritizes redundant
  Verification removal before concurrency.
- Stale Verification Evidence reuse remains forbidden.
- QH-V2-PERF-001 rejected parallel Verification for the current workload.
- QH-V2-PERF-002 and QH-V2-PERF-003 established that measured optimization must
  preserve test isolation and must not weaken production Verification semantics.
- Harness Verification, Evidence, and Final Gate authority remain unchanged.

## Dependencies

- QH-V2-HARD-005 is COMPLETE - VERIFIED.
- QH-V2-PERF-001, QH-V2-PERF-002, and QH-V2-PERF-003 remain historical completed
  performance Evidence and are not reopened.
- This Task is intentionally prioritized before QH-V2-ARCH-008 because current
  Verification latency is materially affecting iteration speed.

## Canonical qhops Source

The current portable qhops operator helper has been imported without semantic
optimization into the Repository under `ops/qhops/` so future changes are auditable.
The canonical pre-implementation operator snapshot is the planning branch state at
commit `f331fcf70f45a82084ffa6c6406959819737078d`.

Tracked operator files are:

- `ops/qhops/qh_ops.py`
- `ops/qhops/qhops.cmd`
- `ops/qhops/install_qhops_path.cmd`
- `ops/qhops/README.md`

`qhops` remains an operator helper, not a Harness authority component. Harness Core,
`tools/qh.py`, scope evaluation, Verification Evidence, and Final Gate remain the
Source of Truth for completion.

## Scope

- Change `qhops green` so it executes only the focused Task Verification command used
  for GREEN development Evidence instead of the complete Task Verification contract.
- Do not push implementation history to `main` after focused GREEN alone.
- Keep the implementation commit local until authoritative final close succeeds.
- Change `qhops commit-impl` consistently so it does not require a duplicate full
  Verification before the later authoritative close.
- Preserve Task scope checks before implementation commit where applicable.
- Keep `qhops finish` as the authoritative final path: invoke `qh close <HEAD>` exactly
  once, create the separate lifecycle commit only after PASS, then perform the existing
  safe fast-forward push.
- Add lightweight wall-clock timing using `time.perf_counter()` or an equivalent
  monotonic high-resolution clock.
- Print stable timing labels for focused RED/GREEN, authoritative close, and overall
  finish duration.
- Print the authoritative full Verification execution count for the normal final path.
- Preserve Repository resolution, clean-state checks, safe-push behavior, and the
  explicit Human-invoked lifecycle model.
- Add focused operator-helper tests under `ops/qhops/tests/`.
- Capture before/after timing Evidence without creating a Verification cache or PASS receipt.

## Allowed Changes

- `ops/qhops/qh_ops.py`
- `ops/qhops/qhops.cmd`
- `ops/qhops/install_qhops_path.cmd`
- `ops/qhops/README.md`
- `ops/qhops/tests/test_qh_ops.py`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-PERF-004.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/qh.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `PROJECT.md`
- `BACKLOG.md` during implementation
- unrelated Task contracts
- test deletion, test skipping, weakened assertions, or cached/persisted PASS receipts
- Verification concurrency
- automatic next-Task start or queue advancement

All unlisted Repository paths remain default-denied.

## Acceptance Criteria

1. Normal `qhops green` does not execute `qh verify` or the complete Task Verification
   contract.
2. Normal `qhops green` executes the focused GREEN command exactly once and fails
   closed if that command fails.
3. Focused GREEN alone does not push implementation history to `main`.
4. The local implementation remains available for diagnosis/retry if final close fails.
5. `qhops commit-impl` follows the same no-duplicate-full-Verification principle while
   preserving scope checks and local implementation commit separation.
6. Normal `qhops finish` invokes authoritative `qh close <implementation HEAD>` exactly
   once and does not separately invoke `qh verify` or `qh review` first.
7. Full Task Verification remains mandatory inside `qh close` and is unchanged.
8. Final scope Evidence, Diff Check, Final Gate, and clean-worktree behavior remain
   unchanged.
9. A failed focused GREEN stops before final close and before any `main` push.
10. A failed authoritative close creates no lifecycle completion commit and pushes no
    invalid completed state.
11. A successful close creates the separate lifecycle commit and then pushes the
    implementation plus lifecycle history using the existing safe fast-forward policy.
12. Timing output includes at least focused command duration, authoritative close
    duration, finish total duration, and authoritative full Verification count.
13. Timing uses lightweight wall-clock measurement and does not alter command exit
    semantics.
14. No stale Verification result, cache, receipt, or prior PASS is treated as final
    Evidence.
15. No test is deleted, skipped, weakened, or omitted from the Task's authoritative
    final Verification contract for speed.
16. Before/after Evidence records full Verification execution count, absolute measured
    durations available from the workflow, and percentage reduction when comparable
    real-workload measurements exist.
17. HARD-005's measured pre-optimization sample remains the reference baseline; the
    first later real Task using the optimized qhops workflow must retain its timing
    output as post-change operational Evidence.
18. If duplicate removal does not materially improve workflow time, record that result
    rather than claiming success from expected savings.

## Verification

Run exactly:

`python -m unittest discover -s ops/qhops/tests -p "test_qh_ops.py"`

Then run:

`python -m py_compile ops/qhops/qh_ops.py`

Then run:

`git diff --check`

Then run:

`git status --short`

The operator-helper test suite must prove at minimum:

- focused GREEN calls the first/focused Verification command once and does not call
  `qh verify`;
- focused GREEN does not call safe push;
- failed focused GREEN stops;
- `commit-impl` does not perform duplicate full Verification;
- `finish` calls `qh close` exactly once;
- successful `finish` creates lifecycle commit then performs one safe push;
- failed `finish` performs no lifecycle commit and no push;
- timing labels are emitted without changing success/failure semantics.

## Evidence Requirements

- HARD-005 GREEN provides the measured pre-optimization sample: 84.507s, 414.872s,
  and 224.129s for its three Python test commands, approximately 723.508s of
  test-process time before overhead.
- Source inspection proves the baseline `qhops green` invokes full `qh verify` and
  baseline `qhops finish` invokes authoritative `qh close`, causing two full final-path
  Verification executions across normal GREEN + finish.
- RED/contract Evidence proves focused-only GREEN behavior is absent before modification.
- GREEN Evidence proves focused development behavior, no early push, and one final
  authoritative full Verification.
- Timing Evidence records focused RED/GREEN duration and final authoritative
  close/finish duration using stable labels.
- Failure-path Evidence proves no invalid lifecycle commit/push after focused or final
  failure.
- Final Repository changed paths remain within the approved exact scope.
- Exact implementation HEAD is used by Human-invoked `qh close`; Final Gate PASS is
  required before lifecycle completion.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- weakening or removing authoritative `qh close` full Verification;
- caching or reusing stale Verification Evidence;
- changing Harness Core, qh Final Gate, ChangeScope, or Verification semantics;
- deleting, skipping, or weakening tests for speed;
- reintroducing Verification concurrency rejected by PERF-001;
- granting qhops, Codex, Qwen, or Worker new autonomous lifecycle authority;
- changing Architecture or Requirements;
- automatic next-Task advancement.

## Next Task

Queue successor candidate: QH-V2-ARCH-008.

Under the current Architecture, completion does not auto-start the successor.
