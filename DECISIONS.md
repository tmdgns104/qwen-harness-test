# Qwen Harness V2 Decisions

## ADR-001 - Deterministic Harness Core Before Further Orchestration

### Status
Accepted

### Context
Qwen Harness experiments showed that local Qwen can successfully perform small implementation tasks, but LLM self-report and file-edit behavior are not sufficiently reliable to serve as the final safety or completion authority.

Observed evidence includes:
- small one-file implementation and bug-fix tasks can succeed;
- a small related two-file task can succeed when task-local execution discipline is explicit;
- Worker/Verifier self-reported PASS is not authoritative;
- prompt-only Allowed/Forbidden scope rules can be violated;
- long Markdown append work can damage existing content even when the requested new content is otherwise correct;
- deterministic Git/Test/hash checks can detect such damage.

### Decision
Harness behavior that is already deterministic and mechanically checkable will be implemented in Python rather than repeatedly delegated to an LLM.

LLMs remain responsible for work that requires semantic reasoning, such as:
- understanding an approved Task;
- implementing small scoped code changes;
- semantic review of implementation intent.

Python Harness Core will become responsible for deterministic workflow and safety behavior, including at minimum:
- parsing Task change-scope contracts;
- matching Allowed Changes and Forbidden Changes;
- checking the Git baseline and actual changed paths;
- running approved verification commands and capturing exit results;
- checking exact content, hashes, or other deterministic invariants when a Task defines them;
- assembling objective Evidence;
- producing deterministic PASS/FAIL gate results for mechanically decidable conditions.

An LLM PASS must never override deterministic FAIL Evidence.

### Implementation Strategy
The deterministic core will be implemented incrementally as small Tasks.

Initial decomposition:
1. HC-001 - Task Contract Parser
2. HC-002 - Path / Scope Matcher
3. HC-003 - Git Baseline and Changed-File Evidence
4. HC-004 - Verification Command Runner
5. HC-005 - Exact / Hash Invariant Checks
6. HC-006 - Evidence Assembly
7. HC-007 - Deterministic Final Gate

Each Task must include its own Acceptance Criteria and Verification and must be completed from objective Evidence before the next Task begins.

### Consequences
- Qwen responsibilities stay narrow.
- Safety does not depend only on prompt compliance.
- Repeated deterministic checks move out of Worker/Verifier reasoning.
- `/work` and `/verify` may later consume Python-generated Evidence rather than recreating objective checks through LLM reasoning.
- Evidence Collector work is resumed only in this smaller incremental form.
- ECC-inspired routing and LangGraph orchestration remain later phases and are not introduced as part of this decision.

## ADR-002 - Agent-Independent Native Local Worker Architecture

### Status
Accepted

### Context
The original local Worker path was coupled to OpenCode + local Qwen.

Subsequent experiments showed that:
- qwen2.5-coder:7b did not reliably produce executable tool calls through OpenCode or Qwen Code;
- Qwen3:8B produced structured tool calls through the native Ollama API;
- a Python-controlled native Ollama tool-call/result continuation loop succeeded against a real Repository file;
- correct tool calling does not guarantee correct semantic or implementation output;
- deterministic scope, Git, test, invariant, and Evidence checks therefore remain necessary;
- little-coder provides a useful external reference for small-local-model Harness techniques such as bounded retry, model-aware reasoning paths, context control, and tool-quality checks.

### Decision
Adopt an agent-independent local Worker architecture.

The Harness Core must not depend on OpenCode-specific behavior or any single Agent frontend.

The current default local Worker candidate is:

Deterministic Python Harness
-> native Ollama API
-> Qwen3:8B

OpenCode remains an optional alternative Worker/backend and future benchmark candidate.
Codex remains an optional high-capability executor and is not required for Harness Core operation.

The deterministic Python Harness owns mechanically checkable behavior including tool permission/execution boundaries, Task scope enforcement, Git Evidence, verification execution, invariants, Evidence assembly, and final PASS/FAIL gating.

Qwen remains responsible for semantic reasoning and small scoped implementation work. Qwen self-reported PASS is not authoritative.

### Worker Strategy
- Use a low-cost fast path first, currently native Ollama with `think:false`.
- A bounded higher-reasoning slow path may be used after fast-path failure.
- Repeated failure terminates as FAIL or BLOCKED.
- Exact retry counts and model parameters may be tuned from benchmark Evidence.
- Do not indefinitely increase prompt complexity after repeated failure.

### Safety Policy
Initial behavior is fail-closed.

Malformed or invalid tool calls must not be silently repaired and executed. Tool execution authority belongs to deterministic Harness code rather than the LLM.

### Reference Policy
little-coder may be used as a reference implementation for proven small-local-model techniques, but Qwen Harness will not copy it wholesale.

The existing Task / Git / Test / Evidence safety model remains the core of Qwen Harness.

### Consequences
- ADR-001 remains Accepted and unchanged.
- HC-001 through HC-007 remain the deterministic Harness Core implementation sequence.
- Worker backend integration can be implemented behind an agent-independent boundary.
- OpenCode can later be compared against the native Worker path using the same regression Evidence.
- ECC-inspired routing, sub-agents, and LangGraph remain later-phase work.
