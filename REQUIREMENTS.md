# Qwen Harness V2 Requirements

## Functional Requirements

### FR-001 - Codex-independent continuation

The Harness must allow Repository work to continue when Codex is unavailable or its token/usage limit is exhausted.

### FR-002 - Local Worker execution path

The Harness must provide a local implementation Worker path that does not require Codex or a paid model.

The current default local Worker candidate is native Ollama API + Qwen3:8B.

OpenCode may remain an optional alternative Worker/backend.

### FR-003 - Small Task execution

Qwen implementation work must be assignable as small Tasks with one clear Goal and a limited change scope.

### FR-004 - One Task at a time

A Worker must execute only the explicitly assigned current Task and must not automatically select or start another Task.

### FR-005 - Change scope contract

A Task must be able to declare Allowed Changes and Forbidden Changes so actual Repository changes can be checked against the Task contract.

### FR-006 - Independent completion evidence

Qwen self-reported PASS, verification claims, or file-change claims must not be treated as authoritative completion evidence.

Completion must be determined from Git, tests, command exit codes, exact file content, or other objective Evidence.

### FR-007 - Git baseline

Before Worker execution, the Harness workflow must be able to identify a clean Git baseline so Task changes can be distinguished from pre-existing changes.

### FR-008 - Failure stop behavior

If a Task fails, violates scope, conflicts with Architecture, or requires an unapproved decision, the workflow must stop rather than silently changing Architecture or requirements.

### FR-009 - Optional Codex

Codex must remain an optional high-capability executor rather than a mandatory dependency of the Harness Core.

### FR-010 - Qwen-safe decomposition

When a Task is too difficult or too large for Qwen, the workflow must allow the Task to be decomposed into smaller Qwen-safe Tasks before considering escalation.

### FR-011 - Worker/backend independence

Task contracts, scope checks, Git Evidence, verification, and completion gates must not depend on OpenCode-specific behavior or any single Worker frontend/backend.

### FR-012 - Harness-owned tool boundary

Tool permission and execution boundaries must be enforced by deterministic Harness code.

An LLM request alone must not authorize Repository operations.

### FR-013 - Bounded retry and safe stop

Worker retries must be bounded.

Repeated failure must terminate as FAIL or BLOCKED rather than loop indefinitely or increase prompt complexity without limit.

## Verification Requirements

- Actual changed paths must be checkable independently from Worker self-report.
- Forbidden-path modification must be detectable.
- Required exact file content must be independently comparable when the Task defines exact output.
- Test and command results used as Evidence must include their actual exit result.
- Completion must not be accepted only because an LLM says PASS.
- A failed Task must not automatically advance to the next Task.

## Non-Functional Requirements

- Repository documents and Git are the project Source of Truth, not chat history or LLM session memory.
- The Harness Core should remain understandable and minimal before adding orchestration complexity.
- Local execution should remain usable without a paid model.
- Qwen Worker responsibilities should stay narrow.
- Architecture changes require explicit Human approval. ChatGPT provides technical analysis and recommendations. A Worker must not infer or approve Architecture changes.

## Milestone 1 Boundary

Milestone 1 requires:

- A local Worker can execute small Repository Tasks without requiring Codex or a paid model.
- Git/Test or other objective Evidence can independently verify the result.
- Failure can stop safely without automatically advancing.

Milestone 1 does not require:

- full ECC adoption
- automatic Agent/Skill routing
- automatic Codex escalation
- LangGraph orchestration