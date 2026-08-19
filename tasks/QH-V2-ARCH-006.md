# QH-V2-ARCH-006 - Backend-Neutral Tool Interaction Contract

## Status

COMPLETE - VERIFIED

## Parent

ADR-004 - Post-HC-007 Worker Integration Architecture

## Problem

Milestone 1 requires a Single-Task Runner connecting Worker execution to the deterministic Harness Core.

The current backend-independent Worker contract contains only:

- WorkerRequest.task_text
- WorkerResponse.transport_ok
- WorkerResponse.output_text
- WorkerResponse.error

The current native Ollama Adapter returns only message.content.

Repository Evidence shows that Qwen3:8B can produce structured native Ollama tool calls and that a Python-controlled tool-call/result continuation loop succeeded, but no backend-neutral Repository contract currently defines how tool requests and tool results cross the Worker boundary.

Directly coupling the Runner to Ollama-native tool_calls would violate Worker/backend independence.

Changing the existing WorkerRequest or WorkerResponse contract without an explicit Architecture decision would violate QH-V2-WC-001.

## Goal

Define the smallest backend-neutral tool-interaction contract needed for Single-Task Runner integration while preserving deterministic Harness ownership of tool permission and execution.

This Task is design-only.

## Required Decisions

The Task must decide:

1. How a Worker requests a Harness-owned tool without exposing Ollama-specific JSON to the Runner.
2. How deterministic Harness code represents a tool result returned to the Worker.
3. Where the multi-turn tool-call/result continuation loop is owned.
4. Whether the existing WorkerRequest and WorkerResponse dataclasses remain unchanged or require an explicitly versioned extension.
5. How malformed, unknown, unauthorized, or invalid tool requests fail closed.
6. Which Milestone 1 tools are initially exposed.
7. How the contract preserves one-Task-at-a-time execution and existing Human Gates.

## Safety Boundaries

- HC-001 through HC-007 remain authoritative.
- Tool permission and execution authority remain deterministic Harness responsibilities.
- Qwen cannot authorize filesystem, shell, Git, verification, Evidence, or final-gate operations.
- No general shell authority is introduced.
- Approved verification commands remain owned by HC-004.
- Qwen self-reported PASS remains non-authoritative.
- Malformed or invalid tool requests must not be silently repaired and executed.
- Backend-specific Ollama JSON must not become the Runner's public contract.
- Retry remains outside this Task.
- Automatic commit, Task completion, next-Task start, or Architecture mutation remain forbidden.

## Scope

Design and document only the backend-neutral interaction boundary required before Single-Task Runner implementation.

Do not implement the Runner or Worker tool loop in this Task.

## Allowed Changes

- DECISIONS.md
- STATUS.md
- tasks/QH-V2-ARCH-006.md

## Forbidden Changes

- tools/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- all existing task files
- all other Repository files

## Acceptance Criteria

1. Repository Evidence and current contracts are explicitly referenced.
2. A backend-neutral tool request/result representation is defined.
3. Ownership of the continuation loop is explicitly assigned.
4. Compatibility with QH-V2-WC-001 is explicitly resolved.
5. Failure behavior for malformed, unknown, and unauthorized tool requests is fail-closed.
6. Initial Milestone 1 tool exposure is explicitly bounded.
7. Ollama-specific fields do not become Runner architecture.
8. Retry remains a later separate Task.
9. No production or test code is modified.
10. The resulting decision is recorded in DECISIONS.md before Runner implementation.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

Confirm that only:

- DECISIONS.md
- STATUS.md
- tasks/QH-V2-ARCH-006.md

may change.

## Stop Condition

Stop if the design would require weakening Worker/backend independence, deterministic Harness tool authority, HC-004 verification ownership, or existing Human Gates.

Do not begin Single-Task Runner implementation in this Task.

## Decision Result

Human approved ADR-008 - Backend-Neutral Tool Interaction Contract.

The accepted design resolves the Runner boundary as follows:

- QH-V2-WC-001 WorkerRequest and WorkerResponse remain unchanged.
- Tool-enabled execution uses separate backend-neutral ToolSpec, ToolRequest, ToolResult, and WorkerStep semantics.
- The Runner owns the tool-call/result continuation loop.
- The Adapter owns backend translation and backend conversation state only.
- Ollama-native tool_calls do not become a Runner contract.
- Initial Worker tools are limited to read_repo_text and write_repo_text.
- write_repo_text scope is injected by the Runner from the current Task; Qwen cannot supply or expand its own change scope.
- Initial Worker steps allow zero or one ToolRequest; multiple requests in one step fail closed.
- Malformed, unknown, unsupported, or unauthorized requests fail closed before execution.
- Authorized tool execution errors may be returned as ToolResult(ok=False).
- The tool loop must have a finite deterministic step budget; the exact limit is deferred to the Runner implementation Task.
- Retry/fallback remains a separate later Task.
- Git, shell, Verification, Evidence, Final Gate, commit, Task lifecycle, and Architecture operations are not exposed as Worker tools.

## Architecture Gate Result

PASS - the backend-neutral interaction boundary required before Single-Task Runner implementation is now explicitly defined by ADR-008.

This Task does not authorize Runner implementation by itself; Runner implementation still requires its own approved Task and Human Gate.
