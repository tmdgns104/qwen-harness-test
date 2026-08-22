# Autonomous Queue Policy Review

## Proposal Only

**AUTONOMOUS QUEUE = NOT AUTHORIZED**

**Human Decision Required**

This document is an Architecture proposal for the separate Human One-Time Autonomous Queue Gate. Completing QH-V2-ARCH-008 does not accept this proposal, does not authorize autonomous execution, and does not change current Repository authority.

The recommended design uses Codex CLI Supervisor as an **optional external executor**. It is not a Harness production component. Harness and the local Qwen path remain Codex-independent and usable without Codex.

## 1. Problem and Intended Outcome

The Repository already has a deterministic queue and Human-reviewed Task contracts. The remaining question is whether one Human approval may authorize an exact, immutable sequence so that the Codex CLI Supervisor can execute one Task at a time without asking for the same activation/commit/close permission after every successful Task.

The proposal must not convert broad Human trust into open-ended automation. Any authority must be bound to exact Repository state, exact Task contracts, exact operations, exact branch/remote constraints, explicit expiry/revocation, and fail-closed STOP conditions.

This proposal does not authorize global or cross-Repository use. ADR-011's later Globalization Gate remains separate.

## 2. Non-Negotiable Preconditions

The one-time Gate is ineligible unless all required preconditions are objectively complete:

- QH-V2-HARD-003: lifecycle start guard COMPLETE - VERIFIED;
- QH-V2-HARD-004: clean-worktree lifecycle invariant COMPLETE - VERIFIED;
- QH-V2-HARD-005: post-Verification Evidence refresh COMPLETE - VERIFIED;
- QH-V2-PERF-004: Verification workflow deduplication may remain an operational optimization but does not change authority;
- working tree clean;
- exact queue and Task contracts ready for Gate review.

QH-V2-HARD-004 and QH-V2-HARD-005 are Harness-owned prerequisites. The Codex CLI Supervisor adds **no compensating safety layer** and must not implement a second lifecycle, Evidence, scope, or Final Gate engine.

## 3. Actor and Authority Model

| Actor | Permitted role under proposal | Never receives |
|---|---|---|
| Human | Defines purpose/scope, approves exact Gate Change Set and Approval Manifest, selects whether commit/close/push delegation is allowed, may revoke at any time | No restriction created by this proposal |
| Codex CLI Supervisor | Optional external executor; validates manifest; executes only exact pre-approved Tasks; may perform only explicitly delegated lifecycle/Git operations | Architecture edits, scope expansion, Task creation, queue reorder, force push, history rewrite, destructive recovery, implicit approval |
| qh/Harness | Deterministic source of scope checks, Verification, Git Evidence, lifecycle checks, and Final Gate | No authority transfer to Codex or Qwen |
| Qwen Worker | Semantic reasoning and small scoped implementation inside one explicitly assigned current Task | General filesystem/shell/Git authority, Verification authority, lifecycle authority, commit/push authority, Architecture authority, Final PASS authority |

The Qwen Worker boundary from ADR-008 is preserved exactly. The Codex CLI Supervisor is not a Worker backend and does not alter WorkerRequest, WorkerResponse, tool authority, retry policy, or Runner behavior.

## 4. Requirement and Decision Conflict Matrix

| Source | Current source meaning | Conflict with pre-approved execution | Proposed treatment | Preserved invariant |
|---|---|---|---|---|
| FR-004 | A Worker executes only the explicitly assigned current Task and must not automatically select or start another Task. | None if Codex CLI Supervisor remains a distinct external executor. Ambiguity exists if future text treats every executor as a Worker. | **preserve** FR-004; later **clarify** REQUIREMENTS.md that Worker restrictions remain unchanged and any Supervisor queue authority is a separate Human-approved policy. | Qwen Worker never self-selects or starts a successor. |
| ADR-005 | Human approval is required for Task approval, semantic review, Task completion approval, and commit decisions. | Repeated per-Task Human completion/commit approval conflicts with one-time advance delegation. | **preserve** Task approval and semantic Human/ChatGPT design authority; narrowly **supersede** repeated commit/completion prompts only for operations explicitly listed in the exact Approval Manifest. | No unapproved Task, Architecture change, or unlisted operation becomes executable. |
| ADR-006 | Every implementation requires its own approved Task and Human Gate; automatic commit/completion/next start are deferred. | One-time Gate would replace repeated per-Task Human Gates for a fixed manifest. | **preserve** the separate approved Task requirement; narrowly **supersede** the repeated Gate invocation only after the Human commits every covered Task in exact approved pre-start form. | Each implementation still has its own immutable approved Task contract. |
| ADR-007 | `qh close` is authoritative; explicit Human close is required; automatic commit/completion/next Task are not authorized. | Supervisor invocation of close and successor progression needs explicit delegation. | **preserve** authoritative `qh close`, complete Verification, Scope Evidence, and Final Gate; narrowly **supersede** who invokes close only if the Human explicitly delegates `qh close` in the manifest. | No stale Evidence, cached PASS, or bypass of close. |
| ADR-008 | Qwen/Worker has no Git, lifecycle, commit, Verification, Evidence, or Architecture authority. | No conflict because the proposed Supervisor is external to the Worker. | **preserve** without modification. | Worker Trust Boundary remains unchanged. |
| ADR-010 | No automatic commit, Task completion, next-Task start, or Architecture mutation; each implementation requires an approved Task and Human Gate. | Exact queue progression conflicts with the automatic-operation prohibition. | **preserve** Architecture prohibition and separately approved Task contracts; narrowly **supersede** only exact manifest-listed lifecycle/Git operations for the approved queue. | No capability expansion, generated Task, or Architecture mutation. |

### Required source changes if the Human accepts later

This proposal itself does not edit `REQUIREMENTS.md` or `DECISIONS.md`.

A later accepted Gate must make the policy explicit rather than relying on interpretation:

1. `REQUIREMENTS.md`: clarify that FR-004 continues to govern the Qwen Worker, and add a narrow requirement for an optional external Supervisor whose authority exists only through an exact Human-approved manifest and fail-closed validation.
2. `DECISIONS.md`: add a new Accepted decision that records the exact narrow supersession of ADR-005, ADR-006, ADR-007, and ADR-010 for the approved manifest while preserving ADR-008 and all deterministic qh/Harness authority.
3. No accepted text may reinterpret ARCH-008 completion itself as permission.

## 5. Approval Manifest

The future **Approval Manifest** is the machine-checkable boundary of one-time authority. It must be generated only from the **post-Gate** committed Repository state and must contain at least:

- schema/version identifier;
- approval ID;
- approved base commit SHA;
- exact `BACKLOG.md` blob identity;
- ordered Task IDs;
- whole-file blob identity for every covered Task contract;
- canonical hash of every covered Task's Immutable Contract Sections;
- allowed local branch;
- allowed remote name, if any;
- allowed remote branch/refspec, if push is enabled;
- permitted operations;
- implementation-commit policy;
- lifecycle-commit policy;
- `qh close` delegation policy;
- push policy;
- fast-forward-only requirement;
- validity start and expiry;
- revocation identifier/state;
- approving Human record;
- Gate Change Set commit SHA;
- audit/checkpoint location and format.

The default push policy is **disabled**. GitHub push becomes eligible only if the Human explicitly pre-approves one remote, one branch/refspec, fast-forward-only behavior, and STOP handling for authentication failure, divergence, rejection, or remote mismatch.

Force push and history rewrite are always forbidden and are never selectable Human approval options.

## 6. Immutable Contract Sections

The following Task sections are **Immutable Contract Sections** for every covered Task:

- Goal;
- Architecture Basis;
- Dependencies;
- Scope;
- Allowed Changes;
- Forbidden Changes;
- Acceptance Criteria;
- Verification;
- Evidence Requirements;
- Stop Conditions;
- Next Task.

The Gate binds each pending Task to its post-Gate whole-file blob and also stores canonical hashes of these authority-bearing sections.

Only explicitly allowlisted lifecycle/status and Result/Evidence mutations may differ during execution. Any other Task mutation is forbidden.

If the implementation cannot mechanically distinguish the allowed mutable portions from Immutable Contract Sections, advance approval must not be enabled. The unresolved result is `DESIGN CHANGE REQUIRED`.

Any mismatch yields:

`Task contract hash mismatch -> STOP`

A whole-file mismatch caused only by an explicitly allowlisted qh-owned lifecycle/Result/Evidence mutation is acceptable only when the immutable-section hash remains exact and the mutation shape is itself allowlisted and auditable.

## 7. Covered Queue

The proposed one-time Gate may cover only the exact unchanged post-Gate sequence committed by the Human. The intended current sequence after Gate G1 is:

1. QH-V2-HARD-006
2. QH-V2-HARD-007
3. QH-V2-OPS-001
4. QH-V2-OPS-002
5. QH-V2-OPS-003
6. QH-V2-OPS-004
7. QH-V2-OPS-005
8. QH-V2-OPS-006
9. QH-V2-M2-SPEC-001
10. HUMAN ARCHITECTURE GATE

QH-V2-HARD-006 and QH-V2-HARD-007 remain ordinary Hardening Tasks with unchanged core behavior. Their existing path-canonicalization and test-integrity contracts remain authoritative. The Supervisor provides **no compensating safety layer** for either.

QH-V2-M2-SPEC-001 always terminates at `HUMAN ARCHITECTURE GATE`. No policy in this proposal may authorize an M2 implementation Task beyond that Gate.

Any queue reorder, inserted Task, removed Task, changed dependency, changed Next Task, or `BACKLOG change` after approval invalidates the manifest and stops execution.

## 8. Gate Change Set

If the Human accepts the proposal later, approval must be materialized as one exact **Gate Change Set** rather than a conversational statement.

The Gate Change Set should contain only the reviewed files/sections needed to make authority explicit, for example:

- `REQUIREMENTS.md`: narrow Supervisor authorization requirement/clarification;
- `DECISIONS.md`: one new Accepted decision recording exact delegation and supersession boundaries;
- every covered pending Task: exact Human-approved pre-start status required by HARD-003, with no Supervisor-authored approval;
- `BACKLOG.md`: authorization-state/banner update only if required; queue order must remain unchanged;
- one Repository-tracked approval manifest location;
- one Repository-tracked audit/checkpoint location or schema decision;
- exact Verification for the Gate Change Set;
- one committed Evidence record identifying the post-Gate state.

The Human, not the Supervisor, approves and commits every Task into its required pre-start form. A PLANNED or DRAFT Task is ineligible. The Supervisor must never rewrite a Task from PLANNED to approved.

The manifest hashes the resulting post-Gate state. A Gate decision is not unscoped write authority.

## 9. Proposed State Machine

### State Machine

```text
GATE_NOT_ACCEPTED
  -> Human accepts exact Gate Change Set
  -> GATE_COMMITTED
  -> manifest built from post-Gate commit
  -> READY(task N)

READY(task N)
  -> validate manifest + queue + task blobs/hashes + branch/remote + clean tree
  -> START_ELIGIBLE
  -> qh start exact already-approved task
  -> ACTIVE(task N)

ACTIVE(task N)
  -> execute only Task contract
  -> focused development checks as permitted
  -> exact implementation commit if delegated
  -> CLOSE_ELIGIBLE
  -> qh close <exact implementation HEAD>

qh close PASS
  -> Final Gate PASS
  -> lifecycle mutation only
  -> lifecycle commit if delegated
  -> require final clean tree
  -> COMPLETE(task N)
  -> validate successor identity
  -> READY(task N+1)

Any mismatch/failure/uncertainty
  -> STOPPED
```

Successor eligibility exists only after the predecessor's exact implementation commit passes authoritative `qh close`, lifecycle changes are committed separately, and the final working tree is clean.

`Final Gate FAIL` always leads to STOPPED. There is no automatic skip, forced completion, or successor start.

## 10. Operation Delegation Choices

The Human One-Time Autonomous Queue Gate must explicitly decide each item below. Nothing is implied by acceptance.

| Operation | Recommended default | Notes |
|---|---|---|
| Start exact already-approved manifest Task | Allow | Only after all eligibility checks pass. |
| Create implementation commit | Allow for exact Task scope | Separate from lifecycle commit; no amend/history rewrite. |
| Invoke authoritative `qh close <implementation HEAD>` | Allow | qh/Harness remains authority; Supervisor only invokes it. |
| Create lifecycle commit after PASS | Allow | Only exact qh-owned lifecycle/result changes. |
| Advance to exact manifest successor | Allow | Only after clean COMPLETE state and full revalidation. |
| Push to GitHub | Disabled by default | Optional explicit remote/branch/refspec, fast-forward-only. |
| Force push | Never | Forbidden. |
| History rewrite/rebase/reset-based recovery | Never | Forbidden. |
| Task creation or contract-authority edit | Never | Requires Human design/Gate. |
| Architecture/Requirement edit during queue execution | Never | Requires STOP + separate Human Gate. |

Recommended narrow policy: allow exact Task start, implementation commit, `qh close`, lifecycle commit, and successor eligibility for the manifest; keep push disabled unless the Human intentionally opts in.

## 11. STOP Matrix

| Condition | Required result |
|---|---|
| Manifest identity mismatch | STOP; no mutation |
| `Task contract hash mismatch` | STOP; no successor |
| Queue identity/order/dependency mismatch | STOP |
| BACKLOG change | STOP |
| Branch mismatch | STOP |
| Remote/refspec mismatch | STOP |
| Dirty tree where clean state is required | STOP |
| Non-allowlisted Task mutation | STOP |
| Scope mismatch or Forbidden change | STOP |
| Final Gate FAIL | STOP; no lifecycle completion |
| Verification nonzero | STOP |
| Known RED cannot be reproduced exactly or distinguished from current regression | STOP |
| Task contract defect or ambiguity | STOP and report Task contract defect |
| Architecture change needed | STOP and report DESIGN CHANGE REQUIRED |
| Requirement change needed | STOP and report DESIGN CHANGE REQUIRED |
| Secret/credential encountered | STOP; do not store or propagate secret/credential material |
| Destructive operation required | STOP; destructive operation is not authorized |
| Force push requested | STOP; force push forbidden |
| History rewrite requested | STOP; history rewrite forbidden |
| Authentication failure / remote divergence / push rejection | STOP; no force workaround |
| Approval expired | STOP |
| Approval revoked | STOP |
| Human response required but absent/timeout | STOP; never default-approve |
| QH-V2-M2-SPEC-001 reaches HUMAN ARCHITECTURE GATE | STOP; no M2 implementation |

There is no retry-based bypass of deterministic safety failure. A known RED is acceptable only when it is pre-approved, reproducible, and mechanically distinguishable from a current regression. Ambiguity stops the queue.

## 12. Audit, Checkpoint, Resume, Expiry, and Revocation

### Audit Record

Every state transition must produce a Repository-grounded or otherwise tamper-evident Audit Record containing at least:

- approval ID and manifest hash;
- Repository identity;
- current base/HEAD;
- current Task ID and Task blob/hash;
- operation attempted;
- start/end timestamps;
- changed paths where applicable;
- Verification/Final Gate result references;
- implementation commit;
- lifecycle commit;
- push result if enabled;
- STOP reason if stopped;
- Human approval/rejection/modification reason when a Gate interaction occurs.

A checkpoint is valid only when it can be reconstructed from Repository state plus the exact manifest. Chat history, Codex session memory, or prior verbal approval is never sufficient resume authority.

Resume must revalidate the full manifest, current Task state, immutable hashes, branch/remote, Git clean state, and last completed audit transition before any new operation.

### Revocation

**Revocation** is immediate. The Human may revoke the approval at any time. A revoked manifest is permanently ineligible for new operations. Re-authorization requires a new Human Gate and new manifest identity.

Expiry behaves the same as revocation for future operations. Human absence, timeout, or inability to verify approval state always stops; it never extends validity automatically.

## 13. Failure and Recovery Limits

The policy authorizes STOP, not destructive self-recovery.

Permitted recovery is limited to actions already safe and explicitly covered by the exact Task or Gate policy. The Supervisor must not invent rollback by reset, force checkout, force push, history rewrite, deleting unknown files, or broad cleanup.

If a Task fails after a write or commit, preserve Evidence and stop for diagnosis under the current Task. Do not skip to the next Task.

If a contract or Architecture issue is discovered, stop and return the decision to Human + ChatGPT. Do not mutate `REQUIREMENTS.md`, `DECISIONS.md`, or the queue during autonomous execution.

## 14. Alternatives

### Alternative A - Keep current per-Task Human Gates

Safest and simplest authority model. No Requirement/Decision changes. Cost: repeated low-value activation/commit/close relay remains.

### Alternative B - One-time exact manifest, local commits/close delegated, push disabled

Recommended starting point. Removes repetitive relay while limiting remote impact. The Human can inspect/push later or separately authorize push.

### Alternative C - One-time exact manifest including one fast-forward GitHub push target

Higher convenience. Acceptable only with one explicit remote, branch/refspec, fast-forward-only enforcement, and fail-closed handling of auth/divergence/rejection. Never force push.

### Alternative D - General autonomous Supervisor without immutable manifest

Rejected by design. It would silently broaden authority, make chat/session state part of the control plane, weaken Task immutability, and conflict with current Requirements/ADRs.

## 15. Risks

- A too-broad manifest could turn one Human decision into unbounded write authority.
- Mutable Task contracts could make advance approval meaningless.
- Allowing Supervisor-authored Task approval would bypass HARD-003's Human boundary.
- Remote push delegation increases blast radius compared with local-only progression.
- Audit state outside the Repository could become stale or unauditable if it is treated as sole authority.
- Ambiguous RED handling could hide a real regression.
- Recovery automation could become more dangerous than the original failure if destructive Git/filesystem operations are permitted.

The design mitigates these risks through exact post-Gate identities, immutable-section hashes, fail-closed STOP, no destructive recovery, default-disabled push, expiry/revocation, and continued qh/Harness final authority.

## 16. Human Decision Checklist

At the separate Gate, the Human must explicitly choose:

- Accept, reject, or defer the policy.
- Exact ordered Tasks covered by the manifest.
- Validity/expiry duration.
- Revocation mechanism.
- Whether Codex CLI Supervisor may invoke `qh start` for already-approved exact Tasks.
- Whether it may create implementation commits.
- Whether it may invoke `qh close`.
- Whether it may create lifecycle commits after Final Gate PASS.
- Whether exact successor advancement is delegated.
- Whether GitHub push remains disabled or is enabled for one exact remote/branch/refspec.
- Audit/checkpoint storage and retention.
- Exact `REQUIREMENTS.md` clarification.
- Exact new `DECISIONS.md` policy text and narrow supersession wording.
- Exact Gate Change Set and Verification.

No unchecked item is implicitly approved.

## 17. Recommended Gate Outcome

If the Human wants to reduce repetitive relay while retaining the current trust model, the recommended proposal is:

1. Preserve FR-004 and ADR-008 unchanged for the Qwen Worker.
2. Human pre-approves every covered Task contract and commits their exact pre-start form.
3. Add a narrow Requirement and Accepted Decision for an optional external Codex CLI Supervisor bound to one immutable Approval Manifest.
4. Delegate exact Task start, implementation commit, authoritative `qh close`, lifecycle commit, and exact successor eligibility.
5. Keep GitHub push disabled initially; optionally authorize one fast-forward-only target later in the same Gate if desired.
6. Revalidate the manifest before every state transition.
7. STOP on any mismatch, ambiguity, failure, expiry, revocation, Human timeout, contract defect, Architecture need, secret/credential issue, destructive operation, force push/history rewrite request, or HUMAN ARCHITECTURE GATE.

This is a recommendation for the Human Gate only. It is not authorization.

## 18. Gate Result Boundary

QH-V2-ARCH-008 completion only proves that this proposal is complete and internally reviewable.

Until the later Human Gate accepts and commits the required `REQUIREMENTS.md`, `DECISIONS.md`, Task approval states, Approval Manifest, Gate Change Set, and Evidence:

**AUTONOMOUS QUEUE = NOT AUTHORIZED**

The Codex CLI Supervisor must not auto-start QH-V2-HARD-006, and no later Task may infer approval from this document, chat history, or ARCH-008 completion.
