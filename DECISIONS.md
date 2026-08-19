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

## ADR-003 - Verified Problem Resolution and Automation Escalation

Status: Accepted

### Decision

- Verified operational failures and their verified resolutions are recorded in `docs/verified_problem_resolutions.md`.
- When the same failure shape appears again, reuse the recorded verified resolution and Evidence instead of rediscovering the recovery procedure from scratch.
- Repeated or error-prone manual recovery procedures should be promoted to a small Python utility through a separate approved Task.
- Automation promotion does not override Architecture, current Task scope, or the HC-001 through HC-007 implementation sequence.
- Worker Adapter implementation remains deferred until the Architecture explicitly permits it.

### Rationale

Operational failures observed during Harness development included CMD parsing, accidental artifacts, candidate isolation, overly broad cleanup, nested escaping, malformed Worker output, and opaque payload corruption. Recording only the failure without the verified resolution would not prevent recurrence.

The Repository therefore preserves both the problem and the Evidence-backed recovery method, while repeated manual procedures become automation candidates rather than permanent shell rituals.

### Constraints

- A documented workaround is not permission to modify Forbidden files.
- A Python utility requires its own approved Task before Repository implementation.
- Deterministic Harness Core sequencing defined by ADR-001 remains unchanged.
- This ADR does not authorize Worker Adapter implementation.

## ADR-004 - Post-HC-007 Worker Integration Architecture

### Status
Accepted

### Context
HC-001 through HC-007 are complete and verified as the authoritative deterministic Harness Core. ADR-003 deferred Worker Adapter implementation until Architecture explicitly permitted it. Milestone 1 now requires a staged local Worker integration while preserving deterministic Harness-owned safety, execution, Evidence, and final gating.

### Decision
ADR-003 Worker Adapter deferral is released only for the approved staged Milestone 1 sequence defined below.

- HC-001 through HC-007 remain the authoritative deterministic Harness Core.
- Worker integration must use an agent/backend-independent boundary.
- The default local Worker path remains native Ollama API + Qwen3:8B.
- The initial fast path remains `think:false`.
- Tool permission and execution authority belong to deterministic Harness code.
- Qwen must not directly authorize filesystem or shell operations.
- Milestone 1 does not grant Qwen general shell execution authority.
- Approved verification command execution remains owned by HC-004.
- Worker transport, tool execution, orchestration, retry policy, CLI, and E2E verification remain separate responsibilities.
- Retry must be bounded and implemented above the Worker Adapter rather than inside the transport adapter.

### Milestone 1 Integration Sequence
1. Worker contract / backend-independent boundary.
2. Native Ollama Worker Adapter.
3. Harness-owned Repository read tools.
4. Harness-owned scoped edit tools.
5. Single-Task Runner connecting Worker execution to HC-001 through HC-007.
6. Bounded retry / safe FAIL or BLOCKED handling.
7. Minimal user CLI.
8. End-to-End regression with real small Repository Tasks.

Exact implementation details, retry counts, and model parameters are deferred to their own approved Tasks and objective Evidence.

### Outside Milestone 1
ECC routing, LangGraph orchestration, multi-agent expansion, and automatic Codex escalation remain outside Milestone 1 and are not authorized by this ADR.

### Consequences
- ADR-001 through ADR-003 remain unchanged and Accepted.
- Worker integration may proceed only incrementally through separately approved Tasks in the sequence above.
- Qwen self-reported PASS remains non-authoritative.
- Deterministic Git/Test/Invariant Evidence and Harness final gating remain authoritative.
- This ADR does not itself implement or authorize changes outside an approved Worker integration Task.

## ADR-005 - Repetitive Harness Workflow Automation Priority

### Status
Accepted

### Context
ADR-003 permits repeated or error-prone manual procedures to be promoted to a small Python utility through a separately approved Task. Repository Evidence now shows repeated manual status inspection, Git checks, scope checks, verification execution, and review preparation are sufficiently recurrent to justify automation.

QH-V2-WC-001 is complete. The Human explicitly requested that this deterministic workflow automation be implemented before the Native Ollama Worker Adapter.

### Decision
Insert a deterministic Harness workflow automation phase immediately after the completed Worker Contract and before Native Ollama Worker Adapter implementation.

- HC-001 through HC-007 remain the authoritative deterministic Harness engine and must be reused rather than reimplemented.
- QH-V2-WC-001 remains complete and its Worker contract is unchanged.
- Automation V1 is limited to read/check-oriented `status`, `preflight`, `verify`, and `review` operations.
- The workflow utility may orchestrate existing Harness Core functions but must not create a second safety, scope, verification, Evidence, or final-gate engine.
- Human approval remains required for Architecture decisions, Task approval, semantic review, Task completion approval, and commit decisions.
- Automation V1 must not auto-commit, auto-complete Tasks, modify Architecture, invoke a Worker backend, execute Qwen tools, or implement retry orchestration.
- Native Ollama Worker Adapter remains NOT STARTED until this automation phase is completed or explicitly superseded by a later Accepted decision.

### Revised Milestone 1 Sequence
1. Worker contract / backend-independent boundary - completed by QH-V2-WC-001.
2. Deterministic Harness repetitive workflow automation - `status`, `preflight`, `verify`, `review`.
3. Native Ollama Worker Adapter.
4. Harness-owned Repository read tools.
5. Harness-owned scoped edit tools.
6. Single-Task Runner connecting Worker execution to HC-001 through HC-007.
7. Bounded retry / safe FAIL or BLOCKED handling.
8. Minimal Worker-facing CLI integration.
9. End-to-End regression with real small Repository Tasks.

### Automation V1 Boundary
The implementation Task may introduce a small Repository utility such as `tools/qh.py`.
Its purpose is to reduce repeated manual CMD workflows while reusing existing Harness Core functions.
Exact CLI arguments, output contracts, and internal implementation details are deferred to the separately approved implementation Task.

### Consequences
- ADR-001 through ADR-004 remain unchanged and Accepted.
- Deterministic safety ownership remains unchanged.
- Repetitive operational checks can be consolidated before Worker backend integration.
- Human Gates are preserved.
- This ADR authorizes the automation phase but does not itself authorize implementation outside a separately approved Task.

## ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints

### Status
Accepted

### Context
Milestone 1 integration has produced concrete Evidence of repetitive workflow errors, scope-review gaps, and usability friction. Lifecycle automation and Task-range scope review have already been promoted and implemented through approved Tasks, while additional safety and usability candidates remain. The existing Milestone 1 sequence has no explicit checkpoint for deciding which remaining candidates must be addressed before Single-Task Runner integration and which can safely wait until after E2E Regression.

### Decision
Add two explicit planning checkpoints without changing deterministic Harness authority or automatically authorizing any improvement implementation.

1. A Pre-Runner Safety/UX Review must occur after Harness-owned Scoped Edit Tools and before Single-Task Runner implementation.
2. That review must classify known candidates as required before Runner, safe to defer until after E2E, or deferred pending more Evidence.
3. After Milestone 1 E2E Regression, perform a Post-Milestone 1 Hardening & UX Improvement review.
4. Every resulting implementation still requires its own approved Task and Human Gate.

Known candidates include:

- automatic Task baseline recording and reuse by review
- unification of Harness Core and Repository Edit Tool scope evaluation
- reduction of long Windows CMD and inline Python command workflows
- deterministic qh doctor environment/state troubleshooting
- clearer qh status current-state, progress, next-gate, and historical-handoff presentation
- Human-approved Task scaffold generation
- Worker smoke-test standardization after sufficient repeated Evidence

### Sequence Effect
The remaining Milestone 1 execution order becomes:

Harness-owned Scoped Edit Tools -> Pre-Runner Safety/UX Review -> Single-Task Runner -> Bounded Retry/Safe Stop -> Minimal Worker-facing CLI -> E2E Regression.

Post-Milestone 1 Hardening & UX Improvement follows successful E2E Regression and is not itself part of Milestone 1 completion.

### Boundaries
- ADR-004 and ADR-005 remain Accepted and authoritative.
- This decision does not implement any improvement candidate.
- It does not authorize Runner, retry, CLI, E2E, Worker, Repository tool, or Architecture implementation changes by itself.
- Automatic commit, automatic Task completion, automatic next-Task start, automatic Architecture modification, and RED/GREEN semantic judgment remain deferred.
- Human approval remains authoritative.

### Consequences
- Single-Task Runner must not begin until the Pre-Runner Safety/UX Review checkpoint is completed or explicitly superseded by a later Accepted decision.
- Improvement candidates are preserved without forcing premature implementation.
- UX and troubleshooting work has an explicit post-E2E review point instead of being lost in historical handoff notes.

## ADR-007 - Pre-Runner Verification Performance Optimization

### Status
Accepted

### Context
Recent QH-V2-AUTO-005 Evidence shows a full Verification run requires approximately 81 seconds for tests.test_qh and 58 seconds for tests.test_harness_core, while repository-tool tests are negligible. The current manual completion workflow has also invoked verify, review, and close separately even though review executes the full Verification contract and close itself invokes review before lifecycle mutation. This can repeat the same authoritative Verification up to three times for an unchanged Repository state.

### Decision
Permit a targeted Verification performance phase before Single-Task Runner. Optimize redundant execution before introducing concurrency.

1. The standard final lifecycle path should rely on qh close as the authoritative final operation because close invokes review, the full Task Verification contract, Scope Evidence, and Final Gate before lifecycle mutation.
2. Standalone qh verify and qh review remain available for diagnostic or explicitly requested intermediate checks, but they are not mandatory predecessors to close when the Human explicitly invokes close.
3. Development loops should prefer focused tests relevant to the current change; the final close path still executes the complete authoritative Task Verification contract.
4. Parallel Verification is secondary. It may be considered only for commands proven independent and must not parallelize Git state checks, Evidence assembly, or Final Gate evaluation.
5. Profiling tests.test_qh subprocess and temporary-Git-repository cost is authorized as a later performance Task if runtime remains material after duplicate execution is removed.

### Safety Boundaries
- HC-004 remains the authoritative Verification command runner.
- qh close must continue to fail closed when review, Verification, Scope Evidence, or Final Gate fails.
- No stale Verification Evidence may be reused by this decision.
- No automatic PASS, commit, Task completion without an explicit Human close command, next-Task start, or Architecture mutation is authorized.
- Verification caching or persisted receipts require a separate approved design because stale-Evidence prevention is non-trivial.

### Consequences
- The first performance improvement is workflow deduplication, not threading.
- The expected normal final path performs one Full Verification instead of manually repeating the same Full Verification through verify, review, and close.
- Focused development tests remain non-authoritative; final close retains the full Verification contract.
- Parallel test execution and Verification Evidence reuse remain separate follow-up candidates requiring their own Evidence and approved Tasks.

## ADR-008 - Backend-Neutral Tool Interaction Contract

### Status
Accepted

### Context
Milestone 1 requires a Single-Task Runner connecting local Worker execution to the deterministic Harness Core.

The existing backend-independent Worker contract from QH-V2-WC-001 is intentionally minimal:

- WorkerRequest.task_text
- WorkerResponse.transport_ok
- WorkerResponse.output_text
- WorkerResponse.error

The current native Ollama Adapter returns only message.content.

Repository Evidence also shows that Qwen3:8B can produce structured native Ollama tool calls and that a Python-controlled native Ollama tool-call/result continuation loop succeeded against a real Repository file.

However, no backend-neutral contract currently exists for carrying tool requests and tool results across the Worker boundary.

Coupling the Runner directly to Ollama-native tool_calls would violate FR-011 Worker/backend independence. Allowing the LLM or Adapter to authorize Repository operations would violate FR-012 Harness-owned tool boundaries and ADR-004.

### Decision
Introduce a separate backend-neutral tool-interaction contract for tool-enabled Worker execution while preserving the existing WorkerRequest and WorkerResponse contract unchanged.

The logical backend-neutral records are:

- ToolSpec
  - name: str
  - description: str
  - input_schema: mapping describing backend-neutral tool arguments

- ToolRequest
  - call_id: str
  - name: str
  - arguments: mapping of requested arguments

- ToolResult
  - call_id: str
  - ok: bool
  - output: str
  - error: str or None

- WorkerStep
  - transport_ok: bool
  - output_text: str
  - tool_requests: ordered collection of ToolRequest
  - error: str or None

These records are logical architecture contracts. Exact Python class names, modules, and callable signatures belong to the separately approved implementation Task, provided the semantics above are preserved.

The existing WorkerRequest and WorkerResponse dataclasses remain unchanged and continue to support the existing transport-only Worker path.

### Ownership
The Single-Task Runner owns the multi-turn tool-call/result control loop.

The Worker Adapter owns only:

- backend-specific request translation;
- backend-specific response translation;
- backend conversation/session state required to continue a tool-enabled interaction.

The Adapter must translate native backend tool calls into backend-neutral ToolRequest values before they reach the Runner.

The Runner must never depend on Ollama-native tool_calls JSON or other Ollama-specific message structure.

The Runner decides whether a ToolRequest is valid and authorized before any tool execution occurs.

### Initial Milestone 1 Tool Exposure
The initial tool-enabled Worker surface is limited to Harness-owned Repository tools:

1. read_repo_text
   - Worker-supplied argument: Repository-relative path.
   - Deterministic Repository root and path safety remain Harness-owned.

2. write_repo_text
   - Worker-supplied arguments: Repository-relative path and content.
   - The Worker does not supply allowed_changes or forbidden_changes.
   - The Runner obtains the current Task scope and injects it into the deterministic Repository edit tool.
   - Final authorization semantics remain ChangeScope + is_path_allowed.

No shell, Git, verification, Evidence, final-gate, Architecture, Task lifecycle, or commit operation is exposed as a Worker tool in this phase.

### Runner Step Rule
For the initial Single-Task Runner:

- one Worker step may contain zero or one ToolRequest;
- zero ToolRequests means the Worker interaction may terminate and proceed to deterministic Harness evaluation;
- one ToolRequest may be validated and, if authorized, executed by deterministic Harness code;
- more than one ToolRequest in a single Worker step is rejected fail-closed without executing any of those requests.

A successful Worker interaction or terminal output does not mean Repository Task PASS.

### Failure Policy
Malformed, unknown, unsupported, or unauthorized ToolRequest values are not silently repaired.

They cause the current Runner execution to stop fail-closed before tool execution.

Examples include:

- missing or invalid call_id;
- unknown tool name;
- invalid argument shape;
- prohibited operation;
- write request outside the current Task scope.

An execution failure from an otherwise well-formed and authorized tool request, such as a safe Repository read of a missing file, may be represented as ToolResult with ok false and returned to the Worker for continuation.

This distinction does not authorize retry policy.

### Loop Bound
A tool-enabled Worker interaction must have a finite deterministic step budget so the Worker cannot loop indefinitely.

The exact step count is deferred to the Single-Task Runner implementation Task and must be justified by focused tests or objective Evidence.

This step budget is an execution bound, not the bounded retry/fallback policy planned for the later Retry/Safe Stop Task.

### Safety Boundaries
- HC-001 through HC-007 remain authoritative.
- HC-004 remains the sole owner of approved verification command execution.
- Tool permission and execution authority remain deterministic Harness responsibilities.
- Qwen cannot authorize filesystem, shell, Git, verification, Evidence, final-gate, commit, Task lifecycle, or Architecture operations.
- Qwen self-reported PASS remains non-authoritative.
- WorkerRequest and WorkerResponse remain unchanged.
- Ollama-specific tool-call structures remain inside the Adapter.
- Retry remains a separate later responsibility.
- Automatic commit, Task completion, next-Task start, and Architecture mutation remain forbidden.
- Human Gates remain authoritative.

### Consequences
Single-Task Runner implementation may now introduce a backend-neutral tool-enabled Worker interaction path without coupling orchestration to native Ollama message structure.

The next implementation Task must preserve this contract and may not broaden Worker tool authority without another approved decision.

Bounded retry/safe-stop behavior remains the next separate Milestone 1 stage after the Single-Task Runner.
