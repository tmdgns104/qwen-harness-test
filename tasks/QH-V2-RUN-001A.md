# QH-V2-RUN-001A - Backend-Neutral Tool Interaction Records

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

QH-V2-RUN-001 - Single-Task Runner Integration

## Architecture Basis

ADR-008 - Backend-Neutral Tool Interaction Contract

## Problem

ADR-008 defines four logical backend-neutral records required before native Ollama tool interaction and Single-Task Runner orchestration can be implemented:

- ToolSpec
- ToolRequest
- ToolResult
- WorkerStep

The existing WorkerRequest and WorkerResponse contracts are already frozen and independently regression-tested.

No production representation for the new ADR-008 records exists yet.

## Goal

Implement only the smallest immutable backend-neutral data contracts required by ADR-008.

Do not implement Ollama tool-call translation, continuation, Repository tool execution, Runner orchestration, retry, or CLI behavior.

## Required Public Contracts

Add immutable dataclasses with these semantics:

### ToolSpec

Fields in this exact order:

1. name: str
2. description: str
3. input_schema: Mapping[str, object]

### ToolRequest

Fields in this exact order:

1. call_id: str
2. name: str
3. arguments: Mapping[str, object]

### ToolResult

Fields in this exact order:

1. call_id: str
2. ok: bool
3. output: str
4. error: str | None

### WorkerStep

Fields in this exact order:

1. transport_ok: bool
2. output_text: str
3. tool_requests: tuple[ToolRequest, ...]
4. error: str | None

All four records must use frozen dataclasses.

These records define transport/orchestration data only. They do not grant tool execution authority or represent Harness PASS/FAIL.

## Existing Contract Preservation

WorkerRequest must remain exactly:

- task_text: str

WorkerResponse must remain exactly:

- transport_ok: bool
- output_text: str
- error: str | None

Do not add, remove, rename, reorder, or change fields in WorkerRequest or WorkerResponse.

## Boundary Rules

The new records must contain no:

- Ollama-specific JSON field names;
- HTTP behavior;
- model selection;
- Repository root authority;
- Allowed/Forbidden scope authority;
- shell authority;
- Git authority;
- Verification authority;
- Evidence or Final Gate authority;
- commit or Task lifecycle authority;
- retry policy.

ToolRequest is only a request representation.

ToolResult is only deterministic tool-execution result data.

WorkerStep is only one backend-neutral Worker interaction step.

## Allowed Changes

- tools/harness_core.py
- tests/test_harness_core.py
- STATUS.md
- tasks/QH-V2-RUN-001A.md

## Forbidden Changes

- tools/ollama_worker.py
- tests/test_ollama_worker.py
- tools/repo_tools.py
- tests/test_repo_tools.py
- tools/qh.py
- tests/test_qh.py
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- tasks/QH-V2-RUN-001.md
- all other existing task files
- all other Repository files

## Acceptance Criteria

1. ToolSpec exists as a frozen dataclass with the exact required field order and annotations.
2. ToolRequest exists as a frozen dataclass with the exact required field order and annotations.
3. ToolResult exists as a frozen dataclass with the exact required field order and annotations.
4. WorkerStep exists as a frozen dataclass with the exact required field order and annotations.
5. Existing WorkerRequest exact contract remains unchanged.
6. Existing WorkerResponse exact contract remains unchanged.
7. New records contain no Ollama-specific or authority-bearing fields.
8. Focused tests prove immutability and exact contract shape.
9. Existing Harness Core regression remains passing.
10. No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop if implementation requires:

- changing WorkerRequest or WorkerResponse;
- introducing Ollama-specific data into the backend-neutral contract;
- granting tool execution or scope authority through these records;
- implementing continuation, Runner, retry, CLI, Git, or Verification behavior;
- changing ADR-008.

Do not begin QH-V2-RUN-001B or QH-V2-RUN-001C in this Task.
