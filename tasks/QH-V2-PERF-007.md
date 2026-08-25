# QH-V2-PERF-007 - New Git-Heavy Test Fixture Optimization and Controlled Benchmark

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-V2-PERF-006 improved authoritative `qh close` observability but did not solve the runtime problem. The exact PERF-006 close recorded `tests.test_qh` at 1232.5 seconds and the review phase at 1457.5 seconds, which is not practical for routine Agent development.

A post-PERF-006 read-only Codex field analysis inspected the current production/test code and reported two dominant contributors:

1. fourteen Git-heavy tests added after QH-V2-PERF-005 use repeated per-test Repository construction instead of the isolated seed/scenario-copy strategy already proven in PERF-005;
2. the current Windows host shows materially higher Git subprocess latency than earlier measured runs.

The field analysis reported the following preliminary values:

- `tests.test_qh`: 48 tests / 496.796s near PERF-005 versus 62 tests / 1232.5s in PERF-006;
- new `QhUnsuccessfulLifecycleTests`: 7 tests;
- new `HandoffCheckTests`: 7 tests;
- the two new classes together: about 475.929s in one focused run;
- preliminary static/runtime accounting: about 257 explicit Git subprocesses and 19 Python/qh child invocations across the two classes;
- current host sample `git rev-parse HEAD`: about 1.513s average;
- the same 119-test `tests.test_harness_core` source measured 54.394s in PERF-005-era Evidence and 166.6s during PERF-006 close.

These field-analysis values are not authoritative Repository Evidence until this Task independently reproduces and records them. In particular, antivirus, disk, CPU, thermal, power, or other host causes remain UNVERIFIED without separate telemetry.

The first safe optimization candidate is therefore test-infrastructure-only: reuse the already verified independent seed/scenario-copy approach for the two newly added Git-heavy classes while preserving their real Git/qh behavior and isolation.

## Goal

Reduce the deterministic setup/process cost of `QhUnsuccessfulLifecycleTests` and `HandoffCheckTests` without changing production code, test meaning, Verification coverage, fail-closed behavior, or Git/Test Evidence strength.

At the same time, collect controlled same-host benchmark Evidence that separates code/fixture improvement from host process-latency variation well enough to decide whether a later Architecture review of Verification strategy is necessary.

This Task does not split Task-scoped Verification from repository-wide regression. That is a possible later Architecture decision only if practical runtime is still not achieved after the low-risk fixture optimization.

## Human Selection

2026-08-25 Human approved inserting this Task before QH-V2-OPS-004 after reviewing the PERF-006 result and the Codex field analysis.

Approved queue intent:

`QH-V2-PERF-006 -> QH-V2-PERF-007 -> QH-V2-OPS-004`

The Human also established the practical operating concern that routine authoritative close taking more than about 5 minutes is not acceptable as the long-term normal workflow. This is a performance target and decision trigger; it does not authorize weakening Verification.

## Architecture Basis

- Repository documents and Git/Test Evidence are the Source of Truth.
- QH-V2-PERF-003 and QH-V2-PERF-005 already established isolated seed Repository reuse as an acceptable test-only optimization when independence is proven.
- QH-V2-PERF-004 keeps `qh close <exact implementation HEAD>` as the authoritative final Verification path and rejects duplicate full Verification in the normal workflow.
- QH-V2-PERF-001 rejected Verification concurrency for the current workload.
- QH-V2-PERF-006 preserves sequential Verification, exact exit semantics, Final Gate authority, and fresh Evidence while adding progress/heartbeat observability.
- Production Harness/qh behavior is outside this Task.
- Test deletion, test skipping, weakened assertions, mocked replacement of real Git/qh behavior, cached PASS reuse, and stale Verification Evidence are forbidden.
- FR-004 Worker successor restrictions remain unchanged.
- `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.

## Dependencies

- QH-V2-PERF-006 = `COMPLETE - VERIFIED`.
- QH-V2-PERF-006 implementation commit = `d4befcb41dabf230ded83938c83546db1b716700`.
- QH-V2-PERF-006 lifecycle commit = `b2a060da0ad81e9e3b30ca73b0bf29ebdac0b2a4`.
- QH-V2-PERF-003 and QH-V2-PERF-005 remain historical performance/isolation Evidence and are not reopened.
- QH-V2-OPS-004 must not start before this Task reaches a terminal disposition and the post-task runtime decision is reviewed.

## Scope

### Stage A - Reproduce Baseline and Host Probes

Before changing fixture behavior:

- reproduce a focused timing of exactly `QhUnsuccessfulLifecycleTests` plus `HandoffCheckTests` once;
- record exact discovered test count and skip count;
- record Git subprocess and Python/qh child counts for the focused path using deterministic instrumentation or source/runtime accounting that does not alter production behavior;
- run a lightweight controlled three-sample host probe that records Git process latency and Python process latency using the same commands before and after implementation;
- keep the host probe bounded so the benchmark itself does not become another long regression suite.

The controlled three-sample probe must use the same command, repetition count, Repository state, and reporting method before and after.

### Stage B - Seed / Scenario Fixture Optimization

Optimize only these existing classes:

- `QhUnsuccessfulLifecycleTests`
- `HandoffCheckTests`

Use the PERF-005-style independent seed/scenario-copy strategy where semantics permit.

Requirements:

- every test still receives an independent worktree/index/HEAD state;
- tracked, staged, unstaged, untracked, ignored, deletion, rename, branch/ref, diverged-history, merge-history, and lifecycle state used by these tests must not leak between tests;
- special Git histories may be prebuilt as immutable scenario seeds and independently copied if this preserves the exact scenario under test;
- tests whose purpose specifically requires construction behavior must retain the required real construction step;
- real qh CLI subprocess execution must remain real where CLI behavior is the subject under test;
- real Git semantics must not be replaced by mocks merely for speed;
- no production file may change.

### Stage C - Controlled After Measurement

After focused GREEN and fixture-isolation proof:

- rerun exactly the same focused two-class timing once;
- rerun the exact same three-sample host probes;
- report before/after wall clock, absolute seconds saved, percentage improvement, Git subprocess count change, Python/qh child count change, test count, and skip count;
- distinguish measured fixture improvement from host-latency movement rather than attributing all timing change to code.

### Stage D - Authoritative Full Result

Do not repeatedly run the full `tests.test_qh` suite during development.

After implementation stabilization and implementation commit:

- authoritative `qh close <exact implementation HEAD>` runs the Task Verification exactly once;
- record final `tests.test_qh` duration and authoritative close/review duration from PERF-006 progress timing;
- use that result for the practical-runtime decision below.

## Practical Runtime Decision

After authoritative final Verification:

- if `tests.test_qh` and normal authoritative close are both within 300 seconds under the measured run, QH-V2-OPS-004 may remain the next successor candidate;
- if either remains above 300 seconds, do not auto-start QH-V2-OPS-004. Record the actual result and request a Human/ChatGPT Architecture review of Verification strategy, including whether Task-scoped authoritative regression and repository-wide integration regression should be separated without weakening release/milestone assurance.

The 300-second trigger does not permit deleting, skipping, caching, parallelizing, or bypassing tests.

## Allowed Changes

- `tests/git_fixture_utils.py`
- `tests/test_git_fixture_utils.py`
- `tests/test_qh.py`
- `tests/test_qh_perf_fixture.py`
- `docs/DEVELOPMENT.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-PERF-007.md`

## Forbidden Changes

- `tools/**`
- `ops/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `README.md`
- current Task other than `tasks/QH-V2-PERF-007.md`
- production Harness/qh/Worker/Runner/Retry behavior
- Verification command deletion or reduction
- test deletion
- new test skip
- assertion weakening
- replacement of real Git/qh integration semantics with mocks for speed
- shared mutable Git worktree/index state between tests
- stale or cached PASS reuse
- persisted Verification receipt reuse
- Verification concurrency or parallel suite execution
- model / `think` / timeout / Worker step budget / Retry policy changes
- tool schema / tool authority changes
- Final Gate / ChangeScope / lifecycle authority changes
- Git push/branch authority expansion
- automatic successor start
- unattended queue authority
- Globalization approval

All unlisted Repository paths remain default-denied.

## Acceptance Criteria

1. Production files remain byte-for-byte unchanged by this Task.
2. `QhUnsuccessfulLifecycleTests` still discovers and executes at least 7 tests with no new skip.
3. `HandoffCheckTests` still discovers and executes at least 7 tests with no new skip.
4. Existing assertions and real Git/qh behavior are preserved or strengthened, never weakened.
5. Deterministic isolation tests prove scenario mutation in one copied fixture cannot leak into another.
6. Special unsuccessful-lifecycle Evidence-path cases remain fail closed exactly as before.
7. Handoff classifications including fast-forward-safe, already-applied/exact, already-contained, dirty, diverged, and merge-history stop cases remain semantically unchanged.
8. The optimized focused two-class path materially reduces repeated Repository-construction Git subprocesses compared with the reproduced baseline.
9. Target focused wall-clock improvement is at least 20% on the adjacent same-host before/after measurement. If host probes move materially, report both raw and host-contextualized results rather than hiding variance.
10. Retained fixture complexity must show either at least 20% focused wall-clock improvement or at least 40% deterministic setup Git-subprocess reduction with no focused wall-clock regression beyond measured host-probe variance.
11. If neither threshold is met, revert non-beneficial complexity and report the actual result instead of claiming success.
12. Three-sample before/after host probes use identical methodology and are recorded.
13. Full `tests.test_qh` is not repeatedly executed during development merely for reassurance.
14. The authoritative final `qh close` executes the approved Verification once at the exact implementation HEAD.
15. Final `tests.test_qh` duration and close/review duration are recorded.
16. `BACKLOG.md` reflects `QH-V2-PERF-006 -> QH-V2-PERF-007 -> QH-V2-OPS-004`.
17. If final routine runtime remains above the 300-second practical trigger, OPS-004 is not auto-started and an Architecture review is requested.
18. No Verification concurrency, stale PASS reuse, test skip, or Final Gate weakening is introduced.
19. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
20. Allowed Changes only occur and `git diff --check` passes.

## Verification

Run exactly:

`python -m unittest tests.test_git_fixture_utils`

Then run:

`python -m unittest tests.test_qh.QhUnsuccessfulLifecycleTests tests.test_qh.HandoffCheckTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -c "from pathlib import Path; b=Path('BACKLOG.md').read_text(encoding='utf-8'); required=['QH-V2-PERF-006','QH-V2-PERF-007','QH-V2-OPS-004']; missing=[x for x in required if x not in b]; assert not missing,missing; assert b.index('QH-V2-PERF-006') < b.index('QH-V2-PERF-007') < b.index('QH-V2-OPS-004')"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Verification Budget

- During implementation use only fixture-isolation tests and the two focused classes needed for RED/GREEN/debugging.
- Controlled three-sample host probes are measurement Evidence, not repeated full regression.
- Do not run full `tests.test_qh` separately after implementation stabilization merely to preview final close.
- The final authoritative full `tests.test_qh` run occurs inside `qh close <exact implementation HEAD>` once.
- If authoritative close fails deterministically, Analyze -> Fix -> focused re-test -> new exact implementation commit -> authoritative close is permitted; do not reuse the failed result as PASS Evidence.

## Evidence Requirements

- exact contract baseline SHA
- PERF-006 exact timing basis: `tests.test_qh` 1232.5s and review 1457.5s
- independently reproduced focused two-class baseline count/time
- independently reproduced focused Git/Python child process accounting
- three-sample pre-change Git/Python host probe results
- fixture design explanation identifying immutable seed/scenario boundaries
- deterministic isolation test Evidence
- focused RED -> GREEN Evidence
- same focused two-class after count/time
- after Git/Python child process accounting
- identical three-sample post-change host probe results
- before/after absolute and percentage improvement
- explanation of host-probe movement and what remains UNVERIFIED
- final authoritative `tests.test_qh` duration
- final authoritative close/review duration
- explicit practical-runtime disposition: `<=300s` or `>300s - ARCHITECTURE REVIEW REQUIRED`
- changed paths confined to Allowed Changes
- `git diff --check` PASS
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS
- separate lifecycle commit
- safe fast-forward push and final clean working tree

## Stop Conditions

STOP and request Human/ChatGPT review if completion requires:

- changing production `tools/**` or `ops/**` behavior;
- weakening Verification coverage or Final Gate semantics;
- deleting/skipping tests or weakening assertions;
- mocking away real Git/qh behavior whose integration semantics are under test;
- sharing mutable fixture state between tests;
- stale/cached PASS reuse;
- Verification concurrency or command parallelization;
- Architecture or Requirements changes;
- Trust Boundary or authority changes;
- Windows security changes such as antivirus exclusions;
- destructive Git recovery or branch divergence resolution;
- Globalization;
- a Verification-strategy split inside this Task.

Host-load variability alone is not a reason to fabricate a performance claim. Record the measured values and retain only deterministic, safety-preserving improvements.

## Next Task

If QH-V2-PERF-007 is `COMPLETE - VERIFIED` and final routine runtime is at or below the 300-second practical trigger, successor candidate:

`QH-V2-OPS-004`

If final routine runtime remains above 300 seconds:

`HUMAN/CHATGPT ARCHITECTURE REVIEW - Verification Strategy and Regression Tiering`

Qwen Worker itself never selects or starts a successor. `GLOBALIZATION = NOT AUTHORIZED`.