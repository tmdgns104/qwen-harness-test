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

## ADR-009 - Bounded Retry and Safe Stop Policy

### Status
Accepted

### Context
QH-V2-RUN-001 completed the deterministic Single-Task Runner.

Milestone 1 next requires bounded retry / safe FAIL or BLOCKED handling.

The current Runner already provides:

- explicit ACTIVE Task validation;
- deterministic ToolRequest validation;
- Harness-owned Repository read/write execution;
- Task scope enforcement;
- lifecycle-control file protection;
- an eight-WorkerStep execution bound;
- fail-closed behavior for malformed, unknown, unauthorized, or multi-tool requests.

However, retry policy remains intentionally separate from the Runner step loop.

A retry layer must not decide safety by parsing human-readable error strings.

Automatic whole-Runner retry also becomes unsafe after a Repository write attempt because a previous attempt may already have produced side effects.

### Decision

#### Retry Layer
Retry is implemented above the Single-Task Runner.

Retry is not implemented inside:

- Ollama transport;
- OllamaToolSession;
- Repository tools;
- Harness Core Verification;
- the Worker-step loop.

The existing eight-WorkerStep budget remains an execution bound for one Runner attempt.

It is not the retry budget.

#### Attempt Limit
Retry V1 allows at most:

2 total Runner attempts

consisting of:

- one initial attempt;
- at most one automatic retry.

No third automatic attempt is permitted.

The attempt count may be revisited later only with objective Evidence.

#### Structured Failure Classification
Retry decisions must use deterministic structured failure metadata.

Retry policy must not depend on matching or parsing human-readable error text.

The implementation must distinguish at least:

- normal Runner interaction completion;
- transient Worker/session failure;
- deterministic validation or safety failure;
- Worker-step budget exhaustion;
- Repository write side-effect risk.

Exact Python field names and types belong to the separately approved implementation Task.

#### Retryable Failure
Automatic retry is permitted only when all of the following are true:

1. the Runner did not terminate normally;
2. the failure is deterministically classified as transient Worker/session failure;
3. no Repository write operation was attempted during that Runner attempt;
4. the total attempt limit has not been reached.

Initial retryable transient candidates are limited to:

- Worker session creation/call failure;
- Worker transport failure;
- Worker continuation transport/session failure.

Qwen does not classify its own failure as retryable.

#### Deterministic FAIL
The following conditions stop as deterministic FAIL and are not automatically retried:

- invalid or mismatched Task selection;
- non-ACTIVE Current Task;
- malformed ToolRequest;
- invalid call_id;
- unsupported or unknown tool;
- invalid argument shape;
- multiple ToolRequests in one WorkerStep;
- absolute path;
- path escape;
- write outside Task scope;
- lifecycle-control write attempt;
- Worker-step budget exhaustion;
- other deterministic authorization or safety-policy violations.

#### Operational BLOCKED
BLOCKED is used when execution cannot safely continue because of an operational or uncertain condition rather than a deterministic authorization violation.

Initial BLOCKED cases include:

- retryable transient Worker/session failure after the total attempt limit is exhausted;
- transient Worker/session failure after a Repository write attempt, where retry is prohibited because side effects may already exist;
- another explicitly classified transient condition for which policy does not permit another attempt.

BLOCKED does not mean the Repository Task itself is incorrect.

#### Repository Tool Errors
A well-formed and authorized Repository tool operation that becomes:

ToolResult(ok=False)

and continues within the same Worker session is not automatically a top-level retry event.

For example, a safe read of a missing file may be returned to the Worker as ToolResult(ok=False) so the existing Runner interaction can continue within its eight-step bound.

This is tool-result continuation, not Retry.

#### Repository Write Side-Effect Boundary
If a Repository write operation is attempted during a Runner attempt, automatic whole-Runner retry is disabled for that attempt.

This remains true even if:

- write_repo_text reports failure;
- the following Worker continuation fails;
- transport fails after the write;
- the system cannot prove whether a partial side effect occurred.

A write attempt means deterministic Runner code reached the Repository write execution boundary after structural and authorization checks.

A rejected write that never reaches Repository write execution does not count as a write attempt, but the deterministic rejection itself remains non-retryable.

#### Read-Only Attempts
Successful Repository reads do not create mutation side effects.

Therefore a transient Worker/session failure after only read operations may remain retryable, subject to the total attempt limit.

#### Normal Interaction Completion
A terminal zero-tool WorkerStep within Runner rules is normal Runner interaction completion.

It is neither FAIL nor BLOCKED.

It is also not authoritative Repository Task PASS.

Repository PASS still requires existing Verification, Evidence, and Final Gate authority.

#### Safe Stop Outcome
When Retry is not permitted or the attempt limit is exhausted, the orchestration layer returns a deterministic safe-stop outcome.

The outcome must preserve:

- normal / FAIL / BLOCKED classification;
- structured failure classification when applicable;
- total attempts consumed;
- readable error information;
- whether Repository write side-effect risk occurred.

Safe stop does not automatically:

- complete a Task;
- run Verification;
- create authoritative Evidence;
- pass Final Gate;
- commit;
- modify Architecture;
- start another Task.

#### Retry V1 Model Policy
Retry V1 does not automatically:

- switch model;
- change model parameters;
- enable think:true;
- escalate to Codex;
- invoke another agent.

The approved default Worker path remains native Ollama + Qwen3:8B.

A higher-reasoning slow path remains a possible later optimization requiring separate Evidence and approval.

### Accuracy and Performance
Correctness and side-effect safety take priority over retry success rate.

The normal successful path performs only one Runner attempt.

Retry cost is incurred only after an explicitly classified retryable transient failure.

Verification suites are not repeated inside the Retry loop.

Final Repository completion remains governed by existing qh close, Verification, Evidence, and Final Gate authority.

### Safety Boundaries
- Retry remains deterministic Harness policy.
- Qwen cannot request or expand the retry budget.
- Qwen cannot classify its own failure as retryable.
- Qwen cannot authorize retry after Repository write side-effect risk.
- Qwen cannot override FAIL or BLOCKED.
- Qwen cannot mark a Task complete.
- ADR-008 Worker/tool authority boundaries remain unchanged.
- Human Gates remain authoritative.

### Consequences
The next Retry implementation Task may:

1. add structured Runner failure and write-side-effect metadata with minimal contract change;
2. preserve existing successful Single-Task Runner behavior;
3. add a retry orchestration layer above run_single_task;
4. permit at most one automatic retry;
5. retry only transient Worker/session failures with no Repository write attempt;
6. stop immediately for deterministic FAIL;
7. return BLOCKED when transient execution cannot safely continue;
8. remain testable without live Ollama.

Retry implementation must not broaden Worker tool authority or introduce automatic model/backend escalation.

## ADR-010 - Post-Milestone 1 Hardening Priority

### Status

Accepted

### Context

Milestone 1 completed a real End-to-End regression through:

Human -> qh run -> bounded Retry -> Single-Task Runner -> native Ollama ->
Qwen3:8B -> Harness-owned Repository tools -> Git/Test Evidence -> Final Gate.

ADR-006 requires a Post-Milestone 1 Hardening & UX Improvement review before
further capability expansion.

The review examined eight accumulated candidates using Repository Evidence.

### Decision

The review establishes the following priority order.

1. Verification Contract Fail-Closed Hardening
   - Classification: REQUIRED-BEFORE-NEXT-MILESTONE.
   - A real QH-V2-CLI-001 incident demonstrated that an intended multi-command
     Verification contract could be parsed as one command while qh close still
     reported Final Gate PASS.
   - Verification completeness must fail closed before Worker capability expands.

2. Duplicate qh start / Lifecycle Guard
   - Classification: REQUIRED-BEFORE-NEXT-MILESTONE.
   - Repeated start of the current ACTIVE Task can corrupt Previous Task lifecycle
     history.
   - Same-active-Task start behavior must become deterministic and protected.

3. Human-Approved Task Scaffold Generation
   - Classification: NEXT-HARDENING.
   - Intended to reduce repeated Task-format and Verification-syntax mistakes.
   - It must not auto-approve Task scope or Architecture.

4. qh doctor
   - Classification: NEXT-HARDENING.
   - Read-only deterministic environment and Repository-state diagnostics.

5. Windows CMD Workflow Simplification
   - Classification: NEXT-HARDENING.
   - Repeated command quoting and long inline-Python failures justify a safer
     Repository-native workflow.

6. Worker Smoke / E2E Standardization
   - Classification: NEXT-HARDENING.
   - Milestone 1 now provides sufficient real Worker and E2E Evidence to justify
     reusable regression standardization.

7. qh status UX
   - Classification: SAFE-TO-DEFER.

8. STATUS Handoff / Historical State Cleanup
   - Classification: SAFE-TO-DEFER.

### Required Sequence

Before the next capability-expansion milestone:

1. implement Verification Contract Fail-Closed Hardening through a separate Task;
2. implement Duplicate qh start / Lifecycle Guard through a separate Task.

After those required fixes, continue the remaining hardening candidates according
to the priority above unless new objective Evidence justifies reprioritization.

### Boundaries

- Milestone 1 Architecture remains Accepted and unchanged.
- Worker tool authority does not expand.
- Retry policy does not change.
- Default native Ollama + Qwen3:8B model policy does not change.
- Verification authority remains deterministic Harness-owned.
- No automatic commit, Task completion, next-Task start, or Architecture mutation
  is authorized.
- Every implementation requires its own approved Task and Human Gate.

### Consequences

The next selected implementation stage is:

Verification Contract Fail-Closed Hardening.

Capability expansion remains blocked until the two REQUIRED-BEFORE-NEXT-MILESTONE
items are complete and verified.

## ADR-011 - Evidence-Driven Global Harness Evolution Strategy

### Status

Accepted

Acceptance approves the long-term strategic direction only. It does not authorize
Globalization, cross-Repository execution, Evidence logging, self-modification,
Milestone 3 implementation, lifecycle automation, authority expansion, or any
implementation Task.

`GLOBALIZATION = NOT AUTHORIZED`

`M3 = FUTURE / NOT AUTHORIZED`

### Context

Milestone 1 proved that a local Qwen Worker can complete a small Repository Task
through Harness-owned scope, tools, Git/Test Evidence, Verification, and Final Gate.
The post-Milestone 1 queue now prioritizes lifecycle, Evidence, path, test-integrity,
and operational hardening before broader capability use.

The long-term product direction is to make a sufficiently stabilized Qwen Harness
available to Codex as an optional external executor for small, bounded, verifiable
Repository Tasks. Difficult work and Architecture or Trust Boundary decisions remain
with Codex or a Human Gate.

Without an explicit strategy, the phrase "self-improvement" could be misread as
permission for a running Harness to edit or promote its own code. It could also blur
the boundary between the Stable Harness used by real projects and a Candidate Harness
being developed or evaluated. The Repository therefore records the intended Evidence,
evaluation, isolation, and promotion sequence before any implementation is authorized.

### Decision

Adopt the following long-term target structure:

```text
Human
  -> Codex Supervisor / Router
       -> small, bounded, verifiable Task -> Qwen Harness Stable -> Qwen Local Worker
       -> difficult Task -> Codex
       -> Architecture / Trust Boundary decision -> Human Gate
```

The Codex Supervisor / Router is an optional external role. Harness Core and the Qwen
Worker must remain usable without Codex, consistent with FR-001 and FR-009. The exact
global installation, discovery, configuration, invocation, and version-selection
mechanisms are deferred to separately approved work.

Initial future routing policy should treat a Task as a Qwen Harness candidate only
when it is small and clear, has a limited change scope, has explicit Verification,
and requires no Architecture change. Architecture work, large refactors, ambiguous
requirements, complex debugging, or broad authority needs remain Codex or Human work.
This routing direction does not itself authorize automatic routing or execution.

Codex use of Qwen Harness must not expand Qwen Worker authority. Qwen continues to:

- receive only one explicitly assigned current Task;
- have no general shell authority;
- have no Git authority;
- have no Architecture authority;
- have no Final PASS authority.

Deterministic Harness code continues to own scope enforcement, Repository tool
authorization, Git/Test Evidence, Verification execution, and Final Gate.

### Globalization Gate

Before Codex may use a Global Qwen Harness in another Repository, objective Evidence
must show at least the following Tasks are COMPLETE - VERIFIED:

- QH-V2-HARD-003;
- QH-V2-HARD-004;
- QH-V2-HARD-005;
- QH-V2-HARD-006;
- QH-V2-HARD-007;
- QH-V2-OPS-002 (`qh doctor`);
- QH-V2-OPS-004 (Worker Smoke / E2E Standardization).

These are necessary Evidence prerequisites, not sufficient authorization. Their
completion only makes a separate Human Globalization Gate eligible for review. The
Human decides the exact approval time, covered version, repositories, operations,
expiry, revocation, audit requirements, and rollback limits after reviewing the Task
Evidence. No current Task or this ADR grants that approval.

QH-V2-ARCH-008 only prepares a proposal for the separate Human One-Time Autonomous
Queue Gate. That Gate may accept, reject, or defer a narrow policy for an exact queue
in this Repository. Neither ARCH-008 nor Gate G1 authorizes cross-Repository or global
use; Globalization requires its own later Human Gate.

If Globalization is later approved, its first phase is `GLOBAL OPTIONAL EXECUTOR`.
Codex may consider the approved Stable Harness for eligible Tasks, but the Harness is
not mandatory and is not the default executor for every Task.

### Cross-Repository Evidence Policy

After a separate Globalization approval, future work may design privacy-conscious
Evidence collection across multiple Repositories. Candidate fields include:

- non-sensitive Repository and Task type;
- language;
- expected and actual changed files;
- Worker steps and Runner attempts;
- NORMAL, FAIL, or BLOCKED outcome;
- Verification and Final Gate results;
- duration and failure classification;
- write side-effect risk;
- Codex fallback use.

The exact schema, storage, retention, repository identification, redaction, and access
policy are not defined or implemented here. They require a separate approved Task.
Credentials, secrets, or unnecessary private Repository content must not be collected.

### Evidence-Driven Improvement Policy

"Automatic evolution" means using objective execution Evidence to propose and evaluate
improvements. It does not mean that the Harness may modify or promote its own code
during normal use.

Every improvement follows this sequence:

```text
Evidence
  -> Improvement Candidate
  -> Task Contract
  -> Candidate Implementation
  -> Regression / Benchmark
  -> Promotion Gate
  -> Stable Version
```

A future Codex Improvement Analyzer is only a conceptual role for finding repeated
failures, bottlenecks, and successful patterns. Its proposal or self-evaluation is not
promotion Evidence and does not authorize a Task, implementation, or release.

The Harness used by real projects is logically `Stable`. Development and evaluation
occur against a logically separate `Candidate`. The physical isolation, packaging,
versioning, and rollback mechanisms require later design. A Candidate must not replace,
modify, or impair Stable before a Promotion Gate. Safety regression or scope violation
makes a Candidate ineligible for automatic promotion.

### Improvement Levels

- **Level A - No Architecture or Trust Boundary change.** Examples include error
  messages, status UX, diagnostics, documentation, regression tests, and verified
  performance optimizations. These may become candidates for a future pre-approved
  improvement policy, but no such policy is authorized here.
- **Level B - Policy change inside the existing Trust Boundary.** Examples include
  retry tuning, Worker step-budget tuning, Router thresholds, context strategy, and
  prompt or model-routing policy. Promotion requires objective Stable-versus-Candidate
  regression and benchmark Evidence.
- **Level C - Architecture or Trust Boundary change.** Examples include shell, Git,
  network, or new write authority; multi-agent or LangGraph orchestration; Final Gate
  authority changes; and automatic escalation Architecture. The required path is
  `Proposal -> STOP -> Human + ChatGPT Architecture Gate`.

For Level C, `Human + ChatGPT Architecture Gate` means mandatory ChatGPT technical
Architecture review followed by Human final approval. ChatGPT analysis alone never
accepts an Architecture or authority change.

A Level C Candidate can never be promoted automatically. After an approved
implementation and objective evaluation, Stable promotion still requires an explicit
Human Promotion Gate informed by ChatGPT Architecture review.

### Regression Corpus and Promotion

Representative successful and failed cross-Repository Tasks may later become a
reproducible Harness Regression Corpus. Stable and Candidate must be evaluated against
the same applicable corpus. Evaluation must compare at least:

- safety regression;
- scope violation;
- Verification integrity;
- Final Gate integrity;
- PASS, FAIL, and BLOCKED behavior;
- Task success;
- runtime and performance.

"Looks better" and Codex self-assessment are not promotion Evidence. Promotion requires
the applicable objective regression and benchmark Evidence plus the required Promotion
Gate. Safety regression or scope violation cannot be waived by a performance gain.

### Future Milestone 3

Record `Milestone 3 - Evidence-Driven Harness Evolution` as a future roadmap candidate.
Illustrative work areas include:

- Global Usage Evidence Schema;
- Cross-Repository Execution Logging;
- Failure Pattern Classification;
- Improvement Candidate Generation;
- Harness Regression Corpus;
- Stable vs Candidate Benchmark;
- Candidate Promotion Gate;
- Evidence-Based Task Router;
- Autonomous Improvement Cycle E2E.

These labels are not Task IDs, approved contracts, or an implementation sequence.
No Milestone 3 implementation Task may be generated or started automatically before
the Milestone 2 Human Architecture Gate or another explicit Human approval.

### Compatibility and Boundaries

- The current deterministic HARD/OPS Queue and its order remain unchanged.
- FR-004 remains authoritative: a Qwen Worker executes only its explicitly assigned
  current Task and never selects or starts the next Task.
- ADR-005 through ADR-010 remain authoritative. This ADR does not authorize automatic
  commit, Task completion, `qh close`, lifecycle commit, push, next-Task start,
  automatic Codex escalation, or Architecture mutation.
- QH-V2-ARCH-008 remains a proposal-only future Task and is not accepted or activated
  by this strategic direction.
- Every implementation or policy change still requires the applicable approved Task,
  objective Evidence, and Human Gate.
- Any future conflict with a Functional Requirement or Accepted ADR requires an
  explicit Human-approved clarification or superseding decision before implementation.
- Cross-Repository Evidence collection, Candidate execution, promotion automation,
  global installation, and Milestone 3 are not implemented or authorized.

### Consequences

- Future Globalization and improvement proposals have a common Evidence-first target.
- Qwen authority stays narrow while Codex may later gain an optional delegation path
  through a separately approved external integration.
- Stable users are protected from unpromoted Candidate behavior by the required
  logical separation and Promotion Gate.
- The current Queue continues from QH-V2-HARD-003 without reordering or skipping.
- Exact Evidence schemas, global integration, Stable/Candidate mechanics, routing,
  evaluation infrastructure, and Milestone 3 Tasks remain deferred.


## ADR-012 - HUMAN ONE-TIME AUTONOMOUS QUEUE GATE G1

### Status

Accepted

### Context

QH-V2-ARCH-008 completed a proposal-only review for reducing repeated Human relay
without transferring Harness or Qwen safety authority to an LLM. On 2026-08-22 the
Human explicitly accepted the recommended narrow policy for one exact Repository
queue and approved fast-forward-only push to `origin/main`.

The accepted decision must not be confused with immediate execution authority.
QH-V2-GATE-001 must first materialize the policy, pre-approve the exact covered Task
contracts, implement deterministic manifest validation, seal the exact Gate Change
Set, and pass authoritative `qh close`.

### Decision

Accept the Human One-Time Autonomous Queue Gate only for this exact covered order:

1. QH-V2-HARD-006
2. QH-V2-HARD-007
3. QH-V2-OPS-001
4. QH-V2-OPS-002
5. QH-V2-OPS-003
6. QH-V2-OPS-004
7. QH-V2-OPS-005
8. QH-V2-OPS-006
9. QH-V2-M2-SPEC-001
10. HUMAN ARCHITECTURE GATE - mandatory STOP

After QH-V2-GATE-001 is COMPLETE - VERIFIED and an exact sealed manifest passes
deterministic `gate-check`, an optional external Codex CLI Supervisor may, without a
new Human prompt for each covered lifecycle step:

- start only the exact next already-approved covered Task;
- create Task implementation commits within that Task's existing scope;
- invoke authoritative `qh close <exact implementation HEAD>`;
- create the separate lifecycle commit after Final Gate PASS;
- revalidate and proceed only to the exact manifest successor;
- push only `HEAD:main` to `origin`, using fast-forward-only behavior.

This is a narrow supersession of the repeated Human lifecycle prompts described by
ADR-005, ADR-006, ADR-007, and ADR-010 for the one exact valid manifest. It does not
supersede deterministic qh/Harness authority.

FR-004 remains authoritative for the Qwen Worker. The external Supervisor is not the
Worker and must not expand Worker tools or authority. ADR-008 remains unchanged:
Qwen has no shell, Git, lifecycle, Verification, Evidence, commit, push, Architecture,
or Final PASS authority.

`qh close` remains the sole authoritative final full Verification / Evidence / Final
Gate path. Focused development tests remain non-authoritative.

### Manifest and Failure Boundary

The approval manifest must bind at least:

- the Gate Change Set commit;
- exact BACKLOG, REQUIREMENTS, and DECISIONS Git blob identities;
- the exact ordered covered Task IDs;
- each covered Task's exact pre-start whole-file Git blob;
- deterministic SHA-256 of its Immutable Contract Sections;
- local branch `master`;
- remote `origin`, remote branch `main`, and push refspec `HEAD:main`;
- fast-forward-only policy;
- delegated and forbidden operations;
- Gate Evidence, revocation, validity, and terminal Human Gate policy.

Every Supervisor mutation must revalidate the manifest and current Repository/Git
state first. Manifest tamper, queue mismatch, covered-contract mutation, wrong branch
or remote, invalid lifecycle, revocation, scope violation, dirty state where clean is
required, or policy mismatch causes deterministic STOP.

A pending or ACTIVE covered Task must retain its exact pre-start whole-file identity.
After normal close, only the approved Status lifecycle value may differ; Immutable
Contract Sections remain exact.

### Push and Recovery Boundary

Push authority is exactly `origin` / `main` / `HEAD:main`, fast-forward only.

Force push, rebase, reset/history rewrite, destructive recovery, skipping a failed
Task, or silently repairing a manifest mismatch are never authorized.

If the remote diverges, validation or Final Gate fails, or safe fast-forward push
cannot be proven, execution stops for Human review.

### Expiry and Terminal Gate

Authorization ends at the first of:

- explicit Human revocation;
- manifest or authority-source mismatch;
- covered queue / contract invalidation;
- policy invalidation;
- successful completion of QH-V2-M2-SPEC-001 at the HUMAN ARCHITECTURE GATE.

No Task may be generated, approved, or started automatically after that terminal Gate.

### Compatibility and Boundaries

- ADR-001 through ADR-011 remain Accepted except for the narrow repeated-Human-prompt
  supersession stated above.
- Qwen/Worker authority, Harness Core scope/Verification/Evidence/Final Gate semantics,
  Retry policy, and native Ollama model policy are unchanged.
- `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
- `M3 = FUTURE / NOT AUTHORIZED` remains unchanged.
- Codex remains optional. Harness Core and the Qwen Worker remain usable without Codex.
- The accepted G1 queue is Repository-local and grants no cross-Repository authority.

### Consequences

QH-V2-GATE-001 may implement the deterministic qhops manifest guard and seal the
accepted queue. Covered autonomous execution is eligible only after that Task is
COMPLETE - VERIFIED and the exact manifest passes `gate-check`.

Until then, the Human-approved policy exists but autonomous queue execution remains
disabled.

## ADR-013 - Human Revocation of Remaining G1 Queue and PERF-005 Insertion

### Status

Accepted

### Context

QH-V2-HARD-006 and QH-V2-HARD-007 both completed successfully under the sealed G1
queue. After HARD-007, measured regression performance remained material on the current
Windows host:

- selected 259-test regression: 560.059 seconds;
- `tests.test_qh`: 48 tests in 470.073 seconds;
- `tests.test_harness_core`: 119 tests in 207.330 seconds.

Profiling shows the slowest tests are concentrated in Git-heavy qh review/close and
Harness Core Git baseline/evidence fixtures. The Human explicitly chose to perform one
additional Evidence-driven performance optimization round before OPS-001 rather than
continue the sealed queue unchanged.

ADR-012 already defines explicit Human revocation, authority-source mismatch, and queue
invalidation as terminal conditions for G1 authorization.

### Decision

1. Revoke the remaining G1 autonomous queue authorization immediately after the
   successful completion of QH-V2-HARD-007.
2. Preserve the existing sealed G1 manifest as historical Evidence; do not rewrite,
   reseal, or reinterpret it as covering a different queue.
3. The DECISIONS/BACKLOG change that records this decision intentionally invalidates
   the manifest's sealed authority-source identities, so any later `gate-check` against
   G1 must fail closed rather than silently continue.
4. Insert QH-V2-PERF-005 before QH-V2-OPS-001 as a Human-approved Level A performance
   optimization round limited to test infrastructure and objective benchmark Evidence.
5. After PERF-005, resume the existing order:
   QH-V2-OPS-001 -> QH-V2-OPS-002 -> QH-V2-OPS-003 -> QH-V2-OPS-004 ->
   QH-V2-OPS-005 -> QH-V2-OPS-006 -> QH-V2-M2-SPEC-001 -> HUMAN ARCHITECTURE GATE.
6. Remaining Tasks use the ordinary Human-controlled lifecycle. No new autonomous
   manifest is authorized by this decision.
7. If PERF-005 Evidence shows the remaining dominant bottleneck requires production
   Harness/qh changes, stop at the test-only boundary and require a separate approved
   performance Task.

### Safety Boundaries

- `qh close` remains the authoritative full Verification / Evidence / Final Gate path.
- No test may be deleted, skipped, weakened, or removed from authoritative Verification
  for speed.
- Stale or cached PASS Evidence remains forbidden.
- Verification concurrency remains rejected unless a separate future Task provides new
  Evidence and approval.
- Qwen Worker authority, Repository tools, Runner, Retry, lifecycle semantics, and
  Final Gate semantics remain unchanged.
- `GLOBALIZATION = NOT AUTHORIZED` and `M3 = FUTURE / NOT AUTHORIZED` remain unchanged.
- This decision grants no automatic Task creation, start, commit, close, push, or
  Architecture mutation authority.

### Consequences

- G1 is retained only as historical Evidence of the completed HARD-006/HARD-007 portion.
- PERF-005 becomes the next nominated Task after HARD-007.
- The Repository returns to ordinary per-Task Human Gates for PERF-005 and the remaining
  OPS/M2 queue unless another explicit Human decision later authorizes a new exact
  manifest.

## ADR-014 - Cross-Repository Trial Hardening Reprioritization

### Status

Accepted

### Context

GitHub Issue #1 records the first real cross-Repository trial Evidence from
`ai_data_analyst`. The trial exposed two independent operational failures that were
not covered by the in-Repository Milestone 1 Evidence:

1. the documented `python tools\qh.py run ...` entry path can fail with
   `ModuleNotFoundError: No module named 'tools'` unless the operator manually adjusts
   `PYTHONPATH`; and
2. after that workaround, real `qwen3:8b` produced multiple ToolRequests in one
   WorkerStep on two controlled runs, causing the deterministic Runner to fail closed
   with `SAFETY` and zero Repository mutation.

Issue #1 is authoritative new operational Evidence for planning purposes. It is not
implementation authority by itself.

### Decision

1. Treat the import-path failure as a runtime portability defect and address it first
   in QH-V2-HARD-008.
2. Treat the repeated multi-ToolRequest behavior as a Worker interaction robustness
   problem and address it second in QH-V2-WORKER-ROB-001.
3. After those Tasks, resume QH-V2-OPS-003 and the existing remaining OPS/M2 order.
   QH-V2-OPS-003 is deferred, not cancelled.
4. The existing `zero or one ToolRequest per WorkerStep` rule remains authoritative.
   More than one ToolRequest remains deterministic SAFETY failure. An invalid step is
   not silently split, repaired, retried as a continuation, or executed.
5. QH-V2-WORKER-ROB-001 may strengthen Worker instructions/context inside the existing
   Trust Boundary. Because prompt/context policy is ADR-011 Level B, promotion requires
   objective Stable-versus-Candidate Evidence.
6. Any change that converts a multi-tool violation into continuation/retry, changes
   retry classification, expands Worker authority, changes model routing or step
   budget, or changes Final Gate authority requires a separate Human Architecture
   review before implementation.
7. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged. The trial and these hardening
   fixes do not authorize stable cross-Repository use.
8. ADR-011 Globalization prerequisites remain in force, including QH-V2-OPS-004 and a
   later explicit Human Globalization Gate.

### Queue

The Human-controlled candidate order after QH-V2-OPS-002 is:

```text
QH-V2-HARD-008
  -> QH-V2-WORKER-ROB-001
  -> QH-V2-OPS-003
  -> QH-V2-OPS-004
  -> QH-V2-OPS-005
  -> QH-V2-OPS-006
  -> QH-V2-M2-SPEC-001
  -> HUMAN ARCHITECTURE GATE
```

No autonomous manifest covers this reprioritized queue. Ordinary Human-controlled
Task lifecycle rules remain authoritative.

### Consequences

- Runtime/import portability is fixed before changing Worker interaction policy.
- Worker robustness work preserves deterministic multi-tool fail-closed semantics.
- Existing OPS work is preserved and resumes after the two evidence-driven Tasks.
- Formal Globalization remains a separate future Human decision.
- Qwen Worker authority, Repository tool authority, Verification, Evidence, and Final
  Gate ownership remain unchanged.
## ADR-015 - Evidence-Backed Unsuccessful Task Closure and Lifecycle Bootstrap

### Status

Accepted

### Context

QH-V2-WORKER-ROB-001 reached a Human Architecture review after objective Stable-versus-Candidate Evidence showed no promotable Worker protocol improvement.

The representative real `qwen3:8b`, `think:false` probe measured 0/10 exact task success for Stable and 0/10 for the final Candidate. Focused diagnostics showed that ToolResult delivery and semantic reuse can succeed while exact downstream tool-argument fidelity remains unreliable. The Candidate was therefore rejected and its failed implementation history was preserved as Evidence only.

The current lifecycle has a gap: normal progression assumes an ACTIVE Task eventually becomes `COMPLETE - VERIFIED`. That is truthful for successful implementation, but it cannot represent a Task that was executed and evaluated correctly yet intentionally not promoted because its Acceptance Criteria were not met. Leaving such a Task ACTIVE forever blocks the queue, while marking it COMPLETE - VERIFIED would falsely claim success.

The Human explicitly approved an Architecture change to add an Evidence-backed unsuccessful terminal state and a one-time bootstrap transition so the lifecycle implementation Task can be started without falsifying QH-V2-WORKER-ROB-001.

### Decision

1. Add a distinct non-success terminal lifecycle state:

   `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

2. This state means all of the following:
   - the Task was actually attempted or evaluated;
   - objective Evidence explains why promotion or successful completion did not occur;
   - the Task is no longer ACTIVE;
   - the state is not equivalent to PASS, COMPLETE, or COMPLETE - VERIFIED;
   - no failed Candidate becomes production state merely because the Task is closed;
   - later work must not cite this state as successful implementation Evidence.

3. `COMPLETE - VERIFIED` remains the only successful completion state. Existing successful `qh close` Final Gate semantics remain authoritative and unchanged.

4. Durable support for unsuccessful closure must be implemented through the separately approved `QH-V2-LIFECYCLE-001` Task. Exact command names and code structure are deferred to that Task, but the implementation must remain Human-invoked, deterministic, Evidence-backed, and fail closed.

5. A future unsuccessful-close operation must require at minimum:
   - exactly one ACTIVE current Task;
   - explicit Human invocation;
   - a declared Evidence artifact or deterministic Evidence condition supporting the non-success result;
   - no claim of Final Gate PASS or successful implementation;
   - lifecycle mutation limited to the explicitly authorized lifecycle files;
   - clean, reviewable Git state before and after the lifecycle transition;
   - no automatic successor start.

6. After an unsuccessful Task is closed, the next Task is not automatically selected or started. Successor eligibility requires an explicit Human decision under the ordinary lifecycle unless a later Accepted ADR grants a narrower deterministic exception.

7. QH-V2-WORKER-ROB-001 is the first and only one-time bootstrap case authorized by this ADR. Its accepted disposition is:

   `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`

   with Candidate promotion rejected and the failed implementation branch retained as Evidence only.

8. Because durable unsuccessful-close support does not yet exist, one Human-authorized bootstrap transition may update the Repository Source of Truth to close QH-V2-WORKER-ROB-001 unsuccessfully and activate `QH-V2-LIFECYCLE-001`. This bootstrap is not reusable precedent for arbitrary manual lifecycle mutation after LIFECYCLE-001 is implemented.

9. The bootstrap change set must be narrow and explicit. It may update only the Architecture/queue/lifecycle records and the new lifecycle Task contract needed to represent the approved transition. It must not modify Worker, Runner, Retry, Repository-tool, Verification, Evidence, Final Gate, model-routing, or tool-authority implementation.

10. QH-V2-OPS-003 remains deferred. The next implementation priority is `QH-V2-LIFECYCLE-001`. Worker/backend/model/thinking-policy comparison and the longer-term question of whether exact data binding belongs in deterministic Harness code require later separately approved Investigation/Architecture work.

### Safety Boundaries

- Qwen Worker authority does not expand.
- Multi-tool Runner SAFETY behavior remains unchanged.
- Retry policy and the eight-step Worker budget remain unchanged.
- Default model and routing policy remain unchanged.
- `qh close` successful Final Gate authority remains unchanged.
- No automatic repair, normalization, silent Candidate promotion, successor start, commit, push, or Architecture mutation is authorized.
- `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
- `M3 = FUTURE / NOT AUTHORIZED` remains unchanged.

### Consequences

- Failed experiments can terminate truthfully without being mislabeled as successful completion.
- Evidence becomes part of the lifecycle outcome rather than an informal side note.
- QH-V2-WORKER-ROB-001 can leave ACTIVE state without promoting its failed Candidate.
- QH-V2-LIFECYCLE-001 becomes the next Human-approved implementation Task before further Worker investigation or OPS-003.
- Future lifecycle code must support this state deterministically so another manual bootstrap is not needed.

## ADR-016 - Post-Lifecycle Worker Diagnosis Before Operations Resume

### Status

Accepted

### Context

QH-V2-WORKER-ROB-001 closed as `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` under ADR-015 after Stable and Candidate both failed the promotion threshold. QH-V2-LIFECYCLE-001 then completed durable Evidence-backed unsuccessful closure support. During the LIFECYCLE-001 implementation attempt, short native Ollama requests remained responsive while the full Task prompt repeatedly reached the bounded 30-second Worker timeout. The existing QH-V2-OPS-003 contract still requires WORKER-ROB-001 to become `COMPLETE - VERIFIED`, which conflicts with its authoritative non-success terminal state.

The Human reviewed this Evidence and selected a dedicated Worker diagnosis before resuming the Operations queue.

### Decision

1. Preserve QH-V2-WORKER-ROB-001 exactly as `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`; it must never be rewritten as successful completion.
2. After QH-V2-PLAN-001, nominate a separately defined QH-V2-WORKER-DIAG-001 investigation before QH-V2-OPS-003.
3. WORKER-DIAG-001 must diagnose the observed long-prompt and timeout behavior from objective Evidence before proposing Worker policy or implementation changes.
4. QH-V2-WORKER-ROB-002 is conditional. It may be created only after diagnostic Evidence and a Human review justify a specific repair Task. It is not automatically required, created, approved, or started.
5. QH-V2-OPS-003 remains deferred until QH-V2-LIFECYCLE-001 is complete and the Worker diagnostic path reaches a Human-reviewed disposition. If ROB-002 is selected, its terminal outcome and the Human decision to resume Operations must be recorded first.
6. After the Worker diagnostic path, the remaining Operations order stays QH-V2-OPS-003, QH-V2-OPS-004, QH-V2-OPS-005, QH-V2-OPS-006, QH-V2-M2-SPEC-001, then HUMAN ARCHITECTURE GATE.
7. This decision changes sequencing and dependency interpretation only. Worker, Runner, Retry, tool, model, lifecycle, Verification, Final Gate, Git, and Trust Boundary authority remain unchanged.
8. No successor is automatically created or started. Ordinary Human-controlled lifecycle gates remain authoritative.

### Consequences

- Repository dependency truth no longer requires an unsuccessful Task to become successful.
- Worker reliability is investigated before additional usability work resumes.
- A repair Task is Evidence-driven rather than assumed in advance.
- OPS-003 and the remaining OPS/M2 work stay preserved and deferred, not cancelled.
- `GLOBALIZATION = NOT AUTHORIZED` and `M3 = FUTURE / NOT AUTHORIZED` remain unchanged.

## ADR-017 - Exception-Driven Human Supervision

### Status

Accepted

### Context

Repeated Human approval for every mechanical lifecycle step adds relay overhead even when a Task is already approved and deterministic Harness checks remain authoritative. The Human has approved an exception-driven supervision model: normal work inside already-approved boundaries may continue without a fresh approval prompt, while failures, ambiguity, new direction, promotion, Architecture, Requirements, or Trust Boundary decisions still require Human review.

### Decision

Adopt Exception-Driven Human Supervision for Human/ChatGPT/Supervisor workflow governance.

Routine continuation does not require a new Human prompt when the current Task and successor authority are already explicit in Repository Source of Truth, scope and dependencies remain valid, deterministic checks pass, qh close reaches Final Gate PASS, lifecycle mutation is expected, and Git operations are clean and fast-forward-only.

Routine continuation may include scoped implementation, focused tests, Verification, authoritative qh close at the exact implementation HEAD, the separate lifecycle commit, safe fast-forward push to an already-authorized target, and starting an exact already-approved successor.

Human review is still required for deterministic FAIL, BLOCKED, SAFETY failure, repeated unresolved Worker failure or timeout, unexpected Repository mutation, scope violation, Git divergence or ambiguity, new Task creation, queue reprioritization, Candidate production promotion, Architecture or Requirements change, Trust Boundary or authority change, model/reasoning/timeout/Retry/step-budget policy change, or a materially different proposed direction.

FR-004 remains unchanged: Qwen Worker executes only its explicitly assigned current Task and never selects or starts a successor. External workflow continuation does not transfer successor-selection authority to Qwen.

CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED, FAIL, BLOCKED, SAFETY, or ambiguous termination never auto-advances.

Deterministic Harness scope, Evidence, Verification, and Final Gate authority remain unchanged. An LLM recommendation cannot override deterministic FAIL Evidence.

The revoked G1 manifest remains historical Evidence only and is not rewritten, resealed, or reactivated.

This decision changes approval cadence only. It does not itself implement unattended production automation. Such automation requires a separate approved implementation Task.

GLOBALIZATION = NOT AUTHORIZED remains unchanged.

### Consequences

- Human involvement moves from repeated mechanical approval to exception and direction review.
- Normal already-authorized work can proceed with less relay overhead.
- Qwen Worker authority does not expand.
- qh close remains the authoritative Final Gate.
- New Tasks, reprioritization, production Candidate promotion, Architecture changes, and unsafe or ambiguous states still stop for Human review.
- After QH-V2-ARCH-017 completes, the already selected QH-V2-WORKER-ROB-002 experiment path may resume under this approval cadence.
