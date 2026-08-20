# QH-V2-CLI-001 - Minimal Worker-facing CLI Integration

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Architecture Basis

- ADR-005 - Revised Milestone 1 sequence
- ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints
- ADR-007 - Verification Performance Optimization
- ADR-008 - Backend-Neutral Tool Interaction Contract
- ADR-009 - Bounded Retry and Safe Stop Policy
- QH-V2-RUN-001 - COMPLETE - VERIFIED
- QH-V2-RETRY-001 - COMPLETE - VERIFIED

This Task implements Milestone 1 stage 8:

Minimal Worker-facing CLI integration.

It does not implement E2E Regression.

## Problem

The Repository currently has a deterministic workflow CLI:

`python tools\qh.py <command>`

with:

- status
- preflight
- verify
- review
- start
- close

The Worker execution path is already implemented through:

Single-Task Runner
-> bounded Retry / Safe Stop orchestration

but there is no minimal user-facing CLI command that invokes that path.

A Human currently cannot execute the approved Worker path through the existing qh workflow utility.

## Goal

Add one minimal Worker-facing command to the existing qh CLI:

`python tools\qh.py run <TASK-ID>`

The command must:

1. reuse the existing bounded Retry orchestration;
2. require an explicit Task ID;
3. preserve Runner validation of the ACTIVE Task;
4. report structured execution outcome;
5. clearly distinguish Worker output from authoritative Repository PASS;
6. return deterministic process exit status;
7. avoid duplicating Runner, Retry, scope, tool, Verification, Evidence, or Final Gate logic;
8. preserve all existing qh commands unchanged.

## Scope

### CLI Command

Add:

`run <TASK-ID>`

to `tools/qh.py`.

Example:

`python tools\qh.py run QH-V2-TEST-001`

The exact active Task match remains enforced by the existing Single-Task Runner.

The CLI must not create a second current-Task parser or Task authorization engine for Worker execution.

### Execution Ownership

The CLI command must delegate Worker execution to the existing Retry layer.

Conceptually:

qh run
-> run_with_retry(...)
-> run_single_task(...)
-> Worker session / Harness-owned Repository tools

The CLI must not reimplement:

- the Worker loop;
- the eight-WorkerStep budget;
- retry eligibility;
- retry attempt counting;
- ToolRequest validation;
- Repository read/write execution;
- ChangeScope authorization;
- lifecycle write protection.

### Import / Integration Rule

Do not refactor the existing qh import architecture merely to add this command.

A small lazy/local import or another minimal integration technique is permitted if it preserves existing qh command behavior and avoids unnecessary Worker-stack loading for unrelated commands.

No broad CLI/parser rewrite is required.

## Output Contract

The run command must expose the final structured orchestration result in human-readable form.

The output must include at least:

- Task ID
- Outcome
- Attempts consumed
- Failure Kind, or an explicit none value
- Repository write side-effect risk
- Worker Output when present
- Error when present

Recommended labels:

- `Task:`
- `Outcome:`
- `Attempts:`
- `Failure Kind:`
- `Write Side Effect Risk:`
- `Worker Output:`
- `Error:`

Equivalent wording is allowed if tests freeze the resulting contract.

### Outcome Values

The CLI must preserve Retry V1 outcome semantics:

- NORMAL
- FAIL
- BLOCKED

The CLI must not reinterpret these values.

### Worker Output Is Non-Authoritative

Worker text must be clearly labeled as Worker output.

For example, if Qwen returns:

`PASS`

the CLI may display:

`Worker Output: PASS`

but must not display or imply:

- Repository PASS;
- Verification PASS;
- Final Gate PASS;
- Task COMPLETE;
- Task VERIFIED.

A NORMAL Worker interaction is not Repository completion.

## Exit Code Contract

Minimal CLI V1:

- NORMAL -> exit code 0
- FAIL -> non-zero
- BLOCKED -> non-zero

FAIL and BLOCKED do not need distinct non-zero process codes in this Task.

The structured printed Outcome remains the authoritative distinction between them.

## Task Selection

`run` requires an explicit Task ID.

Missing Task ID must return a deterministic CLI error through the existing qh error handling style.

The existing Runner remains responsible for rejecting:

- mismatched Task ID;
- non-ACTIVE Task;
- missing Task contract;
- invalid Task state.

Do not duplicate those checks in the CLI.

## Retry Semantics

The CLI does not decide whether to retry.

It must use existing QH-V2-RETRY-001 behavior:

- maximum two Runner attempts;
- retry only transient Worker/session failure;
- no automatic retry after Repository write attempt;
- SAFETY -> FAIL;
- STEP_BUDGET -> FAIL;
- exhausted transient -> BLOCKED.

No error-string parsing is permitted.

## Safety Boundary

The run command must not directly gain authority over:

- Repository read/write tools;
- shell execution;
- arbitrary filesystem access;
- Git mutation;
- Verification execution;
- Evidence assembly;
- Final Gate;
- commit;
- Task completion;
- Task start;
- Architecture modification;
- model switching;
- think:true escalation;
- Codex escalation;
- another agent.

Worker tool authority remains owned by the existing Runner/Harness path.

## Lifecycle Boundary

`qh run` must not automatically call:

- qh verify;
- qh review;
- qh close;
- git commit;
- qh start.

Successful Worker execution leaves Repository completion to the existing Human-controlled lifecycle.

## Existing CLI Compatibility

The following existing commands must remain behaviorally compatible:

- status
- preflight
- verify
- review
- start
- close

Do not convert the CLI to a new parser architecture merely for this Task.

## Testing Strategy

Unit/integration tests for this Task must not require live Ollama.

Tests should inject or substitute a deterministic Retry callable/outcome at the CLI boundary.

Real Ollama + real small Repository execution belongs to the following E2E Regression Task.

## Required Tests

At minimum verify:

1. `run` is accepted as a qh command.
2. `run` requires an explicit Task ID.
3. the provided Task ID is passed to Retry orchestration unchanged.
4. NORMAL prints Outcome NORMAL.
5. NORMAL returns exit code 0.
6. FAIL prints Outcome FAIL.
7. FAIL returns non-zero.
8. BLOCKED prints Outcome BLOCKED.
9. BLOCKED returns non-zero.
10. attempts consumed is printed.
11. structured Failure Kind is printed.
12. absent Failure Kind is represented deterministically.
13. write-side-effect risk is printed.
14. Worker output is printed only/labeled as Worker output when present.
15. Worker output text `PASS` does not become Repository PASS or VERIFIED output.
16. Error is printed when present.
17. CLI does not parse error wording to determine outcome.
18. run command delegates to Retry rather than Runner directly.
19. run command does not directly invoke Repository tools.
20. existing qh command regression remains PASS.

Tests must not call live Ollama.

## Performance

The CLI must add no duplicate Runner attempt.

The normal path is:

one CLI invocation
-> one Retry orchestration invocation
-> normally one Runner attempt

The CLI must not run Verification suites automatically.

Worker-related modules should not force unnecessary work for unrelated qh commands where a minimal integration avoids it.

Correctness and safety remain higher priority than micro-optimization.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh_worker_run.py`
- `STATUS.md`
- `tasks/QH-V2-CLI-001.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tests/test_harness_core.py`
- `tools/task_runner.py`
- `tests/test_task_runner.py`
- `tools/retry_runner.py`
- `tests/test_retry_runner.py`
- `tools/ollama_worker.py`
- `tests/test_ollama_worker.py`
- `tools/repo_tools.py`
- `tests/test_repo_tools.py`
- `DECISIONS.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- other Task files
- unrelated Repository files

## Acceptance Criteria

1. Existing qh CLI remains operational.
2. `run <TASK-ID>` exists.
3. run requires explicit Task ID.
4. run delegates to the existing Retry orchestration.
5. Retry policy is not duplicated.
6. Runner logic is not duplicated.
7. Worker tools are not called directly by qh.
8. NORMAL is reported as NORMAL.
9. FAIL is reported as FAIL.
10. BLOCKED is reported as BLOCKED.
11. NORMAL returns exit code 0.
12. FAIL and BLOCKED return non-zero.
13. attempts consumed is visible.
14. structured failure kind is visible.
15. write-side-effect risk is visible.
16. Worker output remains explicitly non-authoritative.
17. Worker text `PASS` cannot be confused with Repository PASS.
18. no automatic Verification, review, close, commit, or lifecycle mutation is introduced.
19. tests require no live Ollama.
20. existing qh regression remains PASS.
21. no forbidden file changes occur.

## Verification

Run exactly:

`python -m unittest tests.test_qh_worker_run`

`python -m unittest tests.test_qh`

`python -m unittest tests.test_retry_runner`

`python -m unittest tests.test_task_runner`

`python -m unittest tests.test_ollama_worker`

`python -m unittest tests.test_repo_tools`

`python -m unittest tests.test_harness_core`

`git diff --check`

`git status --short`

## Stop Conditions

STOP and report before continuing if implementation requires:

- changing ADR-009 Retry policy;
- changing the two-attempt limit;
- changing the eight-WorkerStep Runner budget;
- changing Worker tool authority;
- direct qh access to Repository edit tools;
- automatic Verification or Final Gate execution from run;
- automatic Task completion or commit;
- Architecture changes;
- model/backend escalation;
- live Ollama as a unit-test dependency;
- broad qh parser refactoring;
- E2E implementation inside this Task.

E2E Regression remains the next separate Milestone 1 Task.
