# QH-V2-PERF-001 - Parallel Independent Verification Commands

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-007 - Pre-Runner Verification Performance Optimization

## Goal

Reduce authoritative Verification wall-clock time by allowing explicitly independent verification commands to run concurrently without changing HC-004 ownership, Evidence semantics, or Final Gate behavior.

## Scope

- Add the minimum Harness/Core and workflow support required for explicitly independent Verification commands.
- Preserve sequential execution as the default.
- Parallelism must be opt-in and deterministic at the contract level.
- Git state checks, Evidence assembly, scope evaluation, and Final Gate remain sequential.
- Capture before/after runtime Evidence using the existing AUTO-005-style full Verification workload.

## Allowed Changes

- tools/harness_core.py
- tools/qh.py
- tests/test_harness_core.py
- tests/test_qh.py
- STATUS.md
- tasks/QH-V2-PERF-001.md

## Forbidden Changes

- tools/repo_tools.py
- tools/ollama_worker.py
- tests/test_repo_tools.py
- tests/test_ollama_worker.py
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- existing Task files
- all other Repository files

## Acceptance Criteria

1. Existing sequential Verification behavior remains the default and passes all regressions.
2. Only commands explicitly designated as independent may execute concurrently.
3. Parallel results preserve contract command order in returned Evidence regardless of completion order.
4. A failing command remains a failing Verification result and cannot be hidden by parallel execution.
5. Process-start errors remain fail-closed.
6. Git diff/status checks, Evidence assembly, and Final Gate are not parallelized.
7. Authoritative full Verification remains mandatory in qh close.
8. Focused development tests remain non-authoritative.
9. Measured wall-clock Evidence demonstrates whether parallel execution materially improves the current full Verification workload.

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

Stop on any architecture ambiguity, unsafe concurrency interaction, regression, scope violation, or inability to preserve deterministic Evidence ordering.
