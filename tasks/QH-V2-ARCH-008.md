# QH-V2-ARCH-008 - Pre-Approved Codex Backlog Execution Policy

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

The Repository now contains a deterministic Hardening and Operations queue with
Human-reviewed Task contracts. Requiring a fresh Human activation decision after
every successful Task may be avoidable for an exact, immutable, pre-approved queue.

The current Accepted Architecture does not authorize that behavior. FR-004 and
ADR-005, ADR-006, ADR-007, ADR-008, and ADR-010 preserve Human lifecycle authority
or explicitly defer/forbid automatic commit, completion, and next-Task start.
Treating advance approval as already equivalent to those gates would silently
reinterpret the Source of Truth.

## Goal

Prepare an Architecture decision proposal for whether a Codex CLI Supervisor may,
after a one-time Human approval of an exact queue and exact Task-contract versions,
execute one Task at a time without repeated activation prompts.

The default proposal treats the Codex CLI Supervisor as an optional external executor,
not a Harness production component. Harness and the Qwen Worker must remain usable
without Codex. The proposal must preserve the Qwen Worker boundary and identify every
Requirement or Accepted Decision that needs clarification or narrow supersession.
This Task does not accept the proposal, implement a Supervisor, or authorize
autonomous queue execution.

## Architecture Basis

- FR-004 assigns a Worker only the explicitly assigned current Task and prohibits
  Worker selection or start of another Task.
- FR-001 and FR-009 preserve Codex-independent continuation and keep Codex optional.
- FR-011 and ADR-002 keep Harness contracts/backend boundaries independent from one
  optional executor or model path.
- FR-006 and FR-008 require objective Evidence and fail-closed stopping.
- ADR-005 preserves Human approval for Task approval, completion, and commit decisions.
- ADR-006 requires an approved Task and Human Gate for every implementation and
  defers automatic commit, completion, and next-Task start.
- ADR-007 makes `qh close` authoritative while requiring an explicit Human close
  operation and prohibiting automatic commit, completion, and next-Task start.
- ADR-008 keeps all Qwen/Worker lifecycle, Git, commit, and Architecture authority
  forbidden; that Worker boundary must remain unchanged.
- ADR-010 again prohibits automatic commit, completion, and next-Task start and
  requires each implementation to have its own approved Task and Human Gate.
- QH-V2-HARD-003 is the remaining ADR-010 REQUIRED-BEFORE-NEXT-MILESTONE fix.
- QH-V2-HARD-004 and QH-V2-HARD-005 strengthen the clean lifecycle and final
  post-Verification Evidence boundary required before unattended repetition.

## Dependencies

- QH-V2-DOC-002 is COMPLETE - VERIFIED and remains the completed first queue stage.
- QH-V2-HARD-003, QH-V2-HARD-004, and QH-V2-HARD-005 must each be
  COMPLETE - VERIFIED through the ordinary Human Task Gate before this proposal starts.
- The current Requirement and Accepted ADR policy remains authoritative throughout
  this Task; autonomous start, commit, close, completion, push, or queue advance is
  not authorized by a PLANNED or COMPLETE proposal.
- A Human must explicitly approve this proposal Task before `qh start`.

## Scope

- Create `docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md` as a proposal for the separate
  Human One-Time Autonomous Queue Gate.
- Use an optional external Codex CLI executor as the default design. Do not add a
  Supervisor module, service, state store, dependency, or runtime path to Harness
  production code, and do not make Codex required for Harness/Qwen operation.
- Distinguish Human, Codex CLI Supervisor, deterministic qh/Harness, and Qwen Worker
  roles without granting Qwen any new tool or lifecycle authority.
- Analyze FR-004 and ADR-005, ADR-006, ADR-007, ADR-008, and ADR-010 clause by
  clause as preserve, clarify, or narrowly supersede; do not force a convenient
  reinterpretation.
- Define an immutable approval manifest containing at least the approved base commit,
  `BACKLOG.md` blob identity, ordered Task IDs, every Task-contract blob identity,
  allowed branch/remote, permitted operations, commit policy, push policy, validity,
  revocation, and approving Human record.
- Define `Immutable Contract Sections` for authority-bearing Task content separately
  from explicitly allowlisted lifecycle/status and Result/Evidence mutations. The
  manifest must bind pending Tasks to their post-Gate whole-file blobs and preserve
  canonical hashes of Goal, Architecture Basis, Dependencies, Scope, Allowed/Forbidden,
  Acceptance, Verification, Evidence Requirements, Stop Conditions, and Next Task
  throughout execution. If current tooling cannot verify that distinction, the
  proposal must stop at a required implementation decision rather than ignore it.
- Define how the Human Gate records every queued contract's exact approved pre-start
  status and commits those immutable versions. HARD-003 will reject PLANNED or DRAFT
  targets, and the Supervisor must never rewrite a Task from PLANNED to approved.
- Define eligibility and state transitions that enforce one ACTIVE Task, exact
  predecessor completion, exact contract/queue identity, clean working tree,
  implementation commit, authoritative `qh close`, Final Gate PASS, separate
  lifecycle commit, final clean state, and only then successor eligibility.
- Analyze whether the Supervisor may create implementation and lifecycle commits,
  whether it may perform a non-force fast-forward push to one allowlisted remote
  branch, and which choices remain Human decisions.
- Treat completed HARD-004 clean-lifecycle enforcement and HARD-005 post-Verification
  Evidence refresh as mandatory Harness-owned prerequisites. Do not design temporary
  Supervisor compensating checks or a second lifecycle/Evidence engine.
- Record HARD-006 and HARD-007 as the first post-Gate Hardening Tasks. Their
  implementation, scope, and Verification contracts remain authoritative; only the
  required queue Dependencies and Next Task links reflect Gate G1. The optional
  executor does not pre-implement or compensate for their path-canonicalization or
  test-integrity behavior.
- Define a `Gate Change Set` for any accepted outcome. It must list exact allowed
  files/sections, proposed Requirement and Decision updates, Task pre-start status
  changes, approval-manifest location, any BACKLOG authorization-state update,
  Verification, and one committed Evidence record. The manifest hashes the post-Gate
  state. Updating an authorization banner is distinct from changing queue order or
  contract authority, which invalidates the proposal and requires new review.
- Prohibit Supervisor edits to Immutable Contract Sections and every Task mutation
  not explicitly allowlisted as qh-owned lifecycle/status or Result/Evidence output;
  also prohibit queue edits or reordering, generated Task execution,
  Architecture/Requirement edits, scope expansion, Forbidden changes, destructive
  operations, force push, and history rewrite.
- Define fail-closed STOP behavior for Final Gate failure, ambiguous known RED versus
  regression, contract defects, Architecture needs, Forbidden changes, secrets or
  credentials, destructive operations, queue changes, and the Milestone 2 Human Gate.
- Define checkpoint, audit, resume, expiry, and revocation records so a restart cannot
  infer authority from chat history or stale approval.
- Define Human-gate response and absence behavior: timeout or no response never
  auto-approves, the queue remains stopped, and approval/rejection/modification
  reasons are retained in the audit record.
- Present alternatives, risks, rollback/recovery limits, open questions, and an
  explicit Human decision checklist. Do not create an implementation Task.

## Allowed Changes

- `docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-008.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `src/**`
- `README.md`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `docs/QUICKSTART.md`
- `docs/HOW_IT_WORKS.md`
- `docs/DEVELOPMENT.md`

Every other path, including every other Task contract, remains default-denied.

## Acceptance Criteria

1. The review prominently states `AUTONOMOUS QUEUE = NOT AUTHORIZED` under the
   current Source of Truth and explains that ARCH-008 completion is not acceptance.
2. The default design is an optional external Codex CLI executor, not a Harness
   production component; Harness and Qwen operation remains Codex-independent.
3. Human, Codex CLI Supervisor, qh/Harness, and Qwen Worker responsibilities are
   separate, and Qwen receives no new filesystem, shell, Git, lifecycle, Verification,
   commit, push, or Architecture authority.
4. A conflict matrix covers FR-004 and ADR-005, ADR-006, ADR-007, ADR-008, and
   ADR-010 with source wording, conflict, preserved invariant, and required
   clarify/supersede action.
5. The review identifies any required `REQUIREMENTS.md` clarification separately
   from a later Human-Accepted `DECISIONS.md` change; neither file is edited here.
6. HARD-003, HARD-004, and HARD-005 COMPLETE - VERIFIED Evidence is a mandatory
   precondition; no temporary Supervisor lifecycle or Evidence safeguard substitutes for it.
7. The proposed approval manifest binds authority to an exact base, queue order,
   contract versions, branch/remote, operation set, validity period, and Human approval.
8. Any manifest, queue, Immutable Contract Section, Task contract hash, scope, branch,
   remote, approved operation, or non-allowlisted lifecycle/Result/Evidence mutation
   invalidates advance approval and causes `Task contract hash mismatch -> STOP` or
   the corresponding fail-closed STOP result.
9. Pending Tasks are bound to post-Gate whole-file blobs, while authority-bearing
   Immutable Contract Sections remain hash-stable across approved lifecycle and
   Result/Evidence mutations. No unspecified Task mutation is exempt.
10. The Human Gate, not the Supervisor, must record and commit the exact approved
   pre-start Task versions required by HARD-003; PLANNED contracts remain ineligible.
11. An accepted Gate has an exact verified and committed Gate Change Set; the Gate
   decision itself is not unscoped Repository mutation authority.
12. The proposed state machine permits at most one ACTIVE Task and advances only after
   the predecessor's exact implementation commit passes `qh close`, lifecycle changes
   are committed separately, and the working tree is clean.
13. Task creation, Task-contract authority edits, queue edits/reordering, Architecture changes,
   scope expansion, Forbidden changes, force push, history rewrite, and destructive
   operations are never authorized by the queue policy.
14. Implementation-commit, lifecycle-commit, `qh close`, and optional fast-forward
    GitHub push authority are explicit Human decision items rather than assumed
    permissions.
15. Force push and history rewrite are always forbidden and are never Human-approval options.
16. The STOP matrix includes every condition required by this Task and specifies no
    automatic skip, retry-based bypass, rollback fiction, or successor start.
17. Known RED handling requires pre-approved, reproducible Evidence that distinguishes
    it from a current regression; ambiguity stops the queue.
18. Audit/checkpoint records are Repository-grounded, resume-safe, revocable, and do
    not depend on chat history.
19. QH-V2-M2-SPEC-001 always terminates at `HUMAN ARCHITECTURE GATE`; the policy cannot
    authorize any M2 implementation Task.
20. The review makes GitHub push disabled by default unless the Human explicitly
    pre-approves one remote, branch/refspec, fast-forward-only behavior, and STOP
    handling for authentication, divergence, rejection, or remote mismatch.
21. HARD-006 and HARD-007 remain post-Gate Tasks under unchanged core behavioral
    contracts, with only queue Dependencies and Next Task links updated; the
    Supervisor adds no temporary compensating safety layer for either Task.
22. Human absence, timeout, expired approval, or revoked approval stops without a
    default approval, and approval/rejection/modification reasons remain auditable.
23. The output is proposal-only, lists Human choices and alternatives, and creates no
    ADR, Requirement change, implementation Task, production code, or test change.
24. Task-range changed paths contain only Allowed Changes and `git diff --check` passes.

## Verification

Run exactly:

`python -c "from pathlib import Path; s=Path('docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md').read_text(encoding='utf-8'); required=('AUTONOMOUS QUEUE = NOT AUTHORIZED','optional external executor','Codex-independent','Human','Codex CLI Supervisor','qh/Harness','Qwen Worker','Approval Manifest','Immutable Contract Sections','Task contract hash mismatch','Gate Change Set','post-Gate','State Machine','Audit Record','Revocation','no compensating safety layer'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md').read_text(encoding='utf-8'); required=('FR-004','ADR-005','ADR-006','ADR-007','ADR-008','ADR-010','preserve','clarify','supersede','REQUIREMENTS.md','DECISIONS.md'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md').read_text(encoding='utf-8'); required=('QH-V2-HARD-004','QH-V2-HARD-005','QH-V2-HARD-006','QH-V2-HARD-007','QH-V2-OPS-001','QH-V2-OPS-002','QH-V2-OPS-003','QH-V2-OPS-004','QH-V2-OPS-005','QH-V2-OPS-006','QH-V2-M2-SPEC-001','Final Gate FAIL','known RED','Architecture change','Task contract defect','Forbidden change','secret/credential','force push','history rewrite','destructive operation','BACKLOG change','HUMAN ARCHITECTURE GATE'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('docs/AUTONOMOUS_QUEUE_POLICY_REVIEW.md').read_text(encoding='utf-8'); assert all(x in s for x in ('Proposal Only','Human Decision Required')); assert '## Accepted Decision' not in s and '## Accepted ADR' not in s"`

Then run:

`python -m unittest tests.test_harness_core.VerificationCommandContractTests`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- The policy review contains the actor/authority table, conflict matrix, immutable
  approval manifest, state machine, STOP matrix, audit/resume model, alternatives,
  and explicit Human decision checklist.
- Every conflict classification is tied to current Repository text rather than chat
  interpretation, and proposed changes remain visibly unaccepted.
- ChangeScope and Verification parsers accept this contract; all marked commands
  execute with exit 0 when the proposal artifact is complete.
- Git Evidence proves no production, test, Requirement, Decision, Backlog, or other
  Task file changed.
- Exact implementation HEAD is used by the Human-invoked `qh close`; all Verification
  commands exit 0, Unexpected Changed Paths is no, Diff Check is 0, and Final Gate is PASS.
- Lifecycle changes are committed separately and final `git status --short` is empty.

## Stop Conditions

STOP without expanding scope if:

- accepting or editing `REQUIREMENTS.md` or `DECISIONS.md` is requested inside this Task;
- a Supervisor prototype, production change, test change, or implementation Task is needed;
- Qwen/Worker authority would expand or qh/Harness Evidence authority would weaken;
- the approval manifest, pending Task whole-file hash, or Immutable Contract Section
  hash does not match exactly;
- `BACKLOG.md`, queue order, Task authority, Architecture, scope, or a Forbidden path
  would need to change outside the exact Human-approved Gate Change Set;
- Final Gate fails or known RED cannot be distinguished from a current regression;
- the conflict cannot be represented honestly without an unresolved Human decision;
- the proposed policy needs mutable contracts, queue reordering, generated Tasks,
  destructive recovery, force push, history rewrite, or credential storage;
- a secret or credential is encountered;
- QH-V2-M2-SPEC-001 completes and reaches the Human Architecture Gate;
- any Gate is treated as implicitly approved by Task completion.

Report `DESIGN CHANGE REQUIRED` and carry the unresolved decision to the Human Gate.

## Next Task

HUMAN ONE-TIME AUTONOMOUS QUEUE GATE - NO AUTOMATIC TASK.

If the Human rejects or defers the proposal, autonomous execution remains forbidden;
QH-V2-HARD-006 may continue only through the ordinary explicit Human Task Gate.
If the Human accepts it, the required Requirement clarification and Accepted Decision
must be recorded and committed before QH-V2-HARD-006 can become eligible under the
exact approved manifest. ARCH-008 itself never starts QH-V2-HARD-006.
