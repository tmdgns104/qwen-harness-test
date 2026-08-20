# QH-V2-RETRY-001 - Bounded Retry and Safe Stop Orchestration

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Architecture Basis

- ADR-009 - Bounded Retry and Safe Stop Policy
- QH-V2-RUN-001 - COMPLETE - VERIFIED
- QH-V2-ARCH-007 - COMPLETE - VERIFIED

## Problem

The Single-Task Runner is complete and verified, but RunnerResult currently exposes only:

- interaction_ok
- output_text
- steps_consumed
- error

Retry policy must not classify failures by parsing human-readable error text.

The Harness also needs to know whether a Repository write operation reached the execution boundary before deciding whether a whole-Runner retry is safe.

## Goal

Implement Retry V1 with:

1. structured Runner failure metadata;
2. Repository write-attempt tracking;
3. one orchestration layer above run_single_task;
4. at most two total Runner attempts;
5. retry only for transient Worker/session failures with no write attempt;
6. deterministic FAIL for safety/validation failures;
7. deterministic BLOCKED when transient execution cannot safely continue;
8. no automatic model/backend/reasoning-mode escalation.

## RunnerResult Extension

Extend RunnerResult with deterministic metadata sufficient for ADR-009.

The implementation must provide an equivalent to:

- failure_kind: structured value or None
- write_attempted: bool

Exact class/enum names are implementation details.

Existing fields remain:

- interaction_ok
- output_text
- steps_consumed
- error

Existing successful Runner behavior must remain compatible.

### Failure Classification

The Runner must classify failures without error-string parsing.

At minimum distinguish:

#### TRANSIENT_WORKER

Examples:

- Worker session creation/call exception;
- Worker transport failure;
- Worker continuation session/transport exception.

#### SAFETY

Examples:

- invalid/mismatched/non-ACTIVE Task;
- malformed ToolRequest;
- invalid call_id;
- unknown tool;
- invalid arguments;
- multi-tool WorkerStep;
- absolute/path-escape request;
- out-of-scope write;
- lifecycle-control write attempt.

#### STEP_BUDGET

- eight-WorkerStep limit exhausted while another tool is requested.

Normal terminal completion has no failure kind.

## Write Attempt Tracking

RunnerResult.write_attempted begins False.

It becomes True immediately before deterministic Runner code invokes Harness-owned write_repo_text after:

- ToolRequest structural validation;
- lifecycle-control validation;
- Task scope authorization.

It remains True for the rest of that Runner attempt.

This is true even if:

- write_repo_text raises;
- write_repo_text returns an operational failure;
- later Worker continuation fails.

Rejected writes that never reach write_repo_text execution keep write_attempted False.

## Retry Orchestration Layer

Add a separate orchestration module or equivalent boundary above run_single_task.

Preferred file:

tools/retry_runner.py

Preferred tests:

tests/test_retry_runner.py

The retry layer must call run_single_task rather than reimplementing the Worker tool loop.

## Retry Attempt Limit

MAX_RUNNER_ATTEMPTS = 2

Meaning:

- attempt 1: initial Runner execution;
- attempt 2: at most one automatic retry.

No third automatic attempt.

## Retry Decision

Retry only when all are true:

- Runner interaction did not complete normally;
- failure_kind is TRANSIENT_WORKER;
- write_attempted is False;
- attempt 1 has failed and attempt 2 remains available.

No other failure kind is retryable.

## Safe Outcome

The retry layer returns structured orchestration outcome metadata.

It must distinguish:

### NORMAL

Runner interaction terminated normally.

This is not Repository Task PASS.

### FAIL

Deterministic validation/safety failure or step-budget exhaustion.

No automatic retry.

### BLOCKED

Operational execution cannot safely continue.

Initial BLOCKED cases:

- second transient Worker/session failure exhausts retry budget;
- transient Worker/session failure after write_attempted=True;
- transient condition for which ADR-009 forbids another attempt.

The result should preserve at least:

- outcome kind;
- attempts consumed;
- final RunnerResult or equivalent data;
- readable error information;
- write side-effect risk.

Exact class/enum names are implementation details.

## No Error-String Policy

Retry decisions must never depend on:

- substring search in RunnerResult.error;
- exact comparison of error text;
- parsing exception message wording.

Only structured Runner metadata may determine Retry / FAIL / BLOCKED.

## Repository Tool Errors

ToolResult(ok=False) handled within the Runner loop is not a top-level retry event by itself.

If the Worker later terminates normally, the retry layer returns NORMAL.

If a later transient Worker failure occurs:

- retry may occur only if write_attempted is False;
- otherwise return BLOCKED.

## No Model Escalation

Retry V1 must not:

- switch model;
- enable think:true;
- alter Ollama parameters;
- invoke Codex;
- invoke another agent;
- perform fallback routing.

## Authority Boundary

Retry orchestration does not own:

- Repository scope policy;
- Repository tool execution;
- Git;
- Verification;
- Evidence;
- Final Gate;
- commit;
- Task start/complete;
- Architecture mutation.

Qwen cannot:

- request more attempts;
- mark a failure retryable;
- override FAIL/BLOCKED;
- authorize retry after a write attempt.

## Accuracy and Performance

Accuracy and side-effect safety have priority over retry success rate.

Performance requirements:

- successful first attempt causes no second Runner execution;
- safety FAIL causes no second Runner execution;
- retry cost occurs only for eligible transient failures;
- no Verification suite runs inside retry orchestration;
- no duplicate scope engine or Worker loop is introduced.

## Required Tests

### Runner Metadata

Focused tests must cover:

1. normal terminal completion -> failure_kind None.
2. normal completion -> write_attempted False when no write occurred.
3. transient session creation failure classification.
4. Worker transport failure classification.
5. Worker continuation failure classification.
6. malformed/unknown/multi-tool/scope/lifecycle failures classify SAFETY.
7. step-budget exhaustion classifies STEP_BUDGET.
8. successful Repository write sets write_attempted True.
9. write_repo_text operational failure still sets write_attempted True.
10. rejected out-of-scope write keeps write_attempted False.

### Retry Orchestration

Focused tests must cover:

11. first-attempt NORMAL -> one Runner call only.
12. first-attempt SAFETY -> FAIL and one Runner call only.
13. first-attempt STEP_BUDGET -> FAIL and one Runner call only.
14. first transient failure with no write -> exactly one retry.
15. transient then NORMAL -> NORMAL with two attempts.
16. transient then transient -> BLOCKED with two attempts.
17. transient failure with write_attempted=True -> BLOCKED with one attempt.
18. no third Runner execution occurs.
19. retry decision works independently of error-message wording.
20. Qwen terminal text such as PASS does not become Repository PASS.

Tests must not require live Ollama.

## Allowed Changes

- tools/task_runner.py
- tests/test_task_runner.py
- tools/retry_runner.py
- tests/test_retry_runner.py
- STATUS.md
- tasks/QH-V2-RETRY-001.md

## Forbidden Changes

- tools/harness_core.py
- tests/test_harness_core.py
- tools/ollama_worker.py
- tests/test_ollama_worker.py
- tools/repo_tools.py
- tests/test_repo_tools.py
- tools/qh.py
- tests/test_qh.py
- DECISIONS.md
- PROJECT.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- all other existing Task files
- all other Repository files

## Acceptance Criteria

1. Runner failure classification is structured.
2. Retry policy performs no error-string parsing.
3. Runner tracks Repository write-attempt side-effect risk.
4. Retry V1 allows at most two total Runner attempts.
5. Only transient Worker/session failures with no write attempt may retry.
6. Deterministic safety failure stops as FAIL.
7. Step-budget exhaustion stops as FAIL.
8. Retry exhaustion stops as BLOCKED.
9. Transient failure after write attempt stops as BLOCKED.
10. Normal Runner completion is NORMAL but not Repository PASS.
11. Successful first attempt performs no retry.
12. ToolResult(ok=False) continuation is not confused with top-level Retry.
13. Existing eight-WorkerStep Runner limit remains unchanged.
14. Existing Worker tool authority remains unchanged.
15. No model/think/Codex/agent escalation is introduced.
16. Focused Retry tests pass without live Ollama.
17. Existing task_runner regression remains passing.
18. Existing Ollama Adapter regression remains passing.
19. Existing Repository tool regression remains passing.
20. Existing Harness Core regression remains passing.
21. No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_retry_runner`

Then run:

`python -m unittest tests.test_task_runner`

Then run:

`python -m unittest tests.test_ollama_worker`

Then run:

`python -m unittest tests.test_repo_tools`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop if implementation requires:

- changing ADR-009;
- retrying deterministic safety failures;
- retrying step-budget exhaustion;
- retrying after Repository write side-effect risk;
- parsing error strings to decide retry;
- changing Worker tool authority;
- changing the eight-step Runner budget;
- model/backend/reasoning-mode escalation;
- Git, Verification, Final Gate, commit, or Task lifecycle authority.

Do not begin Minimal CLI work in this Task.
