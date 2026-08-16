# Qwen Harness V2

## Project Purpose

Build a local-first development harness that allows Repository work to continue when Codex is unavailable or its token/usage limit is exhausted.

## Primary Execution Model

- OpenCode + local Qwen is the low-cost local implementation Worker.
- Codex is an optional high-capability executor.
- Codex is not required for the Harness Core to operate.
- Difficult work may be decomposed into smaller Qwen-safe Tasks.

## Reliability Principle

- Qwen self-reported PASS is not authoritative.
- Completion is determined from Git/Test or other objective Evidence.
- Repository documents and Git, not chat history, are the project state reference.

## Milestone 1

Codex 없이도 OpenCode + Qwen + Git-based Harness를 사용하여 작은 Repository Task를 안전하고 반복 가능하게 수행할 수 있다.

## Future Direction

Future phases may selectively adopt:

- ECC-inspired routing, skill selection, and context-management practices
- optional Codex escalation
- LangGraph orchestration

These are not part of Milestone 1 implementation.