# QH-V2-ARCH-002 - Post-HC-007 Worker Integration Architecture

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-001 - Deterministic Harness Core Before Further Orchestration
ADR-002 - Agent-Independent Native Local Worker Architecture
ADR-003 - Verified Problem Resolution and Automation Escalation

## Problem

HC-001 through HC-007 are complete and verified, but ADR-003 still defers Worker Adapter implementation until Architecture explicitly permits it.

Milestone 1 requires a local Worker to execute small Repository Tasks while deterministic Git/Test Evidence independently verifies completion and unsafe failure stops safely.

The Repository therefore needs one explicit post-HC-007 integration decision before Worker implementation begins.

## Goal

Add an ADR-004 decision that authorizes the post-HC-007 Worker integration phase and fixes the minimal Milestone 1 integration boundaries and implementation sequence.

This is an architecture/documentation Task only.

Do not modify implementation code.

## Proposed Decision Boundary

ADR-004 must record that:

- HC-001 through HC-007 remain the authoritative deterministic Harness Core.
- Worker integration is now permitted behind an agent/backend-independent boundary.
- The default local Worker path remains native Ollama API + Qwen3:8B.
- The initial fast path remains `think:false`.
- Tool permission and execution authority belong to deterministic Harness code.
- Qwen must not directly authorize filesystem or shell operations.
- Milestone 1 does not grant Qwen general shell execution; approved verification commands remain owned by HC-004.
- Worker transport, tool execution, orchestration, retry policy, CLI, and E2E verification remain separate responsibilities.
- Retry is bounded and belongs above the Worker Adapter rather than inside the transport adapter.
- ECC routing, LangGraph orchestration, multi-agent expansion, and automatic Codex escalation remain outside Milestone 1.

## Planned Milestone 1 Integration Sequence

The ADR should authorize incremental Tasks in this order:

1. Worker contract / backend-independent boundary.
2. Native Ollama Worker Adapter.
3. Harness-owned Repository read tools.
4. Harness-owned scoped edit tools.
5. Single-Task Runner connecting Worker execution to HC-001 through HC-007.
6. Bounded retry / safe FAIL or BLOCKED handling.
7. Minimal user CLI.
8. End-to-End regression with real small Repository Tasks.

Exact implementation details and retry counts are deferred to their own Tasks and objective Evidence.

## Required Changes

### DECISIONS.md

Append ADR-004 - Post-HC-007 Worker Integration Architecture.

ADR-004 must explicitly release the ADR-003 Worker Adapter deferral only for the approved staged Milestone 1 sequence.

Do not rewrite ADR-001, ADR-002, or ADR-003.

### STATUS.md

Record QH-V2-ARCH-002 as the current Architecture Task while it is active.

## Allowed Changes

- `tasks/QH-V2-ARCH-002.md`
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

If PROJECT.md or REQUIREMENTS.md is found to conflict with this Task, STOP and report the conflict rather than modifying them.

## Acceptance Criteria

- ADR-004 is added without changing ADR-001 through ADR-003.
- ADR-004 explicitly permits staged Worker integration after verified HC-007 completion.
- Backend independence and native Ollama + Qwen3:8B default direction are preserved.
- Harness-owned tool authority is preserved.
- General Qwen shell authority is not introduced for Milestone 1.
- HC-004 remains the owner of approved verification command execution.
- Retry remains bounded and outside the transport adapter.
- The incremental Milestone 1 sequence is recorded.
- ECC, LangGraph, multi-agent expansion, and automatic Codex escalation remain outside Milestone 1.
- No implementation code is modified.

## Verification

Verify with:

- `git diff -- tasks/QH-V2-ARCH-002.md DECISIONS.md STATUS.md`
- `git diff --check`
- `git status --short`

Confirm that no file outside Allowed Changes was modified.

## Stop Condition

Stop after ADR-004 and STATUS are updated, independently reviewed, committed, and the working tree is clean.

Do not implement WA-001 or any Worker Adapter code in this Task.
