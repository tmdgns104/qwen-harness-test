# QH-V2-PERF-002 - Profile qh Test Bottlenecks

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-007 - Pre-Runner Verification Performance Optimization

## Goal

Measure where tests.test_qh spends its runtime before choosing any further performance implementation.

## Evidence

- Sequential tests.test_qh baseline: approximately 80.274 seconds.
- Parallel Verification was rejected after 138.45s -> 137.55s (~0.7% improvement).
- Parallel execution increased tests.test_qh runtime to 136.650 seconds.
- Further optimization therefore requires per-test and repeated-operation profiling first.

## Scope

- Measure per-test runtime in tests.test_qh.
- Identify the slowest tests and repeated Git/subprocess/temp-repository operations.
- Do not optimize implementation in this Task.
- Rank concrete optimization candidates by expected benefit and safety.

## Allowed Changes

- STATUS.md
- tasks/QH-V2-PERF-002.md

## Forbidden Changes

- tools/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- existing Task files
- all other Repository files

## Acceptance Criteria

1. Obtain per-test timing Evidence for tests.test_qh.
2. Identify the dominant runtime contributors.
3. Distinguish test-fixture cost from production-code cost.
4. Recommend the smallest safe optimization Task.
5. Do not change production or test implementation.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after profiling Evidence, recommendation, review, close, and clean working tree.

## Profiling Result

### Full tests.test_qh timing

- 22 tests completed in 90.110 seconds during per-test duration profiling.
- No single pathological test dominates runtime.
- Individual tests ranged from approximately 2.4 seconds to 7.4 seconds.
- All 22 tests belong to QhStatusCliTests.

### Common fixture evidence

QhStatusCliTests.setUp creates a new temporary Git Repository for every test and executes:

1. git init
2. git config user.email
3. git config user.name
4. git add .
5. git commit baseline
6. git rev-parse HEAD
7. git add STATUS.md
8. git commit persisted baseline

Across 22 tests, this means at least 176 Git subprocess executions from common setup alone.

### Simple status test profile

test_status_reports_current_task_task_file_clean_git_and_scope:

- Total: 4.066 seconds.
- setUp: 2.479 seconds (~61%).
- Eight setup Git calls: 2.468 seconds.
- Total subprocess.run calls: 9.
- The actual test body, including qh status execution, accounted for the remaining approximately 1.56 seconds.

### Slow close test profile

test_close_rejects_non_head_commit_without_modifying_lifecycle_files:

- Total: 7.271 seconds.
- Total subprocess.run calls: 17.
- Total subprocess cumulative time: 7.223 seconds.
- Total _git calls: 16, cumulative 4.633 seconds.
- Common setUp: 2.385 seconds.
- Windows CreateProcess cumulative cost: 1.263 seconds.

### Diagnosis

The dominant tests.test_qh runtime is test infrastructure cost, especially repeated Git process creation and per-test Repository construction.

The Evidence does not indicate that qh production logic itself is the primary cause of the approximately 80-90 second suite runtime.

## Recommendation

Create a separate implementation Task to optimize only tests.test_qh fixture construction.

Preferred first experiment:

- Build one known-good baseline seed Repository for the test class or suite.
- Give every test its own independent copy of that seed Repository.
- Preserve complete test isolation.
- Do not share a mutable working Repository between tests.
- Preserve all current lifecycle, Git-range, and fail-closed assertions.
- Measure full tests.test_qh before and after.
- Keep the optimization only if regressions remain PASS and wall-clock improvement is material.

Do not optimize qh production code based on current profiling Evidence.
