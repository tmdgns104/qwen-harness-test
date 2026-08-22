# QH-V2-GATE-001 - Autonomous Queue Gate Materialization and Supervisor Guard

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

HUMAN ONE-TIME AUTONOMOUS QUEUE GATE after QH-V2-ARCH-008.

Human Gate decision: ACCEPTED on 2026-08-22.

## Problem

QH-V2-ARCH-008 is COMPLETE - VERIFIED and the Human has accepted the proposed narrow
one-time autonomous queue policy. The accepted policy permits an optional external
Codex CLI Supervisor to advance through one exact pre-approved queue without repeated
Human relay, while preserving deterministic qh/Harness authority and the Qwen Worker
Trust Boundary.

The policy cannot safely become executable from documentation alone. Current qhops
has no deterministic Approval Manifest validator, cannot hash Immutable Contract
Sections, and has no manifest-guarded Supervisor lifecycle commands. ARCH-008 explicitly
requires fail-closed STOP rather than enabling advance approval when that distinction
cannot be checked mechanically.

Therefore the accepted Gate must be materialized before QH-V2-HARD-006 can run under
autonomous authority.

## Goal

Materialize the accepted Human Gate as Repository Source of Truth and implement the
smallest deterministic qhops guard needed for a Codex CLI Supervisor to execute the
exact approved queue safely.

After this Task is COMPLETE - VERIFIED, and only after an exact sealed Approval
Manifest passes deterministic validation, the Codex CLI Supervisor may execute the
covered queue without repeated Human activation/commit/close prompts.

This Task does not execute QH-V2-HARD-006 or any later covered Task.

## Accepted Human Gate Choices

The Human approved this exact covered queue:

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

The Human delegated, only under a valid exact manifest:

- start the exact next already-approved covered Task;
- create the Task implementation commit(s);
- invoke authoritative `qh close <exact implementation HEAD>`;
- create the separate lifecycle commit after Final Gate PASS;
- advance to the exact manifest successor after full revalidation;
- push to `origin/main` using fast-forward-only behavior.

Always forbidden:

- Task creation during autonomous queue execution;
- Task-contract authority edits;
- queue insertion, removal, or reordering;
- Architecture or Requirements changes during covered execution;
- scope expansion or Forbidden changes;
- force push, rebase/history rewrite, destructive recovery, or broad cleanup;
- bypassing Verification, Evidence, Diff Check, or Final Gate;
- expanding Qwen/Worker filesystem, shell, Git, lifecycle, Verification, commit, push,
  Architecture, or Final PASS authority.

Any manifest, queue, Task immutable-section, branch, remote, scope, lifecycle, or
approval mismatch must STOP fail-closed.

## Architecture Basis

- QH-V2-ARCH-008 is COMPLETE - VERIFIED and produced the Human-reviewed proposal.
- The Human One-Time Autonomous Queue Gate accepted the recommended narrow policy,
  with GitHub push explicitly enabled only for `origin/main`, fast-forward-only.
- FR-004 remains a Qwen Worker rule; the external Codex CLI Supervisor is not a Worker.
- ADR-005, ADR-006, ADR-007, and ADR-010 require narrow explicit supersession before
  repeated Human lifecycle prompts can be delegated.
- ADR-008 remains fully preserved; Qwen/Worker authority does not expand.
- ADR-007 keeps `qh close` as the authoritative full final Verification path.
- ADR-011 keeps Codex optional and Globalization separately unauthorized.
- HARD-003 requires every covered target Task to already be in the exact approved
  pre-start state; the Supervisor must never promote PLANNED/DRAFT to approved.
- HARD-004 and HARD-005 remain mandatory clean-lifecycle and fresh-Evidence boundaries.
- PERF-004 keeps focused development checks separate from one authoritative final close.

## Dependencies

- QH-V2-ARCH-008: COMPLETE - VERIFIED.
- QH-V2-PERF-004: COMPLETE - VERIFIED.
- QH-V2-HARD-003, HARD-004, and HARD-005: COMPLETE - VERIFIED.
- Human One-Time Autonomous Queue Gate: ACCEPTED.
- This Task is a pre-manifest Gate materialization prerequisite and is not part of the
  covered autonomous queue. The covered queue still begins with QH-V2-HARD-006.

## Scope

### A. Record the accepted Gate

- Add a narrow Requirement for an optional external Codex CLI Supervisor whose
  authority exists only under an exact Human-approved manifest and deterministic
  fail-closed validation.
- Preserve FR-004 as the Qwen Worker one-Task rule.
- Add one Accepted ADR recording the exact narrow supersession of repeated Human
  lifecycle prompts from ADR-005/006/007/010 for the accepted manifest only.
- Preserve ADR-008 and qh/Harness deterministic authority unchanged.
- Record push authority as exactly `origin/main`, fast-forward-only; force push and
  history rewrite remain always forbidden.
- Update BACKLOG authorization text to distinguish `G1 POLICY ACCEPTED` from actual
  execution eligibility and to keep the covered queue order unchanged.
- Create `docs/AUTONOMOUS_QUEUE_GATE_EVIDENCE.md` recording the Human decision,
  accepted operations, covered queue, STOP boundary, and materialization Evidence.

### B. Pre-approve the exact covered Task contracts

Change only the Status field value of these existing Task files from `PLANNED` to
`APPROVED - READY FOR CONTRACT BASELINE`:

- `tasks/QH-V2-HARD-006.md`
- `tasks/QH-V2-HARD-007.md`
- `tasks/QH-V2-OPS-001.md`
- `tasks/QH-V2-OPS-002.md`
- `tasks/QH-V2-OPS-003.md`
- `tasks/QH-V2-OPS-004.md`
- `tasks/QH-V2-OPS-005.md`
- `tasks/QH-V2-OPS-006.md`
- `tasks/QH-V2-M2-SPEC-001.md`

No other byte in those nine Task contracts may change before manifest sealing.

### C. Add deterministic qhops manifest guard

Implement an operator-only deterministic guard under `ops/qhops/`; do not create a
second Harness Verification, Evidence, scope, or Final Gate engine.

The guard must support at least:

1. `qhops gate-seal`
   - usable only for this accepted Gate materialization flow;
   - requires clean working tree at the committed Gate Change Set state;
   - records that HEAD as `gate_change_set_commit` / approved base;
   - records exact `BACKLOG.md`, `REQUIREMENTS.md`, and `DECISIONS.md` blob identities;
   - records the exact ordered covered Task IDs;
   - records every covered Task pre-start whole-file Git blob identity;
   - records a SHA-256 canonical hash of each covered Task's Immutable Contract Sections;
   - records local branch `master`, remote `origin`, remote branch `main`, push refspec
     `HEAD:main`, and fast-forward-only policy;
   - records delegated and forbidden operations;
   - records validity from the sealed Gate state until the first of revocation,
     manifest mismatch, queue completion at the Human Architecture Gate, or policy invalidation;
   - records the Human Gate evidence path and audit/checkpoint policy;
   - writes exactly `ops/qhops/autonomous_queue_manifest.json` and does not push,
     start a Task, modify lifecycle, or infer PASS.

2. `qhops gate-check`
   - read-only and deterministic;
   - validates manifest schema, repository/branch/remote, Gate source blobs, BACKLOG
     identity, queue order, covered Task identity, lifecycle eligibility, and revocation;
   - validates pending/ACTIVE covered Task whole-file identity where exact pre-start
     identity is required;
   - validates Immutable Contract Sections for every covered Task even after the
     allowed lifecycle Status transition;
   - reports a stable non-zero STOP for every mismatch.

3. Manifest-guarded Supervisor lifecycle entry points
   - provide explicit Supervisor commands for start, implementation-commit, and finish
     rather than reinterpreting ordinary Human commands;
   - every Supervisor command must call deterministic gate validation before mutation;
   - start may select only the exact next manifest Task and only when that Task is
     already `APPROVED - READY FOR CONTRACT BASELINE`;
   - start must never call or reuse `approve_task_file()` to promote a Task;
   - implementation commit must preserve current Task scope and focused-development
     behavior from PERF-004;
   - finish must invoke authoritative `qh close <exact HEAD>` exactly once, require
     Final Gate PASS, create a separate lifecycle commit, revalidate successor
     eligibility, and use existing safe fast-forward push to `origin/main`;
   - no Supervisor command may force push, rewrite history, skip a failed Task, create
     a Task, edit contracts, or edit Architecture/Requirements.

Recommended command names are:

- `qhops gate-seal`
- `qhops gate-check`
- `qhops supervisor-start`
- `qhops supervisor-commit-impl`
- `qhops supervisor-finish`

Equivalent names are acceptable only if the semantics remain explicit and documented.

### D. Immutable Contract Sections

Canonical hashing must cover these exact H2 sections when present in each covered Task:

- Goal
- Architecture Basis
- Dependencies
- Scope
- Allowed Changes
- Forbidden Changes
- Acceptance Criteria
- Verification
- Evidence Requirements
- Stop Conditions
- Next Task

Hashing must be deterministic and fail closed for a missing, duplicate, or malformed
required section. V1 may allow only the `Status` lifecycle value to differ after a
covered Task closes; no unspecified Result/Evidence mutation exemption is required.

### E. Audit and resume

- Git state plus the exact manifest is the authoritative resume checkpoint.
- Supervisor operations may append a supplemental user-local audit record under
  `%USERPROFILE%\.qhops\audit\`; that audit is not completion authority.
- Resume must revalidate manifest, current lifecycle, Task immutable hashes, branch,
  remote, and clean-state prerequisites before mutation.
- Chat history or Codex session memory must never be resume authority.

### F. Two-phase Gate sealing

Avoid a self-referential commit hash:

1. Commit A = Gate Change Set: Requirement/Decision/BACKLOG updates, exact Task
   pre-approvals, qhops guard implementation/tests/docs, and Gate Evidence.
2. From clean Commit A, run `qhops gate-seal`; the manifest records Commit A as
   `gate_change_set_commit` and binds its exact authority-source/task blobs.
3. Commit B = manifest seal only (plus no unrelated mutation).
4. Authoritative `qh close <Commit B>` verifies this Task.
5. Lifecycle commit remains separate.

Neither Commit A nor Commit B is pushed until authoritative close succeeds; the final
safe push may carry Gate implementation, manifest seal, and lifecycle history together.

## Allowed Changes

- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`
- `ops/qhops/qh_ops.py`
- `ops/qhops/README.md`
- `ops/qhops/autonomous_queue_manifest.json`
- `ops/qhops/tests/test_qh_ops.py`
- `ops/qhops/tests/test_autonomous_queue.py`
- `docs/AUTONOMOUS_QUEUE_GATE_EVIDENCE.md`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-GATE-001.md`
- `tasks/QH-V2-HARD-006.md`
- `tasks/QH-V2-HARD-007.md`
- `tasks/QH-V2-OPS-001.md`
- `tasks/QH-V2-OPS-002.md`
- `tasks/QH-V2-OPS-003.md`
- `tasks/QH-V2-OPS-004.md`
- `tasks/QH-V2-OPS-005.md`
- `tasks/QH-V2-OPS-006.md`
- `tasks/QH-V2-M2-SPEC-001.md`

## Forbidden Changes

- `PROJECT.md`
- `tools/**`
- `tests/**`
- `src/**`
- WorkerRequest / WorkerResponse / ToolSpec / ToolRequest / ToolResult / WorkerStep contracts
- Runner or Retry semantics
- Qwen/Ollama model policy
- Harness Core scope, Verification, Evidence, or Final Gate semantics
- covered queue insertion/removal/reorder
- any authority-bearing change to the nine covered Task contracts other than their
  exact pre-start Status transition
- force push, history rewrite, destructive recovery, credential storage
- Globalization authorization or any Milestone 2 implementation

All unlisted Repository paths remain default-denied.

## Acceptance Criteria

1. `REQUIREMENTS.md` preserves FR-004 for the Qwen Worker and adds a narrow optional
   external Supervisor requirement bound to an exact Human-approved manifest.
2. `DECISIONS.md` contains one Accepted Gate decision that narrowly supersedes only
   repeated Human start/implementation-commit/close/lifecycle-commit/successor/push
   prompts for the exact valid manifest and preserves ADR-008 unchanged.
3. BACKLOG records `G1 POLICY = ACCEPTED` but states execution is enabled only after
   this Task is COMPLETE - VERIFIED and the sealed manifest passes `gate-check`.
4. The covered queue remains exactly HARD-006 -> HARD-007 -> OPS-001 -> OPS-002 ->
   OPS-003 -> OPS-004 -> OPS-005 -> OPS-006 -> M2-SPEC-001 -> HUMAN ARCHITECTURE GATE.
5. All nine covered Tasks are exactly `APPROVED - READY FOR CONTRACT BASELINE` before
   sealing, and baseline comparison proves no other byte in those files changed.
6. `gate-seal` produces a deterministic manifest bound to Commit A, exact authority
   blobs, exact Task pre-start blobs, exact immutable-section hashes, branch/remote,
   allowed operations, validity/revocation policy, and Human Gate Evidence.
7. `gate-check` passes for the exact sealed state and fails closed for at least:
   manifest tamper, BACKLOG tamper, covered Task immutable-section tamper, wrong queue,
   wrong branch, wrong remote/branch, dirty/invalid lifecycle state where required,
   unapproved pending Task, revoked approval, and expired/completed Gate validity.
8. A Status-only covered Task lifecycle transition may remain valid when its immutable
   hash is unchanged; an immutable-section change always STOPs.
9. Supervisor start selects only the exact next manifest Task, refuses PLANNED/DRAFT,
   never promotes Task status, and preserves one-ACTIVE/clean-state rules.
10. Supervisor implementation commit preserves Task scope checks, focused GREEN only,
    local commit separation, and no early push.
11. Supervisor finish calls authoritative `qh close <exact HEAD>` once, requires PASS,
    creates lifecycle commit separately, and uses only existing safe fast-forward push
    to `origin/main`.
12. Failed Supervisor start/commit/finish or gate validation does not skip to a successor,
    force recovery, or push invalid state.
13. The Human Architecture Gate after M2-SPEC-001 always STOPs; no successor Task can
    be generated, approved, or started.
14. Qwen/Worker authority, Harness Core authority, Retry policy, model policy, and
    Globalization state are unchanged.
15. Gate seal is two-phase: manifest records Commit A and Commit B contains the seal;
    no self-referential commit identity is invented.
16. Final Task-range changes contain only Allowed Changes; the nine future contracts
    differ from baseline only in the exact Status value.
17. Exact Commit B is used by authoritative close; Verification exits 0, Unexpected
    Changed Paths is no, Diff Check is 0, and Final Gate is PASS.
18. Final lifecycle commit is separate, final working tree is clean, and final push is
    fast-forward-only to `origin/main`.

## Verification

Run exactly:

`python -m unittest discover -s ops/qhops/tests -p "test_autonomous_queue.py"`

Then run:

`python -m unittest discover -s ops/qhops/tests -p "test_qh_ops.py"`

Then run:

`python -m py_compile ops/qhops/qh_ops.py`

Then run:

`python ops/qhops/qh_ops.py --repo . gate-check`

Then run:

`python -c "from pathlib import Path; import re; ids=('QH-V2-HARD-006','QH-V2-HARD-007','QH-V2-OPS-001','QH-V2-OPS-002','QH-V2-OPS-003','QH-V2-OPS-004','QH-V2-OPS-005','QH-V2-OPS-006','QH-V2-M2-SPEC-001'); expected='APPROVED - READY FOR CONTRACT BASELINE'; heading='##'+' Status'; assert all(re.search(r'(?m)^'+re.escape(heading)+r'\s*\n\s*'+re.escape(expected)+r'\s*$', Path('tasks', f'{x}.md').read_text(encoding='utf-8')) for x in ids)"`

Then run:

`python -c "from pathlib import Path; r=Path('REQUIREMENTS.md').read_text(encoding='utf-8'); d=Path('DECISIONS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); assert 'optional external Codex CLI Supervisor' in r; assert 'HUMAN ONE-TIME AUTONOMOUS QUEUE GATE' in d; assert 'G1 POLICY = ACCEPTED' in b"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Record the Human Gate decision as ACCEPTED and the exact delegated/forbidden
  operation set in `docs/AUTONOMOUS_QUEUE_GATE_EVIDENCE.md`.
- Record Commit A and Commit B, manifest SHA-256, authority-source Git blob identities,
  each covered Task pre-start Git blob identity, and each immutable-section SHA-256.
- Baseline comparison proves the nine covered Task contracts changed only in Status.
- Focused RED demonstrates current qhops lacks manifest validation/guarded Supervisor
  operations before implementation.
- GREEN tests cover gate-seal/check and all required fail-closed tamper cases.
- Failure-path tests prove no automatic approval, skip, force push, history rewrite,
  Architecture mutation, or successor after failure.
- `gate-check` PASS on exact Commit B state is required before close.
- qh close remains the only authoritative final full Verification/Final Gate path.
- Final Git history shows Gate Change Set, manifest seal, and lifecycle completion as
  distinguishable commits; final working tree is clean.

## Stop Conditions

STOP and report `DESIGN CHANGE REQUIRED` if:

- deterministic immutable-section hashing cannot be made unambiguous;
- covered Task authority sections must change to make the queue work;
- queue order must change;
- Harness Core/Final Gate/Verification/ChangeScope semantics must change;
- Qwen/Worker authority must expand;
- a new general shell/Git/destructive authority is required;
- safe fast-forward-only push cannot be enforced;
- manifest validation would rely on Chat/Codex memory rather than Repository/Git state;
- credentials or secrets would need to be stored;
- the M2 Human Architecture Gate would be bypassed.

Do not start QH-V2-HARD-006 until this Task is COMPLETE - VERIFIED and the sealed
manifest passes deterministic validation.

## Next Task

QH-V2-HARD-006, but only through the manifest-guarded Codex Supervisor path after
QH-V2-GATE-001 COMPLETE - VERIFIED and `gate-check` PASS.
