# QH-V2-OWA-001 - Native Ollama Worker Adapter

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-002 - Agent-Independent Native Local Worker Architecture
ADR-004 - Post-HC-007 Worker Integration Architecture
ADR-005 - Repetitive Harness Workflow Automation Priority
QH-V2-WC-001 - Worker Contract / Backend-Independent Boundary

## Problem

The backend-independent WorkerRequest and WorkerResponse contract exists, but there is no production adapter that sends a WorkerRequest to the approved native Ollama Qwen3:8B backend.

## Goal

Implement the smallest Native Ollama Worker Adapter that converts WorkerRequest into one native Ollama chat request and converts the transport result into WorkerResponse.

This Task is transport-only. It does not grant Qwen Repository, filesystem, shell, Git, verification, or tool execution authority.

## Public Contract

Implement a small callable in `tools/ollama_worker.py` with equivalent behavior to:

`call_ollama_worker(request: WorkerRequest, *, base_url: str, model: str, timeout_seconds: float) -> WorkerResponse`

Defaults:

- base URL: `http://127.0.0.1:11434`
- model: `qwen3:8b`
- initial reasoning path: `think:false`

The existing WorkerRequest and WorkerResponse dataclasses remain unchanged.

## Request Contract

The adapter sends one POST request to the native Ollama `/api/chat` endpoint.

Request JSON must contain:

- `model`: selected model
- `messages`: one user message containing `WorkerRequest.task_text`
- `stream`: false
- `think`: false

The Adapter must not include tool definitions or grant filesystem or shell capabilities.

## Response Contract

For HTTP success with valid Ollama JSON containing string `message.content`:

- `transport_ok=True`
- `output_text=message.content`
- `error=None`

Transport success does not mean Repository Task PASS. Model output is never treated as Harness final-gate authority.

For connection failure, timeout, HTTP failure, invalid JSON, or malformed response schema:

- `transport_ok=False`
- `output_text=""`
- `error` contains a readable failure description

Fail closed. Do not silently repair malformed responses.

## Retry Boundary

No retry is implemented in this Adapter. ADR-004 requires retry above the Worker Adapter in a later Task.

## Tool Boundary

This Task must not implement:

- Ollama tool definitions or tool-call execution
- Repository read tools
- Repository edit tools
- shell execution
- Git operations
- Verification execution
- Evidence or Final Gate ownership
- Runner orchestration
- retry or fallback
- OpenCode integration
- LangGraph, ECC routing, multi-agent behavior, or Codex escalation

## Implementation Constraint

Use Python standard library HTTP and JSON facilities. Do not add a third-party dependency.

## Allowed Changes

- `tools/ollama_worker.py`
- `tests/test_ollama_worker.py`
- `tasks/QH-V2-OWA-001.md`
- `STATUS.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/qh.py`
- `tests/test_harness_core.py`
- `tests/test_qh.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- Existing WorkerRequest and WorkerResponse contracts are reused unchanged.
- Default backend is native Ollama `qwen3:8b`.
- Request uses `/api/chat`, `stream:false`, and `think:false`.
- WorkerRequest.task_text is sent as the user message.
- Valid response content becomes WorkerResponse with transport_ok true.
- Network, HTTP, JSON, and schema failures become transport_ok false with readable error Evidence.
- No retry exists.
- No tool, filesystem, shell, Git, Repository edit, or verification authority is added.
- Model text cannot become Harness PASS merely through this Adapter.
- Focused unit tests validate request payload and success/failure parsing.
- One real local Ollama smoke check confirms qwen3:8b transport returns transport_ok true and non-empty output without asserting semantic correctness.
- Existing Harness Core regression remains passing.
- No third-party dependency is added.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_ollama_worker`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after implementation, real local Ollama transport Evidence, Verification, independent review, commit, and clean working tree.

Do not start Repository read tools, edit tools, Runner, retry, or later Milestone 1 Tasks.
