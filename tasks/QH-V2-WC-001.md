# QH-V2-WC-001 - Worker Contract / Backend-Independent Boundary

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-004 - Post-HC-007 Worker Integration Architecture

## Problem

Milestone 1 requires a backend-independent Worker boundary before any native Ollama transport or Repository tool implementation begins.

The deterministic Harness Core must be able to describe a Worker request and receive a Worker response without depending on Ollama, OpenCode, Codex, or any other specific backend.

## Goal

Define and implement the minimal backend-independent Worker data contract used by later Worker Adapter Tasks.

This Task is limited to the Worker contract itself.

Do not implement Ollama transport, tool execution, retry orchestration, CLI behavior, or Repository mutation.

## Required Contract

Add minimal immutable Worker contract types to `tools/harness_core.py`.

The contract must represent at minimum:

- a Worker request containing the approved Task text or task instruction supplied by deterministic Harness code;
- a Worker response containing Worker-produced textual output;
- explicit success/failure transport status that does not represent Harness final PASS/FAIL;
- an optional backend-neutral error description for failed Worker execution.

The exact contract for this Task is:

```python
@dataclass(frozen=True)
class WorkerRequest:
    task_text: str

@dataclass(frozen=True)
class WorkerResponse:
    transport_ok: bool
    output_text: str
    error: str | None = None
```

`transport_ok=True` means only that the Worker backend returned successfully with a structurally usable response. It must not be interpreted as Repository Task PASS.

These class names, field names, field order, and Python types are fixed by this Task and must be covered by tests.

The contract must not contain Ollama-specific request objects, HTTP fields, model names, tool execution authority, Git authority, verification authority, or final gate authority.

## Boundary Rules

- Worker response success means only that the Worker backend returned a structurally valid response.
- Worker success must never mean Repository Task PASS.
- Qwen self-reported PASS remains non-authoritative.
- Deterministic HC-001 through HC-007 remain responsible for scope, Git Evidence, verification, invariants, Evidence assembly, and final gating.
- No filesystem or shell execution authority is granted by this contract.
- No retry policy belongs inside this contract.

## Scope

Implement only the backend-independent Worker contract and focused tests for that contract.

Do not implement:

- native Ollama API calls;
- `think:false` transport behavior;
- Repository read tools;
- Repository edit tools;
- shell execution;
- verification command execution changes;
- Single-Task Runner;
- retry or fallback policy;
- CLI;
- LangGraph, ECC routing, multi-agent behavior, or Codex escalation.

## Allowed Changes

- `tools/harness_core.py`
- `tests/test_harness_core.py`
- `tasks/QH-V2-WC-001.md`
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

- Backend-independent Worker contract types exist in `tools/harness_core.py`.
- Contract types contain no Ollama/OpenCode/Codex-specific fields.
- Worker transport success is structurally distinct from deterministic Harness PASS/FAIL.
- Contract grants no filesystem, shell, Git, verification, or final-gate authority to the Worker.
- Contract contains no retry implementation.
- Focused tests prove construction, immutability, success/failure representation, and backend independence.
- Existing Harness Core tests continue to pass.
- No third-party dependency is added.
- No file outside Allowed Changes is modified.

## Verification

Run:

`python -m unittest tests.test_harness_core`

Then verify:

- `git diff --check`
- `git status --short`

## Stop Condition

Stop after QH-V2-WC-001 implementation, Verification, independent review, commit, and clean working tree.

Do not start the Native Ollama Worker Adapter Task.
Do not implement WA-001 or Ollama transport in this Task.
