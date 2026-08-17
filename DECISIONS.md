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
