# QH-V2-RUN-001B - Native Ollama Tool Interaction Adapter

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

QH-V2-RUN-001 - Single-Task Runner Integration

## Dependency

QH-V2-RUN-001A - COMPLETE - VERIFIED

## Architecture Basis

ADR-008 - Backend-Neutral Tool Interaction Contract

## Problem

QH-V2-RUN-001A provides backend-neutral ToolSpec, ToolRequest, ToolResult, and WorkerStep records.

The existing native Ollama Adapter remains transport-only:

- it accepts WorkerRequest;
- sends one native `/api/chat` request;
- returns WorkerResponse;
- it does not expose tools;
- it does not parse native `tool_calls`;
- it does not support tool-result continuation.

Single-Task Runner integration requires a tool-enabled Adapter boundary without exposing Ollama-native JSON to Runner orchestration.

## Local Compatibility Evidence

Before Human approval, a read-only local probe was executed against:

- native Ollama `/api/chat`
- model `qwen3:8b`
- `stream:false`
- `think:false`
- one advertised `read_repo_text` function tool

The real response contained one native tool call with:

- non-empty native `id`: `call_cv5gfs88`
- `function.index`: 0
- `function.name`: `read_repo_text`
- `function.arguments`: `{"relative_path": "PROJECT.md"}`

This confirms that the current approved local Worker path can supply the non-empty call identity required by ADR-008 ToolRequest.

001B must preserve this backend-supplied identity as ToolRequest.call_id.

If a future/native response omits or invalidates the required call identity, the Adapter must fail closed rather than inventing or silently repairing an ID.

## Local Continuation Evidence

A second read-only local probe verified the complete native Ollama tool-result continuation path with `qwen3:8b`.

First response:

- native call id: `call_veh5y2ur`
- tool name: `read_repo_text`
- arguments: `{"relative_path": "PROJECT.md"}`

The probe then preserved the assistant tool-call message and supplied a native tool-result message containing:

- role: `tool`
- tool_name: `read_repo_text`
- content: `PROBE-CONTENT`

The following `/api/chat` continuation returned normal assistant content:

`RESULT:PROBE-CONTENT`

This proves that the currently approved local Worker path supports the Adapter-owned conversation continuation required by this Task.

The Adapter must use the backend-neutral ToolResult.call_id to match the pending ToolRequest internally. Backend-specific continuation messages remain an Adapter responsibility and do not become Runner contract data.

## Goal

Extend the native Ollama Adapter with the smallest tool-enabled interaction/session boundary that translates between:

- backend-neutral ToolSpec / ToolResult / WorkerStep;
- native Ollama tools / messages / tool_calls.

Preserve the existing transport-only call_ollama_worker API and behavior unchanged.

Do not execute Repository tools or implement the Single-Task Runner loop in this Task.

## Required Behavior

### Existing Transport Path

`call_ollama_worker(...) -> WorkerResponse` remains available and behavior-compatible.

Its existing request remains transport-only and must not silently begin advertising tools.

### Tool-Enabled Session Boundary

Add a native Ollama tool-enabled interaction object or equivalent callable boundary with these semantics:

1. It is initialized from:
   - WorkerRequest;
   - backend-neutral tuple of ToolSpec;
   - existing Ollama connection/model/timeout configuration.

2. Initial execution:
   - translates ToolSpec values into native Ollama tool definitions;
   - sends the initial Worker task message;
   - uses `/api/chat`;
   - uses `stream:false`;
   - uses `think:false`;
   - parses the returned native message into WorkerStep.

3. Continuation:
   - accepts one backend-neutral ToolResult from deterministic Runner code;
   - associates it with the preceding ToolRequest/call_id;
   - appends the required native assistant/tool conversation state internally;
   - sends the continuation request;
   - returns the next WorkerStep.

4. Ollama-native message history and tool-call JSON remain internal to the Adapter.

The exact internal class/function names are implementation details of this Task.

## Native Tool Translation

ToolSpec must translate to an Ollama-compatible function tool definition.

The Adapter may translate:

- ToolSpec.name
- ToolSpec.description
- ToolSpec.input_schema

into the corresponding native Ollama tool schema.

The Runner must not construct or inspect that native schema.

## Native Tool Call Parsing

A valid native tool call must become one backend-neutral ToolRequest containing:

- a non-empty call_id;
- a non-empty tool name;
- arguments represented as Mapping[str, object].

The Adapter must preserve native call identity rather than inventing replacement IDs when an ID is supplied by the backend.

Malformed native tool-call structures must not be silently repaired.

## WorkerStep Semantics

A successfully decoded Ollama response becomes WorkerStep with:

- transport_ok = True;
- output_text from native message content;
- tool_requests containing parsed ToolRequest values;
- error = None.

Transport, JSON, UTF-8, response-schema, or malformed tool-call failures become WorkerStep with:

- transport_ok = False;
- no executable ToolRequest values;
- readable error Evidence.

A successful WorkerStep does not mean Repository Task PASS.

## Conversation Ownership

This Adapter owns only backend-specific conversation state required for native Ollama continuation.

It does not own:

- whether a requested tool is authorized;
- Repository root selection;
- Allowed/Forbidden scope;
- Repository tool execution;
- Runner loop count;
- step budget;
- retry/fallback;
- Git;
- Verification;
- Evidence;
- Final Gate;
- commit;
- Task lifecycle;
- Architecture decisions.

## Tool Result Boundary

The Adapter may accept ToolResult only as data supplied by deterministic Runner code.

It must not manufacture a successful ToolResult for a requested Repository operation.

It must not execute read_repo_text or write_repo_text.

## Multiple Tool Calls

The Adapter translates all structurally valid native tool calls into the ordered WorkerStep.tool_requests tuple.

It does not decide whether multiple requests are authorized.

The later QH-V2-RUN-001C Runner enforces ADR-008's zero-or-one ToolRequest execution rule and rejects multi-tool Worker steps before execution.

## Existing Contract Preservation

Do not change the field shape of:

- WorkerRequest
- WorkerResponse
- ToolSpec
- ToolRequest
- ToolResult
- WorkerStep

## Allowed Changes

- tools/ollama_worker.py
- tests/test_ollama_worker.py
- STATUS.md
- tasks/QH-V2-RUN-001B.md

## Forbidden Changes

- tools/harness_core.py
- tests/test_harness_core.py
- tools/repo_tools.py
- tests/test_repo_tools.py
- tools/qh.py
- tests/test_qh.py
- PROJECT.md
- REQUIREMENTS.md
- DECISIONS.md
- tasks/QH-V2-RUN-001.md
- tasks/QH-V2-RUN-001A.md
- all other existing task files
- all other Repository files

## Acceptance Criteria

1. Existing call_ollama_worker public behavior remains passing.
2. ToolSpec values are translated into native Ollama tool definitions.
3. Initial tool-enabled request uses `/api/chat`, `stream:false`, and `think:false`.
4. Valid native tool_calls become backend-neutral ToolRequest values.
5. Native call identity and argument mapping are preserved.
6. ToolResult can be continued through Adapter-owned native conversation state.
7. Native Ollama message/tool JSON does not escape as Runner contract data.
8. Malformed tool-call schema fails closed without executable ToolRequest output.
9. Adapter performs no Repository read/write execution.
10. Adapter gains no scope, Git, Verification, Evidence, Final Gate, retry, commit, Task lifecycle, or Architecture authority.
11. Focused Adapter tests cover initial request, parsing, continuation, malformed calls, and existing transport regression.
12. Existing Harness Core regression remains passing.
13. No file outside Allowed Changes is modified.

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

Stop if implementation requires:

- changing ADR-008;
- changing existing backend-neutral record shapes;
- exposing Ollama-native JSON as the Runner public contract;
- letting the Adapter authorize or execute Repository tools;
- implementing the Single-Task Runner loop;
- implementing retry/fallback;
- granting shell, Git, Verification, Evidence, Final Gate, commit, or Task lifecycle authority.

Do not begin QH-V2-RUN-001C in this Task.
