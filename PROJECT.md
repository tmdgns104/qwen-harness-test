# Qwen Harness V2

## Project Purpose

Build a local-first development harness that allows Repository work to continue when Codex is unavailable or its token/usage limit is exhausted.

## Primary Execution Model

- The Harness Core is independent from any specific agent frontend or Worker backend.
- The current default local Worker candidate is native Ollama API + Qwen3:8B.
- OpenCode remains an optional alternative Worker/backend and future benchmark candidate.
- Codex is an optional high-capability executor.
- Codex is not required for the Harness Core to operate.
- Difficult work may be decomposed into smaller Qwen-safe Tasks.

## Reliability Principle

- Qwen self-reported PASS is not authoritative.
- Completion is determined from Git/Test or other objective Evidence.
- Repository documents and Git, not chat history, are the project state reference.
- Deterministic Harness failure Evidence cannot be overridden by LLM output.

## Milestone 1

Without Codex or a paid model, the Harness can use a local Worker to execute small Repository Tasks safely and repeatably while deterministic Git/Test Evidence independently verifies completion and stops unsafe failure.

## Future Direction

Future phases may selectively adopt:

- additional local Worker backends and model benchmarking
- ECC-inspired routing, skill selection, and context-management practices
- optional Codex escalation
- LangGraph orchestration

These are not part of Milestone 1 implementation.
