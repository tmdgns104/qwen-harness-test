# QH-V2-ARCH-003 - Repetitive Workflow Automation Priority

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-003 - Verified Problem Resolution and Automation Escalation
ADR-004 - Post-HC-007 Worker Integration Architecture

## Problem

ADR-004 places the Minimal CLI after Worker Adapter, Repository tools, Runner, and Retry work.

Repository Evidence now shows that repeated manual status, Git, scope, verification, and review commands are already frequent and error-prone enough to justify automation before Native Ollama Worker Adapter implementation.

The Human has explicitly requested prioritizing this repetitive workflow automation.

## Goal

Authorize a small deterministic Harness workflow automation phase immediately after the completed Worker Contract and before the Native Ollama Worker Adapter.

This is an Architecture/documentation Task only.

Do not implement `tools/qh.py` or any automation code in this Task.

## Proposed Decision

Append ADR-005 - Repetitive Harness Workflow Automation Priority.

ADR-005 must record that:

- HC-001 through HC-007 remain authoritative and are reused rather than reimplemented.
- QH-V2-WC-001 remains completed and its Worker contract is unchanged.
- A deterministic workflow utility may be implemented before the Native Ollama Worker Adapter.
- Automation V1 is limited to read/check-oriented `status`, `preflight`, `verify`, and `review` operations.
- The utility may orchestrate existing Harness Core functions but must not create a second safety or verification engine.
- Human approval remains required for Architecture decisions, Task approval, semantic review, completion approval, and commit decisions.
- Automation V1 must not auto-commit, auto-complete Tasks, modify Architecture, invoke a Worker backend, execute Qwen tools, or introduce retry orchestration.
- Native Ollama Worker Adapter remains NOT STARTED until the automation phase is completed or explicitly superseded by a later approved decision.

## Revised Milestone 1 Sequence

1. Worker contract / backend-independent boundary - completed by QH-V2-WC-001.
2. Deterministic Harness repetitive workflow automation - `status`, `preflight`, `verify`, `review`.
3. Native Ollama Worker Adapter.
4. Harness-owned Repository read tools.
5. Harness-owned scoped edit tools.
6. Single-Task Runner connecting Worker execution to HC-001 through HC-007.
7. Bounded retry / safe FAIL or BLOCKED handling.
8. Minimal Worker-facing CLI integration.
9. End-to-End regression with real small Repository Tasks.

The automation phase is an operational efficiency insertion and does not change the deterministic safety ownership defined by ADR-001 through ADR-004.

## Automation V1 Boundary

The later implementation Task should expose a small utility such as `tools/qh.py` with these initial operations:

- `status`: summarize Current Task, Task file, Git state, changed paths, and Task scope.
- `preflight`: check that the current Task and Repository state are ready for work.
- `verify`: reuse existing Harness verification/Evidence/final-gate functions where applicable.
- `review`: summarize actual changes against Allowed/Forbidden scope and verification state for Human review.

Exact CLI arguments, output dataclasses, persistence behavior, and implementation details belong to the later implementation Task.

## Required Changes

### DECISIONS.md

Append ADR-005 only. Do not rewrite ADR-001 through ADR-004.

### STATUS.md

Record QH-V2-ARCH-003 as the active Architecture Task while this decision is being completed.

## Allowed Changes

- `tasks/QH-V2-ARCH-003.md`
- `DECISIONS.md`
- `STATUS.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `src/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- existing Task files
- fixtures
- implementation code

## Acceptance Criteria

- ADR-005 explicitly authorizes deterministic workflow automation before Native Ollama Worker Adapter work.
- Existing ADR-001 through ADR-004 remain unchanged.
- HC-001 through HC-007 remain the authoritative deterministic engine.
- Automation V1 is limited to `status`, `preflight`, `verify`, and `review`.
- Human Gates remain authoritative.
- Automatic commit, automatic Task completion, Worker execution, tool execution, and retry orchestration are not authorized.
- Revised Milestone 1 ordering is recorded.
- No implementation code is modified.

## Verification

- `git diff -- tasks/QH-V2-ARCH-003.md DECISIONS.md STATUS.md`
- `git diff --check`
- `git status --short`

Confirm that no file outside Allowed Changes was modified.

## Stop Condition

Stop after ADR-005 and STATUS are updated, independently reviewed, committed, and the working tree is clean.

Do not implement `tools/qh.py` in this Architecture Task.
Do not start the Native Ollama Worker Adapter.
