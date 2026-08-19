# QH-V2-ARCH-005 - Pre-Runner Verification Performance Review

## Status

COMPLETE - VERIFIED

## Goal

Decide whether evidence-backed Verification performance work should be moved before Single-Task Runner without weakening HC-004 authority, final Verification, or Human Gates.

## Evidence

- Full verify currently runs tests.test_qh, tests.test_harness_core, tests.test_repo_tools sequentially.
- Recent full verify required roughly 81s + 58s + negligible repo-tools time.
- review and close repeat the same Verification contract.
- The Human requested performance improvement immediately after QH-V2-AUTO-005.

## Review Candidates

1. Focused/Fast Verification for development loops.
2. Parallel execution only for independent test suites.
3. Safe reuse of Verification Evidence across verify -> review -> close when HEAD, Task baseline, Task contract, and working tree state are unchanged.
4. Profiling tests.test_qh subprocess/Git fixture cost.

## Boundaries

- No performance implementation in this Task.
- HC-004 remains authoritative.
- Final authoritative Verification must remain fail-closed.
- No stale Evidence reuse.
- No automatic PASS, commit, completion, Architecture mutation, or next-Task start.

## Allowed Changes

- DECISIONS.md
- STATUS.md
- tasks/QH-V2-ARCH-005.md

## Forbidden Changes

- tools/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- existing Task files
- all other Repository files

## Acceptance Criteria

- Decide whether a targeted performance phase may occur before Runner.
- Define which optimization is safest to implement first.
- Preserve authoritative final Verification semantics.
- Record the decision in DECISIONS.md and STATUS.md.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after decision, review, commit, close, and clean working tree.
