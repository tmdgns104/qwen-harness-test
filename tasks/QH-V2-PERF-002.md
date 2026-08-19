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
