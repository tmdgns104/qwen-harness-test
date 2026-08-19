# QH-V2-PERF-003 - Seed Repository Test Fixture Optimization

## Status

COMPLETE - VERIFIED

## Parent

QH-V2-PERF-002 - Profile qh Test Bottlenecks

## Goal

Reduce tests.test_qh wall-clock time by eliminating repeated baseline Git Repository construction while preserving complete per-test isolation and all existing behavioral assertions.

## Evidence

- tests.test_qh baseline is approximately 80-90 seconds for 22 tests.
- QhStatusCliTests.setUp executes 8 Git commands for every test.
- This produces at least 176 Git subprocesses from common setup alone.
- A simple status test spent approximately 61% of its runtime in common setUp.
- Production qh logic is not currently supported as the primary bottleneck.

## Scope

- Change only tests.test_qh fixture construction.
- Build a known-good seed Repository once for the test class or suite.
- Give every test an independent mutable copy of that seed Repository.
- Preserve current Git history, persisted Task Baseline semantics, lifecycle state, and test isolation.
- Do not share a mutable Repository between tests.
- Do not change production qh behavior.
- Measure full tests.test_qh before and after.

## Allowed Changes

- tests/test_qh.py
- STATUS.md
- tasks/QH-V2-PERF-003.md

## Forbidden Changes

- tools/**
- tests/test_harness_core.py
- tests/test_repo_tools.py
- tests/test_ollama_worker.py
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- existing Task files
- all other Repository files

## Acceptance Criteria

1. All existing tests.test_qh tests remain behaviorally unchanged and PASS.
2. Every test receives an independent Repository copy.
3. No mutable Repository state leaks between tests.
4. Baseline and persisted Task Baseline Git semantics remain unchanged.
5. No production code changes.
6. Full tests.test_qh wall-clock time improves materially versus the recorded 80-90 second baseline.
7. tests.test_harness_core and tests.test_repo_tools regressions remain PASS.
8. git diff --check passes.
9. No unexpected changed paths.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python -m unittest tests.test_repo_tools`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop if fixture sharing weakens test isolation, changes Git semantics, causes any regression, or does not produce material wall-clock improvement.

## Implementation Result

- Implementation commit: 7a8a5f6
- Production code was not changed.
- QhStatusCliTests now builds the baseline Git Repository once in setUpClass.
- Each test receives its own independent copy of the seed Repository, including .git history.
- No mutable Repository is shared between tests.

## Performance Evidence

Before optimization:

- tests.test_qh: 22 tests in 90.110 seconds.

After optimization:

- tests.test_qh: 22 tests in 46.899 seconds.
- Improvement: 43.211 seconds.
- Wall-clock reduction: approximately 48%.

The previously profiled simple status test dropped from approximately 4.066 seconds total to a 1.342 second test duration within the full suite.

## Isolation Evidence

A dedicated isolation probe:

- modified the first per-test Repository copy;
- confirmed the seed Repository remained unchanged;
- created a second Repository copy;
- confirmed the first test's mutation did not appear there.

Result: ISOLATION PASS.

## Regression Evidence

- tests.test_qh: 22 PASS.
- tests.test_harness_core: 109 PASS.
- tests.test_repo_tools: 13 PASS.
- git diff --check: PASS.
- No production files changed.

## Conclusion

The seed Repository fixture optimization is accepted.

It materially reduces tests.test_qh runtime while preserving independent mutable Repository state, Git history semantics, lifecycle behavior, and existing assertions.
