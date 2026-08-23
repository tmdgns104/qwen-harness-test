# QH-V2-ARCH-017 - Exception-Driven Human Supervision Policy

## Status

APPROVED - READY FOR CONTRACT BASELINE

The Human explicitly approved replacing repeated per-step approval prompts with an exception-driven supervision model, while preserving deterministic Harness authority and Human control over Architecture, Trust Boundary, and new-direction decisions.

## Problem

The current Repository policy requires repeated Human approval for normal lifecycle steps even when the Task contract is already approved and deterministic checks are available.

This creates unnecessary relay overhead for routine actions such as focused implementation, Verification, authoritative `qh close`, lifecycle commit, and safe fast-forward push.

The Human now wants normal, already-authorized work to continue without repeated approval prompts and wants to be interrupted primarily when:

- a problem, failure, ambiguity, or policy conflict occurs; or
- a new proposal, new direction, Architecture decision, Trust Boundary change, Candidate promotion, or Task/queue decision needs Human judgment.

Existing Source of Truth must be reconciled before this behavior is treated as project policy. In particular, BACKLOG currently says ordinary per-Task Human Gates are mandatory and several Accepted ADRs defer automatic successor continuation.

## Goal

Record an Accepted Architecture policy for **Exception-Driven Human Supervision** that distinguishes:

1. routine continuation inside already-approved boundaries; and
2. exception conditions that still require Human review.

The policy must reduce repeated Human prompts without weakening deterministic safety, Evidence, Verification, Final Gate, scope, or Worker authority.

This Task is Architecture/documentation reconciliation only. It does not implement new automation code.

## Architecture Basis

- ADR-001: deterministic Harness checks remain authoritative.
- ADR-005 / ADR-006 / ADR-007 / ADR-010: earlier policy retained repeated Human lifecycle gates and deferred automation.
- ADR-012 / ADR-013: the former G1 manifest is historical and revoked; it must not be reactivated or rewritten.
- ADR-014: Qwen Worker still may not self-authorize multi-tool continuation or broader authority.
- ADR-015: unsuccessful closure remains truthful non-success and must not auto-advance.
- ADR-016: WORKER-DIAG-001 required Human-reviewed disposition before the next Worker path; that review is now complete.
- FR-004 remains unchanged: a Worker executes only its explicitly assigned current Task and never selects or starts a successor.
- FR-006, FR-008, FR-012, and FR-013 remain unchanged.

The new policy applies to Human/ChatGPT/Supervisor workflow governance, not to Qwen Worker authority.

## Proposed Policy

### Normal continuation that should not require a new Human approval prompt

After this policy is Accepted and recorded, a normal workflow may continue without asking the Human again for each mechanical step when all applicable preconditions are already satisfied:

- the current Task contract is already approved;
- exactly one Task is ACTIVE;
- work remains inside the current Task Allowed/Forbidden scope;
- no Architecture or Trust Boundary change is required;
- focused tests and required Verification are passing;
- `qh close <exact implementation HEAD>` reaches authoritative Final Gate PASS;
- lifecycle mutation is limited to expected lifecycle files;
- Git state is clean where required;
- push is safe and fast-forward-only to an already-authorized target;
- any successor is already explicitly selected/approved by Repository Source of Truth and its dependencies are satisfied.

Routine continuation may include:

- scoped implementation within an approved Task;
- focused RED/GREEN and regression checks already authorized by that Task;
- Verification;
- authoritative `qh close` at the exact implementation HEAD;
- separate lifecycle commit after Final Gate PASS;
- safe fast-forward push to the already-authorized remote/branch;
- starting the exact next already-approved successor when Repository Source of Truth unambiguously identifies it and no exception condition is present.

This is approval-cadence policy. Existing production tools gain no new technical authority merely because this ADR is recorded. Any unattended software implementation of these steps requires a later approved implementation Task.

### Exception conditions that require Human review / report

STOP normal continuation and report to the Human when any of the following occurs:

- Verification, test, Diff Check, Scope Check, Final Gate, or deterministic invariant fails;
- unexpected changed paths or unexpected Repository mutation appears;
- the Worker returns BLOCKED, repeated timeout/failure, SAFETY failure, or another unresolved execution failure;
- Git has divergence, non-fast-forward state, branch/remote ambiguity, conflict, dirty-state ambiguity, or destructive recovery would be required;
- Requirements, Accepted ADRs, Task scope, or dependency records conflict or are ambiguous;
- the next Task is not already selected/approved in Repository Source of Truth;
- a new Task must be created or an existing queue priority changed;
- a Candidate is proposed for production promotion;
- model policy, `think` policy, timeout policy, Worker step budget, Retry policy/classification, tool schema/authority, filesystem/shell/Git/network authority, Verification authority, Final Gate authority, lifecycle semantics, or Trust Boundary would change;
- Architecture or Requirements must change;
- Globalization or cross-Repository authority would be expanded;
- the system wants to propose an optional improvement or materially different direction for Human consideration.

A deterministic FAIL may never be overridden by an LLM recommendation.

### Successor rule

FR-004 remains unchanged. Qwen itself never selects or starts the successor.

A Human/ChatGPT/Supervisor workflow may continue to the next Task without a fresh approval prompt only when the exact successor is already approved by Repository Source of Truth, all dependencies are satisfied, the previous Task completed successfully, and no exception condition exists.

`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`, FAIL, BLOCKED, or ambiguous termination never auto-advances.

New Task creation, reprioritization, or Architecture-dependent successor selection remains an exception requiring Human judgment.

## Scope

- Record a new Accepted ADR defining Exception-Driven Human Supervision.
- Update BACKLOG governance text so repeated per-step Human prompts are no longer mandatory for already-approved normal continuation.
- Reconcile Requirements only as necessary to distinguish Worker FR-004 from external workflow/supervisor continuation.
- Preserve the revoked G1 manifest as historical Evidence only.
- Record that production automation for unattended continuation is not implemented by this Task.
- Nominate the already Human-selected Worker robustness path after this Architecture policy is complete, without implementing it here.

## Allowed Changes

- `DECISIONS.md`
- `REQUIREMENTS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-017.md`

## Forbidden Changes

- all production code
- all tests
- `tools/**`
- `ops/qhops/**`
- Worker/model/backend/prompt files
- `PROJECT.md`
- any Task file other than `tasks/QH-V2-ARCH-017.md`
- the sealed historical G1 manifest
- Worker tool authority
- Retry/step-budget behavior
- Verification or Final Gate behavior
- lifecycle implementation behavior
- Git implementation behavior
- automatic Candidate promotion
- automatic Task creation
- Globalization authorization

All paths not explicitly Allowed remain default-denied.

## Acceptance Criteria

1. DECISIONS records a new Accepted ADR for Exception-Driven Human Supervision.
2. The ADR explicitly distinguishes routine already-approved continuation from Human-review exceptions.
3. FR-004 remains unchanged in meaning: Qwen Worker cannot select/start a successor.
4. Requirements clarify, if necessary, that external workflow/supervisor continuation is distinct from Worker successor selection.
5. BACKLOG no longer claims a fresh Human prompt is mandatory before every mechanical step when the Task/queue authority is already approved.
6. BACKLOG still requires Human review for new Task creation, reprioritization, Architecture/Requirements/Trust Boundary changes, Candidate promotion, failures, ambiguity, and unsafe Git/state conditions.
7. Failed, BLOCKED, SAFETY, unsuccessful-terminal, or ambiguous Tasks never auto-advance.
8. `qh close` remains the authoritative Final Gate and deterministic FAIL cannot be overridden by an LLM.
9. The revoked G1 manifest remains historical Evidence and is not rewritten/resealed/reactivated.
10. No production automation implementation changes in this Task.
11. The policy states that unattended software automation requires a separate implementation Task.
12. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
13. The post-policy next work may return to the already selected `QH-V2-WORKER-ROB-002` experiment path, but this Task does not implement or start it automatically.

## Verification

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); r=Path('REQUIREMENTS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); assert 'Exception-Driven Human Supervision' in d; assert 'FR-004 - One Task at a time' in r; assert 'Worker must execute only the explicitly assigned current Task' in r; assert 'GLOBALIZATION = NOT AUTHORIZED' in d; assert 'exception' in b.lower()"`

Then run:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8').lower(); b=Path('BACKLOG.md').read_text(encoding='utf-8').lower(); required=['final gate','blocked','architecture','new task','candidate']; assert all(x in d or x in b for x in required); assert 'qwen' in d and 'successor' in d"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Show exact DECISIONS/REQUIREMENTS/BACKLOG policy diff.
- Confirm FR-004 Worker boundary remains intact.
- Confirm revoked G1 historical Evidence is untouched.
- Confirm no production/test/qhops/Worker files changed.
- Verification commands exit 0.
- Baseline-to-implementation changed paths are only Allowed Changes.
- Exact implementation HEAD is used by normal `qh close`; Final Gate PASS is required.
- Lifecycle close commit remains separate.
- Final working tree is clean.

## Stop Conditions

STOP and report to the Human if this policy requires:

- granting Qwen successor-selection authority;
- weakening deterministic scope, Verification, Evidence, or Final Gate authority;
- allowing continuation after FAIL/BLOCKED/SAFETY/unsuccessful termination;
- force push, rebase, reset, destructive recovery, or ambiguous Git mutation;
- automatic Task creation or Architecture mutation;
- production automation implementation inside this Architecture Task;
- reactivating or rewriting G1;
- Globalization authorization.

## Next Task

After this Task is COMPLETE - VERIFIED, normal work may return to the already Human-selected `QH-V2-WORKER-ROB-002` experiment path under the new exception-driven approval cadence.

Do not implement WORKER-ROB-002 inside this Architecture Task.