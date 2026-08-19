# QH-V2-AUTO-001 - Deterministic Harness Workflow Automation

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-005 - Repetitive Harness Workflow Automation Priority

## Problem

Qwen Harness development repeatedly requires manual STATUS inspection, Task loading, Git checks, scope checks, verification execution, and review preparation.

HC-001 through HC-007 already implement the authoritative deterministic safety and verification primitives, but they are currently invoked through repeated manual commands.

## Goal

Implement a small deterministic workflow utility that reduces repeated manual CMD work by orchestrating existing Harness Core functions.

The first version provides four read/check-oriented operations: `status`, `preflight`, `verify`, and `review`.

## Architecture Boundary

The automation utility is an orchestration layer, not a second Harness Core.

It must reuse existing HC-001 through HC-007 behavior where applicable and must not duplicate or weaken deterministic scope, Git, verification, Evidence, invariant, or final-gate logic.

## Required Operations

### status

Summarize at minimum:

- Current Task from `STATUS.md`;
- expected Task file path and whether it exists;
- Git working-tree state;
- actual changed paths;
- parsed Allowed Changes and Forbidden Changes when the Task file is available.

`status` must not modify Repository files.

### preflight

Check whether the Repository is in a valid state to begin or continue the Current Task.

At minimum it must check:

- Current Task can be resolved from `STATUS.md`;
- corresponding Task file exists;
- Task change-scope contract parses successfully;
- Repository root is a valid Git top-level;
- Repository state required by the operation is reported explicitly rather than silently repaired.

`preflight` is diagnostic only and must not clean or modify the Repository.

### verify

Reuse existing Harness verification functionality to execute the Current Task Verification contract and report objective results.

Where existing HC-006/HC-007 inputs are available, verification should reuse existing Evidence/final-gate types rather than inventing a separate PASS/FAIL authority.

The exact integration boundary must remain minimal; unsupported Evidence must be reported explicitly rather than fabricated.

### review

Summarize Human-review Evidence at minimum:

- Current Task;
- actual changed paths;
- Allowed/Forbidden scope result for each changed path;
- verification result summary;
- `git diff --check` result or equivalent deterministic whitespace check;
- whether unexpected changed paths exist.

`review` prepares Evidence for Human review. It does not approve semantic correctness and does not commit.

## CLI Boundary

A small Python entry point such as `tools/qh.py` may expose:

- `python tools/qh.py status`
- `python tools/qh.py preflight`
- `python tools/qh.py verify`
- `python tools/qh.py review`

Use only Python standard library unless an existing Repository dependency is already required by Harness Core.

Exact text formatting may be minimal and readable. Machine-readable persistence is deferred.

## Forbidden Automation

This Task must not implement:

- automatic Git commit;
- automatic Task completion;
- automatic STATUS mutation;
- Architecture or Decision mutation;
- Native Ollama API calls;
- Worker execution;
- Qwen tool execution;
- Repository edit tools;
- retry or fallback orchestration;
- LangGraph, ECC routing, multi-agent behavior, or Codex escalation.

## Allowed Changes

- `tools/qh.py`
- `tools/harness_core.py`
- `tests/test_qh.py`
- `tests/test_harness_core.py`
- `tasks/QH-V2-AUTO-001.md`
- `STATUS.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- `status`, `preflight`, `verify`, and `review` are implemented as the complete Automation V1 command set.
- Existing HC-001 through HC-007 logic is reused rather than duplicated where applicable.
- All four operations are deterministic with respect to Repository state and Task contract input.
- Read/check commands do not modify Repository state.
- Missing or malformed Current Task information fails clearly rather than guessing.
- Scope violations are reported and never silently accepted.
- Worker or Ollama execution is absent.
- No automatic commit, Task completion, STATUS mutation, retry, or Architecture mutation exists.
- Focused automation tests pass.
- Existing Harness Core regression tests continue to pass.
- No third-party dependency is added.
- No file outside Allowed Changes is modified.

## Verification

Run focused automation tests:

`python -m unittest tests.test_qh`

Run Harness Core regression:

`python -m unittest tests.test_harness_core`

Then verify:

- `git diff --check`
- `git status --short`

## Stop Condition

Stop after QH-V2-AUTO-001 implementation, Verification, independent review, commit, and clean working tree.

Do not start the Native Ollama Worker Adapter Task.
