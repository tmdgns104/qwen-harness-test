# QH-V2-SPEC-001A - Create Project Definition

## Status

APPROVED - READY FOR IMPLEMENTATION

## Goal

Create `PROJECT.md` for Qwen Harness V2.

This Task records the already-approved project purpose and scope.
Do not invent or change Architecture.

## Required Content

`PROJECT.md` must state the following.

### Project Purpose

Build a local-first development harness that allows Repository work to continue
when Codex is unavailable or its token/usage limit is exhausted.

### Primary Execution Model

- OpenCode + local Qwen is the low-cost local implementation Worker.
- Codex is an optional high-capability executor.
- Codex is not required for the Harness Core to operate.
- Difficult work may be decomposed into smaller Qwen-safe Tasks.

### Reliability Principle

- Qwen self-reported PASS is not authoritative.
- Completion is determined from Git/Test or other objective Evidence.
- Repository documents and Git are used instead of chat history as project state.

### Milestone 1

Codex 없이도 OpenCode + Qwen + Git-based Harness를 사용하여
작은 Repository Task를 안전하고 반복 가능하게 수행할 수 있다.

### Future Direction

Future phases may selectively adopt:

- ECC-inspired routing / skill / context-management practices
- optional Codex escalation
- LangGraph orchestration

These are not part of Milestone 1 implementation.

## Scope

Create only:

- `PROJECT.md`

## Allowed Changes

- `PROJECT.md`

## Forbidden Changes

- all other Repository files

## Acceptance Criteria

- `PROJECT.md` exists.
- It explains why Qwen Harness V2 exists.
- It explicitly covers Codex token/usage exhaustion.
- OpenCode + Qwen is identified as the local Worker path.
- Codex is identified as optional, not mandatory.
- Qwen self-reported PASS is identified as non-authoritative.
- Git/Test Evidence is identified as the completion basis.
- Milestone 1 is clearly stated.
- ECC and LangGraph are described only as future directions.
- No implementation code is created.
- No other Repository file is modified.

## Stop Condition

Stop immediately after creating `PROJECT.md`.

Do not create REQUIREMENTS.md.
Do not create ARCHITECTURE.md.
Do not create DECISIONS.md.
Do not create AGENTS.md.
Do not modify STATUS.md.
Do not start another Task.
