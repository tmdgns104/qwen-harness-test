# QH-V2-ARCH-007 - Bounded Retry and Safe Stop Policy

## Status

COMPLETE - VERIFIED

## Parent Context

Milestone 1 - Bounded Retry / Safe Stop stage after QH-V2-RUN-001 completion.

## Architecture Basis

- ADR-004 - Post-HC-007 Worker Integration Architecture
- ADR-008 - Backend-Neutral Tool Interaction Contract
- QH-V2-RUN-001 - COMPLETE - VERIFIED

## Problem

The deterministic Single-Task Runner is complete and verified.

The next Milestone 1 stage requires bounded retry / safe FAIL or BLOCKED handling.

However, the current RunnerResult exposes a readable error string but does not yet provide a structured retry classification.

A retry layer must not determine safety by parsing error-message text.

Retry also must not restart a Task after a Repository write when the previous execution may already have produced side effects.

## Goal

Record ADR-009 defining the minimum safe retry policy before Retry implementation begins.

This Task makes an Architecture decision only.

It does not implement Retry production code.

## Proposed Decision

### Attempt Limit

The initial Retry V1 maximum is:

2 total Runner attempts

meaning:

- 1 initial Runner execution;
- at most 1 automatic retry.

There is no third automatic attempt.

The value may be revisited only with later objective Evidence.

### Retry Layer

Retry is implemented above the Single-Task Runner.

Retry must not be implemented inside:

- Ollama transport;
- OllamaToolSession;
- Repository read/write tools;
- Harness Core Verification;
- the Worker-step loop itself.

The existing eight-WorkerStep limit remains independent.

A new Runner attempt receives a new eight-step execution budget.

### Structured Failure Classification

Retry policy must use deterministic structured failure metadata.

It must not depend on matching or parsing human-readable error text.

The later implementation may extend RunnerResult or introduce an equivalent backend-neutral result type.

Exact field names are implementation details, but the result must distinguish at least:

- normal terminal completion;
- transient Worker/session failure;
- deterministic validation/safety failure;
- Worker-step budget exhaustion;
- Repository side-effect risk.

### Retryable Failure

Automatic retry is allowed only when all of the following are true:

1. the Runner did not terminate normally;
2. the failure is classified as transient Worker/session failure;
3. no Repository write operation was attempted during that Runner attempt;
4. the total attempt limit has not been reached.

Initial transient candidates are limited to failures such as:

- Worker session creation/call failure;
- Worker transport failure;
- Worker continuation transport/session failure.

This classification is deterministic Harness policy, not a Qwen decision.

### Non-Retryable Safe Stop

The following failures are not automatically retried:

- invalid or mismatched Task selection;
- non-ACTIVE Current Task;
- malformed ToolRequest;
- empty/invalid call_id;
- unsupported or unknown tool;
- extra/missing/wrongly typed arguments;
- multiple ToolRequests in one WorkerStep;
- absolute path;
- path escape;
- write outside Task scope;
- lifecycle-control write attempt;
- Worker-step budget exhaustion;
- any other deterministic authorization or safety-policy failure.

These stop safely on the first attempt.

### Repository Tool Errors

A well-formed, authorized Repository tool operation that returns ToolResult(ok=False) and continues within the same Worker session is not an automatic top-level Retry event.

Examples:

- safe read of a missing file;
- safe operational Repository tool failure already represented as ToolResult.

The Worker may react within the existing eight-step Runner interaction.

### Write Side-Effect Boundary

If a Repository write operation is attempted during a Runner attempt, automatic whole-Runner retry is disabled for that attempt.

This remains true even when:

- write_repo_text reports failure;
- the following Worker continuation fails;
- transport fails after the write;
- the system cannot prove whether a partial side effect occurred.

The policy is intentionally conservative.

A write attempt means deterministic Runner code reached the Repository write execution boundary after structural and authorization checks.

A rejected write that never reaches Repository write execution does not count as a write attempt, but the deterministic rejection itself remains non-retryable.

### Read-Only Attempts

Successful read operations do not create Repository mutation side effects.

Therefore a transient Worker/session failure after only read operations may remain retryable, subject to the total attempt limit.

### Safe Stop Outcome

When Retry is not permitted or the attempt limit is exhausted, the orchestration layer returns a deterministic safe-stop outcome.

The outcome must preserve:

- deterministic outcome classification, including normal completion, FAIL, or BLOCKED;
- final structured failure classification when applicable;
- total attempts consumed;
- readable error information;
- whether Repository write side-effect risk occurred.

Safe stop does not mean Repository Task PASS.

### FAIL vs BLOCKED

Retry V1 must distinguish deterministic FAIL from operational BLOCKED without parsing error-message text.

#### FAIL

Use FAIL when deterministic Harness policy establishes that the current Runner execution cannot continue safely because the request or interaction violated an approved rule.

Initial FAIL cases include:

- invalid or mismatched Task selection;
- non-ACTIVE Current Task;
- malformed ToolRequest;
- invalid call_id;
- unsupported or unknown tool;
- invalid argument shape;
- multiple ToolRequests in one WorkerStep;
- absolute path or path escape;
- write outside Task scope;
- lifecycle-control write attempt;
- Worker-step budget exhaustion;
- other deterministic authorization or safety-policy violations.

FAIL is not automatically retried.

#### BLOCKED

Use BLOCKED when execution cannot safely continue because of an operational or uncertain condition rather than a deterministic authorization violation.

Initial BLOCKED cases include:

- retryable transient Worker/session failure after the total attempt limit is exhausted;
- transient Worker/session failure after a Repository write attempt, where automatic retry is prohibited because side effects may already exist;
- another explicitly classified transient condition for which policy does not permit another attempt.

BLOCKED does not imply that the Repository Task itself is incorrect.

#### Normal Interaction Completion

A terminal zero-tool WorkerStep within Runner rules represents normal Runner interaction completion.

It is neither FAIL nor BLOCKED.

It is also not authoritative Repository Task PASS.

Repository PASS still requires existing Verification, Evidence, and Final Gate authority.

The later implementation must expose this distinction through structured orchestration metadata or an equivalent deterministic representation.

It does not automatically:

- complete the Task;
- run Verification;
- commit;
- modify Architecture;
- start the next Task.

### No Slow-Path Model Change in Retry V1

Retry V1 does not automatically:

- switch model;
- change model parameters;
- enable think:true;
- escalate to Codex;
- invoke another agent.

The existing default Worker remains the approved native Ollama + Qwen3:8B path.

A higher-reasoning slow path remains a possible later optimization, but requires separate Evidence and approval.

### Human Authority

Human Gates remain authoritative.

Qwen cannot:

- request an additional retry budget;
- classify its own failure as retryable;
- authorize a write retry;
- override Safe Stop;
- mark a Task complete.

## Accuracy and Performance

Correctness and side-effect safety take priority over retry success rate.

The normal successful path must not perform a second Runner execution.

Retry cost is incurred only for an explicitly classified retryable failure.

No Verification suite is repeated inside the Retry loop.

Final Repository completion remains governed by existing qh close / Verification / Final Gate authority.

## Consequences

The next implementation Task should:

1. add structured Runner failure/side-effect metadata with minimal contract change;
2. preserve existing successful Runner behavior;
3. add an orchestration layer above run_single_task;
4. permit at most one retry;
5. retry only transient failures with no write attempt;
6. stop immediately for deterministic safety failures;
7. return safe-stop Evidence after attempt exhaustion;
8. remain independently testable without live Ollama.

## Allowed Changes

- DECISIONS.md
- STATUS.md
- tasks/QH-V2-ARCH-007.md

## Forbidden Changes

- tools/**
- tests/**
- PROJECT.md
- REQUIREMENTS.md
- all other existing Task files
- all other Repository files

## Acceptance Criteria

1. ADR-009 records a two-total-attempt Retry V1 limit.
2. Retry remains above the Single-Task Runner.
3. Retry and the eight-WorkerStep budget remain separate concepts.
4. Retry decisions use structured failure metadata, not error-string parsing.
5. Only transient Worker/session failures are initial retry candidates.
6. Deterministic validation and safety failures are non-retryable.
7. Worker-step budget exhaustion is non-retryable.
8. Repository write attempt disables automatic whole-Runner retry.
9. Read-only transient failures may be retried.
10. ToolResult(ok=False) continuation is not confused with top-level Retry.
11. Retry V1 performs no automatic model/think-mode/Codex/agent escalation.
12. Retry V1 distinguishes deterministic FAIL from operational BLOCKED through structured metadata.
13. Normal Runner interaction completion is neither FAIL/BLOCKED nor authoritative Repository PASS.
14. Safe Stop grants no Task completion, Git, Verification, commit, or Architecture authority.
15. No production code is changed in this Architecture Task.

## Verification

Run exactly:

`git diff --check`

Then run:

`git status --short`

Confirm Architecture Task changes only:

- DECISIONS.md
- STATUS.md
- tasks/QH-V2-ARCH-007.md

## Stop Condition

Stop if this decision would require:

- weakening ADR-008 authority boundaries;
- retrying deterministic safety violations;
- retrying after Repository write side-effect risk;
- granting Qwen Retry authority;
- changing the Worker backend or reasoning mode;
- implementing production Retry code in this Architecture Task.

Do not begin Retry implementation until ADR-009 is recorded and this Task is COMPLETE - VERIFIED.
