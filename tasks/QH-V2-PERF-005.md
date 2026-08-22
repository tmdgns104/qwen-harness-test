# QH-V2-PERF-005 - Git-Heavy Test Fixture Performance Optimization Round

## Status

COMPLETE - VERIFIED

## Problem

After QH-V2-HARD-007, authoritative selected regression still takes several minutes on
the current Windows host even though duplicate full Verification was already removed.
Measured Evidence on 2026-08-22 shows:

- selected 259-test regression: 560.059 seconds, OK, one existing skip;
- `tests.test_qh`: 48 tests in 470.073 seconds;
- `tests.test_harness_core`: 119 tests in 207.330 seconds;
- the slowest cases are overwhelmingly Git baseline/evidence and qh review/close tests;
- `tests.test_harness_core` still constructs real temporary Git repositories repeatedly;
- `tests.test_qh` already reuses seed repositories in some classes, but Repository copy,
  Python process startup, Git subprocess, and close/review paths remain material.

PERF-001 rejected Verification concurrency because it improved wall clock by only about
0.7% while individual suites became slower. PERF-003 already proved that seed Repository
reuse can preserve isolation while reducing fixture cost. PERF-004 removed duplicate
full Verification from the normal operator workflow. The remaining problem is therefore
not permission to weaken Verification; it is repeated test-infrastructure work.

## Goal

Reduce real wall-clock time of the existing authoritative selected regression by
optimizing Git-heavy test fixture construction and isolation, while preserving the same
production behavior, Verification meaning, test coverage, fail-closed semantics, and
Git/Test Evidence strength.

## Architecture Basis

- ADR-001 keeps deterministic Git/Test Evidence authoritative.
- ADR-003 permits repeated, verified operational work to become deterministic utilities.
- ADR-007 explicitly prioritizes Evidence-driven Verification performance work and
  forbids stale PASS reuse.
- QH-V2-PERF-001 rejected parallel Verification for the current workload.
- QH-V2-PERF-003 established isolated seed Repository reuse as a valid test-only
  optimization when mutation does not leak between tests.
- QH-V2-PERF-004 removed duplicate full Verification while retaining `qh close` as the
  sole authoritative final path.
- ADR-011 classifies verified performance optimization that does not change Architecture
  or Trust Boundaries as Level A.
- ADR-013 terminates the remaining G1 autonomous queue authorization after HARD-007 and
  inserts this Human-approved performance round before OPS-001.

## Dependencies

- QH-V2-HARD-007 must be COMPLETE - VERIFIED.
- QH-V2-PERF-001 through QH-V2-PERF-004 remain completed historical Evidence and are
  not reopened.
- The G1 autonomous queue must no longer be used for progression after HARD-007.
- This Task uses the ordinary Human-controlled lifecycle and does not reseal a new
  autonomous manifest.

## Scope

Perform one measured optimization round in ordered stages.

### Stage A - Harness Core Git Fixture Reuse

- Replace repeated per-test `git init` / config / add / commit setup in Git-heavy
  `tests.test_harness_core` classes with a prebuilt immutable seed Repository and
  independent per-test copies where semantics permit.
- Preserve tests that intentionally exercise non-Repository or process-failure cases.
- Prove that tracked, staged, unstaged, untracked, ignored, deletion, rename, and HEAD
  mutations in one test do not leak into another test.

### Stage B - qh Test Repository Fixture Cost

- Profile the remaining `tests.test_qh` fixture/copy cost after Stage A.
- Compare safe test-only fixture strategies on the current Windows host before replacing
  the existing seed-copy implementation.
- Adopt a different copy/clone/worktree-like strategy only if it is measurably faster
  and preserves independent index, worktree, HEAD, ignored-file, and lifecycle state.
- Preserve real qh CLI subprocess execution for tests whose purpose is CLI behavior.

### Stage C Boundary

- If the remaining dominant cost is inside production `qh review` / `qh close` Git
  subprocess behavior rather than test fixture setup, stop this Task at the test-only
  boundary and propose a separate performance Task with fresh profiling Evidence.
- Do not modify production Harness/qh behavior inside PERF-005 merely to hit a timing
  target.

## Allowed Changes

- `tests/git_fixture_utils.py`
- `tests/test_git_fixture_utils.py`
- `tests/test_harness_core.py`
- `tests/test_qh.py`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-PERF-005.md`

## Forbidden Changes

- `tools/**`
- `ops/qhops/**`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- existing OPS Task contracts
- Worker, Runner, Retry, Repository-tool, Verification, Evidence, Final Gate, or
  lifecycle semantics
- test deletion
- new test skipping
- assertion weakening
- authoritative Verification reduction
- cached or persisted PASS reuse
- Verification concurrency

All unlisted Repository paths remain default-denied.

## Acceptance Criteria

1. Production files are byte-for-byte unchanged by this Task.
2. The selected regression still discovers and executes at least the same 259 tests and
   adds no skip beyond the one existing baseline skip.
3. `tests.test_qh` continues to execute at least the same 48 tests with no new skip.
4. `tests.test_harness_core` continues to execute at least the same 119 tests with no
   new skip.
5. Fixture-isolation tests prove that mutation of tracked files, index state, untracked
   files, ignored files, HEAD, deletion, and rename state in one test Repository cannot
   leak into a later independent fixture.
6. Stage A removes repeated Git Repository construction where the tests do not require
   construction itself as the subject under test.
7. Stage B changes the existing qh fixture strategy only after a same-host benchmark
   shows a measurable benefit and independence checks remain GREEN.
8. The final selected-regression wall clock is compared against the 560.059-second
   HARD-007-era baseline using the same command and host.
9. The target is at least 20% wall-clock reduction, i.e. 448.047 seconds or less; a
   30% reduction, 392.041 seconds or less, is the preferred goal.
10. If the measured gain is below 20%, the Task must report the actual result and must
    not claim the performance target was achieved; non-beneficial complexity is reverted
    rather than retained merely to complete the Task.
11. No improvement may trade away deterministic correctness, fail-closed behavior,
    Git Evidence, Verification completeness, or Final Gate strength.
12. Any required production-code optimization is deferred to a separate approved Task.

## Verification

Run exactly:

`python -m unittest tests.test_git_fixture_utils`

Then run:

`python -m unittest --durations 30 tests.test_qh tests.test_harness_core tests.test_repo_tools tests.test_task_runner tests.test_retry_runner tests.test_ollama_worker tests.test_qh_worker_run tests.test_text_utils tests.test_report_utils`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Preserve the baseline measurements: 259 tests / 560.059s, `tests.test_qh` 48 /
  470.073s, and `tests.test_harness_core` 119 / 207.330s.
- Record Stage A before/after `tests.test_harness_core` wall clock.
- Record Stage B before/after `tests.test_qh` wall clock if Stage B changes are retained.
- Record final selected-regression count, skip count, wall clock, absolute seconds saved,
  and percentage improvement against 560.059s.
- Prove fixture independence with deterministic tests rather than assuming copied `.git`
  state is isolated.
- Show no production path in baseline-to-implementation changed paths.
- Show no test deletion, added skip, or weakened assertion used to obtain the timing gain.
- Exact implementation HEAD is used by `qh close`; all Verification commands exit 0,
  no unexpected path is reported, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- modifying `tools/**` or `ops/qhops/**`;
- reducing authoritative Verification coverage;
- deleting or skipping tests;
- reusing stale/cached PASS Evidence;
- reintroducing Verification concurrency rejected by PERF-001;
- sharing mutable Git worktree/index state between tests;
- changing Harness, Worker, Runner, Retry, Final Gate, or lifecycle semantics;
- changing Architecture or Trust Boundaries;
- modifying or resealing the retired G1 manifest;
- hiding a sub-20% result instead of recording it.

## Next Task

Queue successor candidate: QH-V2-OPS-001.

After PERF-005 completion, progression returns to the ordinary Human-controlled Task
lifecycle unless a separate later Human decision authorizes another exact manifest.

## Completion Evidence

- Stage A same-host `tests.test_harness_core`: 130.997s -> 54.394s, saving 76.603s (58.48%).
- Stage B fixture microbenchmark: `QhPostVerificationEvidenceRefreshTests` 1.796s/test -> 0.026s/test; `QhCleanWorktreeLifecycleTests` 2.810s/test -> 0.037s/test.
- Stage B adjacent `tests.test_qh` measurement: 508.527s -> 496.796s, saving 11.731s (2.31%). Host-load variability was observed, so earlier 282.076s is retained as context and is not used as causal Stage B evidence.
- Final selected regression: 259 tests in 422.114s, OK, skipped=1. External stopwatch: 422.363s.
- Baseline selected regression: 259 tests in 560.059s, skipped=1.
- Final saving against baseline: 137.945s, 24.63% improvement.
- Acceptance target <=448.047s (20% reduction): ACHIEVED.
- Preferred target <=392.041s (30% reduction): NOT ACHIEVED.
- Exact implementation HEAD used by `qh close`: 204dedd.
- `qh close`: all Verification commands exit 0, Diff Check 0, Unexpected Changed Paths no, Final Gate PASS.
- Production `tools/**` and `ops/qhops/**` were not modified.
- Remaining dominant cost is production qh review/close Git subprocess behavior; further production optimization is deferred beyond PERF-005 Stage C boundary.
