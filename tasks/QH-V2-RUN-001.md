# QH-V2-RUN-001 - Single-Task Runner Integration

## Status

COMPLETE - VERIFIED

## Parent

ADR-008 - Backend-Neutral Tool Interaction Contract

## Goal

Integrate one approved Repository Task with the local Worker through a deterministic Single-Task Runner while preserving Harness-owned scope, tool execution, Verification, Evidence, and Final Gate authority.

This is a parent integration Task.

Implementation is intentionally decomposed into small Qwen-safe child Tasks.

## Architecture Basis

The Runner must preserve:

- ADR-004 - Post-HC-007 Worker Integration Architecture
- ADR-008 - Backend-Neutral Tool Interaction Contract
- QH-V2-WC-001 WorkerRequest / WorkerResponse compatibility
- Harness-owned Repository read and scoped edit tools
- HC-001 through HC-007 deterministic authority
- one Task at a time
- fail-closed behavior
- Human Gates

The Runner must not depend directly on Ollama-native `tool_calls` JSON.

## Child Task Sequence

### QH-V2-RUN-001A - Backend-Neutral Tool Interaction Records

Implement the ADR-008 logical contracts:

- ToolSpec
- ToolRequest
- ToolResult
- WorkerStep

Preserve the existing WorkerRequest and WorkerResponse dataclasses unchanged.

No Ollama continuation loop or Runner orchestration is implemented in 001A.

### QH-V2-RUN-001B - Native Ollama Tool Interaction Adapter

Extend the native Ollama Worker Adapter so backend-specific tool definitions, `tool_calls`, tool results, and conversation continuation are translated through the backend-neutral ADR-008 contract.

Ollama-specific structures remain inside the Adapter.

No Repository tool execution authority is granted to the Adapter.

No Single-Task Runner loop is implemented in 001B.

### QH-V2-RUN-001C - Deterministic Single-Task Runner Loop

Implement the Runner that:

- operates only on the explicitly selected current Task;
- supplies the approved Task context to the Worker;
- validates zero or one ToolRequest per Worker step;
- executes only Harness-owned `read_repo_text` and `write_repo_text`;
- injects current Task Allowed/Forbidden scope into `write_repo_text`;
- rejects malformed, unknown, unsupported, unauthorized, or multi-tool requests fail-closed;
- uses a finite deterministic Worker-step budget;
- stops safely when the step budget is exhausted;
- leaves Git, Verification, Evidence, Final Gate, commit, Task lifecycle, and Architecture authority outside Qwen.

The exact finite step budget must be fixed and tested in 001C.

## Dependency Order

Implementation order is mandatory:

1. QH-V2-RUN-001A
2. QH-V2-RUN-001B
3. QH-V2-RUN-001C
4. Parent integration review

A later child must not begin before the preceding child is COMPLETE - VERIFIED.

## Parent Completion Rule

QH-V2-RUN-001 is complete only when:

1. 001A is COMPLETE - VERIFIED.
2. 001B is COMPLETE - VERIFIED.
3. 001C is COMPLETE - VERIFIED.
4. Existing relevant regression tests remain passing.
5. Repository scope review reports no unexpected paths.
6. Single-Task Runner authority remains consistent with ADR-008.
7. Qwen self-reported completion is not used as authoritative PASS Evidence.

## Safety Boundaries

- Qwen cannot authorize filesystem operations.
- Qwen cannot choose or expand Allowed/Forbidden scope.
- Qwen receives no general shell authority.
- Qwen receives no Git authority.
- Qwen receives no Verification command authority.
- HC-004 remains owner of approved Verification command execution.
- Qwen cannot create Evidence or Final Gate authority.
- Qwen cannot commit.
- Qwen cannot complete or start Tasks.
- Qwen cannot modify Architecture.
- Retry/fallback policy remains outside this parent Task and follows Runner completion as a separate Milestone 1 stage.
- Automatic Codex escalation, LangGraph, ECC routing, and multi-agent expansion remain outside Milestone 1.

## Allowed Changes

The parent coordination Task itself may change only:

- STATUS.md
- tasks/QH-V2-RUN-001.md

Each child Task defines and owns its separate implementation change scope.

## Forbidden Changes

During parent coordination work:

- tools/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- all existing task files
- all other Repository files

Implementation changes occur only inside separately approved child Tasks.

## Acceptance Criteria

1. Runner integration is decomposed into 001A, 001B, and 001C.
2. Child responsibilities do not overlap unnecessarily.
3. Child order is explicit and mandatory.
4. ADR-008 backend-neutral boundary is preserved.
5. Existing WorkerRequest and WorkerResponse compatibility is preserved.
6. Tool authority remains deterministic and Harness-owned.
7. Retry remains outside Runner implementation.
8. Parent Task does not directly implement production code.
9. Every child requires its own Human approval and objective Verification.
10. Parent completion requires all children to be independently COMPLETE - VERIFIED.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

Confirm that parent contract preparation changes only:

`tasks/QH-V2-RUN-001.md`

## Stop Condition

Stop if child decomposition would require:

- changing ADR-008 without a new Architecture decision;
- broadening Qwen authority;
- coupling Runner orchestration to Ollama-native JSON;
- combining Retry/Safe Stop policy into Runner implementation;
- bypassing an independent child Task Human Gate.

Do not begin QH-V2-RUN-001A implementation in this parent planning step.

## Parent Integration Review Evidence

Parent integration review was performed after all mandatory child Tasks were independently completed and verified.

### Child Completion

- QH-V2-RUN-001A: COMPLETE - VERIFIED
- QH-V2-RUN-001B: COMPLETE - VERIFIED
- QH-V2-RUN-001C: COMPLETE - VERIFIED

Implementation Evidence:

- 001A backend-neutral tool interaction records: commit 80cdfff
- 001B native Ollama tool interaction adapter: completion commit 5472162
- 001C deterministic Single-Task Runner: completion commit 4cb1ff5

### Integration Boundary Review

The deterministic Runner imports and connects:

- backend-neutral Harness Core contracts and scope authority;
- OllamaToolSession;
- Harness-owned read_repo_text and write_repo_text.

Runner inspection found no direct authority for:

- Git;
- subprocess/shell execution;
- Verification;
- Evidence or Final Gate;
- commit;
- Ollama-native tool_calls JSON.

Adapter inspection found no direct Repository tool execution, Git, Verification, or Final Gate authority.

Therefore the architecture boundary remains:

Qwen / Ollama Adapter
-> backend-neutral ToolRequest / ToolResult / WorkerStep
-> deterministic Single-Task Runner
-> Harness-owned Repository tools

### Runner Safety Evidence

QH-V2-RUN-001C verified:

- explicit ACTIVE Current Task validation;
- complete Task contract delivery to Worker;
- read_repo_text / write_repo_text-only Worker tool surface;
- zero-or-one ToolRequest execution policy;
- fail-closed multi-tool, malformed, unknown, unauthorized, absolute-path, and path-escape handling;
- Runner-owned Allowed/Forbidden write scope injection;
- lifecycle-control write protection for STATUS.md and the active Task contract;
- Windows case-alias lifecycle protection;
- finite eight-WorkerStep budget;
- no ninth Worker interaction;
- terminal Worker text is not treated as Repository PASS.

Focused Runner tests: 23 PASS before authoritative close.

### Authoritative Child Verification

QH-V2-RUN-001C authoritative qh close reported:

- tests.test_task_runner: PASS
- tests.test_ollama_worker: PASS
- tests.test_repo_tools: PASS
- tests.test_harness_core: PASS
- git diff --check: PASS
- unexpected changed paths: none
- Final Gate: PASS

No production code changes occurred after that verified Runner completion before this Parent integration review.

### Parent Review Result

PASS - READY FOR AUTHORITATIVE CLOSE

The integrated 001A + 001B + 001C implementation remains consistent with ADR-008.

Qwen self-reported completion is not used as authoritative PASS Evidence.

Retry/Safe Stop remains outside this Parent and is the next Milestone 1 stage after Parent completion.
