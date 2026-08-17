# QH-V2-ARCH-001 - Agent-Independent Native Local Worker Architecture



## Status



APPROVED - READY FOR IMPLEMENTATION



## Goal



Update the Qwen Harness V2 formal project documents to reflect the Human-approved

local Worker architecture based on the evidence gathered from OpenCode,

Qwen Code, native Ollama experiments, and the little-coder reference implementation.



This is a documentation and architecture-decision Task only.



Do not modify implementation code.



## Problem



The current formal specification identifies:



OpenCode + local Qwen



as the primary local Worker path.



Experiments showed:



- OpenCode + qwen2.5-coder:7b did not reliably produce executable tool calls.

- Qwen Code + qwen2.5-coder:7b showed the same tool-call problem.

- Qwen3:8B can produce structured native Ollama tool calls.

- Qwen3:8B with native Ollama `/api/chat`, `stream:false`, and `think:false`

successfully completed a real tool-call/result continuation loop.

- A real Repository file read through a Python-controlled tool loop succeeded.

- Qwen semantic/implementation output can still be wrong even when tool calling succeeds.

- Deterministic Git/Test/scope checks therefore remain necessary.

- little-coder provides external evidence that small local Qwen models benefit from

a model-aware Harness, bounded retry, controlled tool execution, and limited context.



## Decision



Adopt an agent-independent Worker architecture.



The Harness Core must not depend on OpenCode-specific behavior.



The current default local Worker candidate is:



Deterministic Python Harness

-> native Ollama API

-> Qwen3:8B



OpenCode is not removed.

It remains an optional alternative Worker/backend and future benchmark candidate.



Codex remains optional and is not required for Harness Core operation.



## Responsibility Boundary



### Qwen Worker



Qwen is responsible for semantic work such as:



- understanding an approved small Task;

- proposing or implementing small scoped changes;

- reasoning about implementation intent.



Qwen self-reported PASS is not authoritative.



### Deterministic Python Harness



Python Harness code is responsible for mechanically checkable behavior including:



- Task contract parsing;

- Allowed / Forbidden scope enforcement;

- Git baseline and changed-file inspection;

- tool permission and execution boundaries;

- approved verification command execution;

- exact-content and hash invariants;

- Evidence assembly;

- deterministic PASS / FAIL gates;

- bounded retry / stop behavior.



LLM output must not override deterministic failure Evidence.



## Worker Strategy



Initial Qwen3:8B Worker strategy:



- Fast path: native Ollama with `think:false`.

- Slow path: higher-reasoning retry when the fast path fails.

- Retry is bounded.

- Repeated failure terminates as FAIL or BLOCKED.

- Do not indefinitely increase prompt complexity after repeated failure.



Exact retry counts and model parameters may be tuned from benchmark Evidence.



## Safety Policy



Initial Harness behavior is fail-closed.



Malformed or invalid tool calls must not be silently repaired and executed.



Automatic repair techniques from other Harness implementations may be evaluated later,

but they are not part of this initial decision.



Tool execution permission belongs to deterministic Harness code, not to the LLM.



## Reference Implementation Policy



little-coder may be used as a reference for proven small-local-model techniques including:



- model-specific profiles;

- bounded retry;

- fast / slow reasoning paths;

- context management;

- read-before-edit;

- tool-call quality checks.



Qwen Harness will not copy little-coder wholesale.



The existing deterministic Task / Git / Test / Evidence safety model remains the

core of Qwen Harness.



## Existing ADR-001



ADR-001 - Deterministic Harness Core Before Further Orchestration remains Accepted.



The existing HC decomposition remains valid:



1. HC-001 - Task Contract Parser

2. HC-002 - Path / Scope Matcher

3. HC-003 - Git Baseline and Changed-File Evidence

4. HC-004 - Verification Command Runner

5. HC-005 - Exact / Hash Invariant Checks

6. HC-006 - Evidence Assembly

7. HC-007 - Deterministic Final Gate



This Task does not implement those components.



## Required Formal Document Changes



### PROJECT.md



Update the Primary Execution Model and Milestone 1 so that:



- the Harness is agent/backend independent;

- native Ollama + Qwen3:8B is the current default local Worker candidate;

- OpenCode is optional rather than required;

- Codex remains optional;

- the existing Reliability Principle remains intact;

- the corrupted Milestone 1 text is replaced with valid text.



### REQUIREMENTS.md



Update FR-002 and Milestone 1 so they do not require OpenCode.



Add requirements covering:



- Worker/backend independence;

- Harness-owned tool permission/execution;

- bounded retry and safe stop.



Change the Architecture decision authority wording so that:



- ChatGPT provides technical analysis and recommendations;

- final Architecture approval belongs to the Human;

- the Worker must not infer Architecture changes.



All existing deterministic safety requirements remain valid unless directly superseded

by this approved decision.



### DECISIONS.md



Keep ADR-001 unchanged.



Append:



ADR-002 - Agent-Independent Native Local Worker Architecture



recording the decision described by this Task.



### STATUS.md



Record that QH-V2-ARCH-001 is the current architecture-documentation Task while it is

being performed.



After this Task is verified and approved, HC-001 may be resumed.



## Allowed Changes



- `PROJECT.md`

- `REQUIREMENTS.md`

- `DECISIONS.md`

- `STATUS.md`



## Forbidden Changes



- `tools/**`

- `tests/**`

- `src/**`

- existing Task files

- fixture files

- all implementation code



## Acceptance Criteria



- PROJECT.md no longer requires OpenCode as the primary Worker path.

- Native Ollama + Qwen3:8B is recorded as the current default local Worker candidate.

- OpenCode remains optional.

- Codex remains optional.

- Reliability Principle is preserved.

- REQUIREMENTS.md reflects backend independence.

- REQUIREMENTS.md requires deterministic Harness-owned tool boundaries.

- REQUIREMENTS.md requires bounded retry / safe stop.

- Human is explicitly the final Architecture approval authority.

- ADR-001 remains unchanged.

- ADR-002 is added with the approved Worker architecture.

- STATUS.md records this Task correctly.

- No implementation code is modified.



## Verification



Verify with:



- `git diff -- PROJECT.md REQUIREMENTS.md DECISIONS.md STATUS.md`

- `git status --short`



Confirm that no file outside Allowed Changes was modified.



## Stop Condition



Stop after the formal documents are updated and externally reviewed.



Do not implement Worker Adapter code.

Do not modify HC-001 implementation.

Do not start HC-002.

Do not add LangGraph.

Do not add ECC routing.

