# QH-V2-HARD-001 - Post-Milestone 1 Hardening & UX Review

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Architecture Basis

- ADR-003 - Verified Problem Resolution and Automation Escalation
- ADR-006 - Pre-Runner Safety/UX and Post-Milestone Hardening Checkpoints
- ADR-007 - Verification Performance Optimization
- ADR-009 - Bounded Retry and Safe Stop Policy
- QH-V2-E2E-001 - COMPLETE - VERIFIED

Milestone 1 E2E has completed successfully.

ADR-006 now requires a Post-Milestone 1 Hardening & UX Improvement review
before further expansion.

## Problem

Milestone 1 proved that the complete real Worker path operates:

Human
-> qh run
-> Retry
-> Runner
-> native Ollama
-> Qwen3:8B
-> Harness-owned Repository tools
-> Git/Test Evidence
-> Final Gate

During Milestone 1, additional operational and safety Evidence accumulated.

These issues must not be fixed ad hoc.

They must first be reviewed, classified, prioritized, and recorded.

## Goal

Perform a Repository-backed hardening review that:

1. inventories known post-Milestone 1 issues;
2. separates safety/correctness problems from UX improvements;
3. records Evidence for each candidate;
4. assigns implementation priority;
5. identifies candidates requiring focused reproduction first;
6. identifies candidates safe to defer;
7. records the resulting priority decision in DECISIONS.md;
8. updates STATUS.md with the selected next implementation stage;
9. performs no production implementation.

## Review Priority Principle

Use the following order when comparing candidates:

1. Verification correctness and trust
2. Safety / destructive-side-effect prevention
3. Deterministic lifecycle correctness
4. Repeated human-error reduction
5. Troubleshooting usefulness
6. usability / command simplicity
7. performance optimization
8. convenience

Do not trade verification correctness for speed or convenience.

## Mandatory Candidate Inventory

### Candidate A - Verification Contract Fail-Closed Hardening

Observed Evidence:

During QH-V2-CLI-001, the Task Verification section contained nine intended
commands under one `Run exactly:` marker.

`parse_verification_commands()` parsed only the first command.

`qh close` therefore executed only:

`python -m unittest tests.test_qh_worker_run`

and still reported:

`Final Gate: PASS`

The lifecycle completion was reverted before committing, the Verification
contract was corrected to use repeated `Then run:` markers, parser count was
verified as 9, and qh close was rerun successfully with all 9 commands.

Review questions:

- Should malformed/unmarked Verification command lines fail closed?
- Should the parser accept multiple consecutive explicit command tokens?
- Should Task scaffolding generate parser-safe syntax automatically?
- Which protection belongs in Harness Core versus Task-generation UX?

This candidate must be treated as a verification-trust issue, not merely UX.

### Candidate B - Duplicate qh start / Lifecycle Guard

Observed Evidence:

During QH-V2-E2E-001 start, an operational state was observed where:

- Current Task became QH-V2-E2E-001 - ACTIVE
- Previous Task also became QH-V2-E2E-001 - ACTIVE

The state was restored.

A subsequent single clean invocation produced the correct state:

- Current Task: QH-V2-E2E-001 - ACTIVE
- Previous Task: QH-V2-CLI-001 - COMPLETE - VERIFIED

Code inspection shows command_start copies the current lifecycle line into
Previous Task and currently has no explicit same-current-Task rejection.

Review questions:

- Should `qh start` reject starting the already-current ACTIVE Task?
- Should duplicate start be idempotent or fail closed?
- Which lifecycle states are valid start sources?

### Candidate C - Human-Approved Task Scaffold Generation

ADR-006 already identifies Task scaffolding as a deferred candidate.

Review must consider whether a deterministic scaffold utility could prevent:

- malformed Verification syntax;
- missing required Task sections;
- inconsistent Status values;
- long manual Task creation scripts.

The utility must not auto-approve Architecture or Task scope.

### Candidate D - qh doctor

ADR-006 already identifies deterministic qh doctor troubleshooting.

Potential checks include:

- Git repository/root validity;
- required SOT files;
- STATUS lifecycle shape;
- active Task existence;
- Verification parseability;
- Ollama endpoint availability;
- default Worker model availability.

Review only. Exact implementation is deferred.

### Candidate E - qh status UX

ADR-006 already identifies clearer current-state presentation.

Potential improvements include:

- current Task;
- lifecycle state;
- baseline;
- next gate;
- changed paths;
- Verification count;
- Worker readiness;
- concise historical handoff separation.

Review only.

### Candidate F - Windows CMD Workflow Simplification

Repeated Evidence exists for:

- quoting failures;
- long inline Python commands;
- accidental prompt/output copy;
- multiline patch difficulty.

The established temporary Python script pattern has reduced these failures.

Review whether this should become a deterministic Repository utility or remain
an operator convention.

### Candidate G - Worker Smoke / E2E Standardization

ADR-006 deferred this pending repeated Evidence.

Milestone 1 now has:

- native Qwen3:8B smoke Evidence;
- native Ollama tool-call continuation Evidence;
- real qh run E2E Evidence.

Review whether this is now sufficient to standardize a reusable Worker smoke
or E2E fixture.

### Candidate H - STATUS Handoff / Historical State Cleanup

STATUS.md accumulated substantial historical handoff material during Milestone 1.

Review whether:

- current operational state should remain concise;
- long history should move to a dedicated document;
- cleanup is useful enough to justify a separate Task.

Do not delete history during this Review.

## Required Classification

Each candidate must receive exactly one classification:

### REQUIRED-BEFORE-NEXT-MILESTONE

A correctness, safety, or deterministic-operation issue that should be fixed
before expanding Worker capability.

### NEXT-HARDENING

Useful hardening that should follow the required fixes.

### SAFE-TO-DEFER

Useful but not necessary before the next development milestone.

### EVIDENCE-PENDING

Insufficient objective Evidence to justify implementation yet.

For every candidate record:

- Evidence
- Risk if ignored
- User/operator impact
- Expected implementation scope
- Classification
- Relative priority
- Rationale

## Required Decision Output

Append a new accepted decision to DECISIONS.md recording:

- completion of the Post-Milestone 1 review;
- priority order;
- which candidates are required before capability expansion;
- which candidates are deferred;
- that each implementation still requires its own Task;
- that Milestone 1 Architecture remains unchanged unless explicitly stated.

The exact ADR number must use the next available ADR sequence.

## STATUS Output

Update STATUS.md to record:

- Milestone 1 E2E complete;
- Post-Milestone 1 Review complete;
- the next selected implementation stage;
- deferred candidates preserved for later review.

Do not start the next implementation Task automatically.

## No Implementation

This Task must not modify production code or tests.

It is review / prioritization / decision recording only.

## Allowed Changes

- `DECISIONS.md`
- `STATUS.md`
- `tasks/QH-V2-HARD-001.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- Repository fixture files
- `PROJECT.md`
- `REQUIREMENTS.md`
- other Task files
- unrelated files

## Acceptance Criteria

1. Milestone 1 E2E completion is acknowledged.
2. All mandatory candidates A-H are reviewed.
3. Every candidate receives exactly one classification.
4. Verification correctness receives explicit priority consideration.
5. Duplicate-start lifecycle behavior receives explicit priority consideration.
6. Task scaffold interaction with Verification syntax is analyzed.
7. Worker smoke standardization is reconsidered using new E2E Evidence.
8. No production implementation occurs.
9. No test implementation occurs.
10. A new ADR records the review decision.
11. STATUS records the selected next implementation stage.
12. Deferred candidates remain explicitly preserved.
13. No Architecture authority is broadened.
14. Every future implementation remains Task-gated.
15. git diff check passes.
16. no forbidden changed path occurs.


## Review Result

### Priority 1 - Candidate A: Verification Contract Fail-Closed Hardening

Classification: REQUIRED-BEFORE-NEXT-MILESTONE

Evidence:
- QH-V2-CLI-001 intended nine Verification commands.
- The existing parser accepted only the first command because only the first command followed an explicit marker.
- qh close therefore reported Final Gate PASS after executing only one intended Verification command.
- The lifecycle change was reverted before completion.
- After the Task contract was corrected to use explicit repeated markers, parser count became nine and all nine commands passed.

Risk if ignored:
- A Task may appear fully verified while only part of its intended Verification contract actually ran.
- This directly weakens the trust boundary between Worker output and deterministic Repository completion.

User/operator impact:
- Human-readable Task syntax can silently produce weaker Verification than intended.

Expected implementation scope:
- Fail-closed Verification contract parsing and focused parser/close regression tests.
- Exact parser behavior belongs to a separate implementation Task.

Relative priority: 1

Rationale:
Verification correctness is the highest-priority Harness property and must be hardened before capability expansion.

### Priority 2 - Candidate B: Duplicate qh start / Lifecycle Guard

Classification: REQUIRED-BEFORE-NEXT-MILESTONE

Evidence:
- During QH-V2-E2E-001 an observed duplicate-start state produced Current Task and Previous Task both pointing to QH-V2-E2E-001 ACTIVE.
- Restoring STATUS and performing one clean invocation produced the correct lifecycle transition.
- command_start currently derives Previous Task from the current lifecycle line and does not explicitly reject starting the already-current ACTIVE Task.

Risk if ignored:
- Repeated operator invocation can corrupt lifecycle Evidence and Previous Task history.

User/operator impact:
- An accidental duplicate command can create confusing or misleading Repository state.

Expected implementation scope:
- Deterministic same-active-Task start guard and focused lifecycle regression tests.

Relative priority: 2

Rationale:
Lifecycle correctness is part of Repository Source-of-Truth integrity and should be fixed before expanding capability.

### Priority 3 - Candidate C: Human-Approved Task Scaffold Generation

Classification: NEXT-HARDENING

Evidence:
- Long manual Task-generation scripts are repeated.
- Verification marker syntax caused a real completion-trust incident.
- Task structure is highly repetitive and mechanically checkable.

Risk if ignored:
- Continued human formatting errors and unnecessary CMD/script friction.

User/operator impact:
- High repetitive effort when defining Tasks.

Expected implementation scope:
- Deterministic scaffold generation only.
- Human still supplies/approves Goal, Scope, Acceptance Criteria, Verification, and Architecture decisions.

Relative priority: 3

Rationale:
Useful after the parser itself is made fail-closed; scaffold generation must not become a substitute for parser correctness.

### Priority 4 - Candidate D: qh doctor

Classification: NEXT-HARDENING

Evidence:
- Repeated manual checks have been needed for Git root, lifecycle state, task existence, Verification parseability, Ollama availability, and model readiness.

Risk if ignored:
- Troubleshooting remains fragmented and slower than necessary.

User/operator impact:
- More manual diagnosis and greater chance of checking the wrong layer.

Expected implementation scope:
- Read-only deterministic environment/state diagnostics.

Relative priority: 4

Rationale:
High operational value, but lower correctness urgency than Candidates A and B.

### Priority 5 - Candidate F: Windows CMD Workflow Simplification

Classification: NEXT-HARDENING

Evidence:
- Repeated quoting, multiline command, prompt-copy, and inline-Python failures occurred during Milestone 1.
- Temporary Python patch scripts proved substantially more reliable.

Risk if ignored:
- Continued operator mistakes and unnecessary recovery work.

User/operator impact:
- Significant Windows CMD friction.

Expected implementation scope:
- Prefer small deterministic utilities or documented Repository-native workflows over fragile long one-liners.

Relative priority: 5

Rationale:
Repeated Evidence now justifies improvement, but it is not a verification-authority issue.

### Priority 6 - Candidate G: Worker Smoke / E2E Standardization

Classification: NEXT-HARDENING

Evidence:
- Native Qwen3:8B smoke succeeded.
- Native Ollama structured tool-call continuation succeeded.
- Real qh run E2E completed with one Runner attempt and exact Git/Test Evidence.

Risk if ignored:
- Future Worker/backend changes may require rebuilding ad hoc smoke procedures.

User/operator impact:
- Regression checks remain more manual than necessary.

Expected implementation scope:
- Reusable bounded smoke/E2E fixture without granting new Worker authority.

Relative priority: 6

Rationale:
Evidence is now sufficient to justify standardization after required safety fixes.

### Priority 7 - Candidate E: qh status UX

Classification: SAFE-TO-DEFER

Evidence:
- Current status output works, but operational state and historical handoff remain verbose.

Risk if ignored:
- Primarily readability and navigation cost.

User/operator impact:
- Slower interpretation of current state.

Expected implementation scope:
- Presentation-only improvements preserving lifecycle semantics.

Relative priority: 7

Rationale:
Useful but not required for correctness or the next implementation stage.

### Priority 8 - Candidate H: STATUS Handoff / Historical State Cleanup

Classification: SAFE-TO-DEFER

Evidence:
- STATUS.md contains substantial historical handoff material accumulated during development.

Risk if ignored:
- Increasing document noise.

User/operator impact:
- Current state becomes harder to scan.

Expected implementation scope:
- Preserve history while separating concise operational state from long historical detail.

Relative priority: 8

Rationale:
No current correctness failure is caused by the accumulated history.

### Review Conclusion

Required before the next capability-expansion milestone:

1. Candidate A - Verification Contract Fail-Closed Hardening.
2. Candidate B - Duplicate qh start / Lifecycle Guard.

Then continue hardening in this order unless new Evidence changes priority:

3. Candidate C - Human-Approved Task Scaffold Generation.
4. Candidate D - qh doctor.
5. Candidate F - Windows CMD Workflow Simplification.
6. Candidate G - Worker Smoke / E2E Standardization.

Candidates E and H are safe to defer.

No Milestone 1 Architecture change is required by this review.
Every implementation remains subject to its own approved Task and Human Gate.

## Verification

Run exactly:

`python -c "from pathlib import Path; s=Path('tasks/QH-V2-HARD-001.md').read_text(encoding='utf-8'); assert all(x in s for x in ('Candidate A','Candidate B','Candidate C','Candidate D','Candidate E','Candidate F','Candidate G','Candidate H'))"`

Then run:

`python -c "from pathlib import Path; s=Path('DECISIONS.md').read_text(encoding='utf-8'); assert 'Post-Milestone 1' in s"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Conditions

STOP before implementation if the review concludes that:

- Milestone 1 Architecture must change;
- Worker tool authority must expand;
- Retry policy must change;
- model/backend policy must change;
- Verification authority must move away from Harness Core;
- automatic Task completion/commit should be introduced.

Those require a separate Architecture decision and Task.

This Review does not itself authorize any code change.
