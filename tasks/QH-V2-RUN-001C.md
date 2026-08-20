# QH-V2-RUN-001C - Deterministic Single-Task Runner Loop

## Status

COMPLETE - VERIFIED

## Parent

QH-V2-RUN-001 - Single-Task Runner Integration

## Dependencies

- QH-V2-RUN-001A - COMPLETE - VERIFIED
- QH-V2-RUN-001B - COMPLETE - VERIFIED

## Architecture Basis

- ADR-004 - Post-HC-007 Worker Integration Architecture
- ADR-008 - Backend-Neutral Tool Interaction Contract
- QH-V2-RUN-001 parent contract

## Problem

The Repository now has:

- deterministic Harness Core authority;
- backend-neutral ToolSpec / ToolRequest / ToolResult / WorkerStep records;
- Harness-owned read_repo_text and write_repo_text tools;
- shared ChangeScope / is_path_allowed authorization semantics;
- native Ollama tool-call translation and continuation through OllamaToolSession.

What is still missing is the deterministic orchestration layer that connects those pieces for exactly one active Repository Task.

Without that Runner:

- Qwen can request tools but no Harness-owned loop evaluates those requests;
- current Task scope is not yet injected into Worker write operations;
- zero/one/multiple ToolRequest policy is not yet enforced;
- unknown or malformed Worker requests are not rejected by orchestration;
- Worker interaction does not yet have a finite execution bound.

## Historical Safety Evidence

Previous Qwen Harness experiments showed that even small Qwen3:8B Tasks can violate prompt-declared Allowed Changes.

Therefore:

- prompt instructions are not authorization;
- Qwen cannot choose or expand Repository scope;
- deterministic Harness code must authorize tool execution;
- Qwen self-reported PASS remains non-authoritative.

## Goal

Implement the smallest deterministic Single-Task Runner that:

1. runs only the explicitly selected ACTIVE current Task;
2. sends the complete current Task contract to the Worker;
3. exposes only read_repo_text and write_repo_text;
4. validates each backend-neutral WorkerStep;
5. executes at most one authorized ToolRequest from a WorkerStep;
6. injects current Task Allowed/Forbidden scope into write_repo_text;
7. returns safe Repository tool execution results to the Worker;
8. stops fail-closed on invalid or unauthorized orchestration requests;
9. enforces a finite deterministic Worker-step budget;
10. never grants Qwen Task PASS, Git, Verification, Evidence, commit, lifecycle, shell, or Architecture authority.

This Task implements Runner orchestration only.

## Current Task Selection

The Runner must receive an explicit Task identifier.

Before Worker execution it must deterministically confirm that:

- STATUS.md exists;
- STATUS.md identifies the same Task identifier as Current Task;
- that Current Task is ACTIVE;
- tasks/<TASK_ID>.md exists.

A mismatched, missing, malformed, or non-ACTIVE current Task must fail before Worker or Repository tool execution.

The Runner must not start, complete, or switch Tasks.

The exact helper/function names are implementation details.

## Task Context

The Runner must read the selected Task Markdown from:

tasks/<TASK_ID>.md

The WorkerRequest must include the complete current Task contract.

A small deterministic wrapper/header may be added around the Task Markdown, but requirements from the Task must not be silently removed, expanded, or reinterpreted.

## Scope Loading

The Runner must parse the current Task Markdown with the existing Harness Core:

parse_change_scope(...)

The resulting ChangeScope remains the Repository Task authorization scope used by the Runner.

Scope should be loaded once per Runner execution rather than reparsed for every write request.

The Runner must not create a second independent path-pattern authorization engine.

In addition, Worker write authority must be strictly narrower than overall Task lifecycle change authority.

The Worker must never be allowed to write:

- STATUS.md
- the active Task contract file tasks/<TASK_ID>.md

These are Harness/Human lifecycle-control files even when they appear in the Task's overall Allowed Changes for start/close bookkeeping.

This fixed lifecycle-control deny is an additional authority boundary, not a replacement path-pattern scope engine.

## Worker Tool Surface

Exactly these Harness-owned Repository tools are exposed:

### read_repo_text

Worker arguments:

- relative_path: string

The Worker does not supply Repository root.

### write_repo_text

Worker arguments:

- relative_path: string
- content: string

The Worker does not supply:

- allowed_changes
- forbidden_changes
- Repository root

The Runner supplies those deterministic values.

No other Worker tool is authorized in this Task.

## Tool Schemas

The Runner must construct backend-neutral ToolSpec values for:

- read_repo_text
- write_repo_text

Schemas must require the expected argument fields and reject unsupported argument shapes in deterministic Runner validation.

The Runner, not Qwen, determines which tool names exist.

## ToolRequest Validation

Before executing a requested tool, the Runner must validate the backend-neutral ToolRequest.

Common requirements:

- call_id is a non-empty string;
- name is a non-empty string;
- arguments is a Mapping;
- tool name is one of the two explicitly supported tools.

read_repo_text requires exactly:

- relative_path: non-empty string

write_repo_text requires exactly:

- relative_path: non-empty string
- content: string

Unknown, extra, missing, or incorrectly typed arguments are rejected fail-closed before Repository tool execution.

Repository-relative paths must not be absolute or contain parent-directory escape components.

## Worker Step Rule

For each WorkerStep:

### Transport Failure

If transport_ok is False:

- Runner stops fail-closed;
- no ToolRequest from that step is executed.

### Zero ToolRequest

If tool_requests is empty:

- Worker interaction terminates normally;
- terminal Worker output may be returned as Runner interaction output;
- this does NOT mean Repository Task PASS.

### One ToolRequest

If exactly one ToolRequest exists:

- validate it;
- authorize it;
- execute it through deterministic Harness-owned Repository tools;
- construct ToolResult;
- continue the same Worker session.

### More Than One ToolRequest

If more than one ToolRequest exists:

- reject the step fail-closed;
- execute none of those ToolRequests;
- do not partially execute the first request.

## Read Execution

For a valid read_repo_text request:

- Runner supplies repo_root;
- Harness-owned read_repo_text performs Repository path safety and text reading.

A safe operational failure after a structurally valid request, such as:

- file not found;
- directory requested as text;
- readable filesystem/encoding failure;

may become:

ToolResult(
    call_id=<same call id>,
    ok=False,
    output="",
    error=<readable deterministic error>
)

and may be returned to the Worker for continuation.

The Runner itself does not repair the requested path.

## Write Authorization and Execution

For a valid write_repo_text request:

1. Runner determines the normalized Repository-relative path.
2. Runner rejects lifecycle-control paths before Repository write execution:
   - STATUS.md
   - tasks/<TASK_ID>.md
3. Runner checks the current Task ChangeScope with existing is_path_allowed(...).
4. If lifecycle-control or scope authorization fails:
   - stop fail-closed;
   - do not call write_repo_text.
5. If authorization succeeds:
   - call Harness-owned write_repo_text;
   - inject:
     - repo_root;
     - current Task scope.allowed;
     - current Task scope.forbidden.

The Worker must never provide or override allowed_changes or forbidden_changes.

write_repo_text retains its own deterministic scope check as defense in depth.

## Repository Tool Errors

After a request has passed Runner structural and authorization checks, safe Repository tool execution failures may be represented as ToolResult(ok=False) and returned to the Worker.

This is tool-result continuation, not Retry policy.

The Runner must not silently retry a failed operation.

## Step Budget

The initial Single-Task Runner Worker-step budget is fixed at:

8 WorkerSteps maximum per Runner execution.

Budget semantics:

- the initial session.start() response consumes one Worker step;
- each continue_with_tool_result(...) response consumes one Worker step;
- a terminal zero-tool WorkerStep within the budget may end normally;
- if the final allowed WorkerStep still requests another tool, Runner stops before executing that requested tool;
- no ninth Worker interaction is allowed.

This means the execution is finite even if Qwen repeatedly requests tools.

The value 8 is intentionally small because current Qwen Subtasks are designed around narrow goals and usually 1-3 target files, while still leaving room for several read/write interactions and a terminal response.

This budget is not:

- bounded Retry;
- fallback;
- another model attempt;
- Task rerun.

Those remain later work.

## Session Boundary

Production Runner execution may use OllamaToolSession from QH-V2-RUN-001B.

Tests must be able to provide a deterministic fake/session substitute so Runner behavior can be verified without requiring a live Ollama server.

The Runner must interact through backend-neutral WorkerStep / ToolRequest / ToolResult semantics.

It must not inspect Ollama-native tool_calls JSON.

## Runner Outcome

The Runner may return a small deterministic Runner-specific result or equivalent value describing:

- whether Runner interaction terminated normally;
- terminal Worker output;
- Worker steps consumed;
- readable Runner error when stopped.

Exact result class/function names are implementation details.

A successful Runner outcome means only:

the deterministic Worker interaction completed within Runner rules.

It does NOT mean:

- Verification PASS;
- Evidence PASS;
- Final Gate PASS;
- Task COMPLETE.

## Authority Boundaries

The Runner owns:

- selected current Task validation;
- Task context loading;
- ToolSpec selection;
- ToolRequest validation;
- zero/one/multiple request enforcement;
- Repository tool dispatch;
- write scope injection;
- finite Worker-step budget;
- deterministic fail-closed orchestration.

The Runner does not own:

- Architecture changes;
- Task decomposition;
- Task start;
- Task completion;
- Git commands;
- commits;
- Verification command execution;
- Evidence collection authority;
- Final Gate;
- retry/fallback;
- shell commands;
- general filesystem operations outside Harness-owned Repository tools.

Qwen receives none of those authorities.

## Accuracy and Performance Boundary

Correctness and safety take priority over speed.

Within that boundary:

- Task Markdown should be loaded once per run;
- ChangeScope should be parsed once per run;
- no Verification suite is executed inside the Worker tool loop;
- no redundant Repository scope engine is introduced;
- focused Runner tests are used during development;
- final Task close remains the authoritative full Verification path.

Do not weaken validation or Verification to improve speed.

## Required Tests

Focused deterministic tests must cover at least:

1. matching ACTIVE current Task starts Worker interaction.
2. mismatched Task ID fails before Worker execution.
3. non-ACTIVE current Task fails before Worker execution.
4. full Task Markdown reaches WorkerRequest.
5. only read_repo_text and write_repo_text ToolSpecs are exposed.
6. terminal zero-tool WorkerStep ends normally.
7. one valid read request executes and continues.
8. one valid in-scope write executes and current Task scope is enforced.
9. Worker cannot provide or override write scope.
10. Worker cannot write STATUS.md or the active Task contract file.
11. unknown tool fails before Repository tool execution.
12. malformed argument shape fails before Repository tool execution.
13. absolute/path-escape request fails before Repository tool execution.
14. multiple ToolRequests fail before any Repository tool execution.
15. transport failure stops fail-closed.
16. safe Repository tool error becomes ToolResult(ok=False) and can continue.
17. eighth WorkerStep may terminate normally.
18. an eighth WorkerStep requesting another tool stops without executing that tool.
19. no ninth Worker interaction occurs.
20. Qwen/Worker terminal text is not treated as Harness Task PASS.

Tests must not require live Ollama.

## Allowed Changes

- tools/task_runner.py
- tests/test_task_runner.py
- STATUS.md
- tasks/QH-V2-RUN-001C.md

## Forbidden Changes

- tools/harness_core.py
- tests/test_harness_core.py
- tools/ollama_worker.py
- tests/test_ollama_worker.py
- tools/repo_tools.py
- tests/test_repo_tools.py
- tools/qh.py
- tests/test_qh.py
- PROJECT.md
- REQUIREMENTS.md
- ARCHITECTURE.md
- DECISIONS.md
- tasks/QH-V2-RUN-001.md
- tasks/QH-V2-RUN-001A.md
- tasks/QH-V2-RUN-001B.md
- all other existing Task files
- all other Repository files

## Acceptance Criteria

1. Single-Task Runner validates the explicit Task against ACTIVE Current Task.
2. Complete current Task Markdown is supplied to WorkerRequest.
3. Runner exposes only read_repo_text and write_repo_text.
4. Runner depends only on backend-neutral tool interaction records, not Ollama-native tool_calls JSON.
5. Zero/one/multiple ToolRequest behavior follows ADR-008.
6. Unknown or malformed requests fail closed before Repository tool execution.
7. write_repo_text scope is supplied only by deterministic Runner state.
8. Out-of-scope write is rejected before write_repo_text execution.
9. STATUS.md and the active Task contract file are never Worker-writable, even when present in overall Task Allowed Changes.
10. Existing ChangeScope / is_path_allowed remains the path-pattern authorization engine.
11. Safe authorized Repository tool execution errors may return ToolResult(ok=False).
12. Worker interaction has an exact eight-step maximum.
13. No ninth Worker interaction or post-budget tool execution is possible.
14. Runner implements no Retry/fallback.
15. Runner grants no shell, Git, Verification, Evidence, Final Gate, commit, Task lifecycle, or Architecture authority.
16. Worker terminal output is not authoritative Repository PASS.
17. Focused Runner tests pass without live Ollama.
18. Existing Ollama Adapter regression remains passing.
19. Existing Repository tool regression remains passing.
20. Existing Harness Core regression remains passing.
21. No file outside Allowed Changes is modified.

## Verification

Run exactly:

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

- changing ADR-008;
- changing backend-neutral Worker or tool record shapes;
- changing OllamaToolSession contract;
- changing Repository tool authorization semantics;
- exposing native Ollama JSON to Runner;
- giving Qwen scope selection authority;
- giving Qwen shell, Git, Verification, Evidence, Final Gate, commit, lifecycle, or Architecture authority;
- adding Retry/fallback;
- automatically starting or completing another Task.

Do not begin Parent integration review or Retry/Safe Stop work in this Task.
