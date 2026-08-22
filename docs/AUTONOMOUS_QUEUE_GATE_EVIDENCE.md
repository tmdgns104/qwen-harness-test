# Autonomous Queue Gate G1 Evidence

## Decision

Human decision: `ACCEPTED` on 2026-08-22.

Parent review: `QH-V2-ARCH-008 - COMPLETE - VERIFIED`.

Materialization Task: `QH-V2-GATE-001`.

This record captures the Human-approved narrow one-time autonomous queue policy.
It is not Final Gate evidence and does not authorize execution by itself.

## Covered Queue

The exact covered order is:

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

No insertion, removal, reordering, or automatic successor beyond the terminal Human
Architecture Gate is approved.

## Delegated Operations

Only after `QH-V2-GATE-001` is COMPLETE - VERIFIED and the sealed manifest passes
deterministic `gate-check`, an optional external Codex CLI Supervisor may:

- start the exact next already-approved covered Task;
- create the Task implementation commit;
- invoke authoritative `qh close <exact implementation HEAD>`;
- create the separate lifecycle commit after Final Gate PASS;
- advance only to the exact manifest successor after revalidation;
- push `HEAD:main` to `origin` using fast-forward-only behavior.

The Supervisor is external to the Qwen Worker. FR-004 continues to constrain the
Worker to one explicitly assigned current Task.

## Always Forbidden

The accepted Gate does not authorize:

- Task creation during autonomous queue execution;
- edits to covered Task immutable contract authority;
- queue insertion, removal, or reordering;
- Architecture or Requirements changes during covered execution;
- Task scope expansion or Forbidden-path bypass;
- force push, rebase, reset/history rewrite, or destructive recovery;
- bypass of Verification, Evidence, Diff Check, or Final Gate;
- expansion of Qwen/Worker filesystem, shell, Git, lifecycle, Verification, commit,
  push, Architecture, or Final PASS authority;
- continuation past the Human Architecture Gate;
- Globalization or Milestone 2 implementation.

## Git / Push Boundary

Approved local branch: `master`.

Approved remote: `origin`.

Approved remote branch: `main`.

Approved push refspec: `HEAD:main`.

Push policy: fast-forward only. Force push and history rewrite are forbidden.

The sealed manifest records a credential-free remote identity. A credential-bearing
remote URL is rejected rather than persisted.

## Two-Phase Seal

1. Commit A is the Gate Change Set: accepted Requirement/Decision/BACKLOG overlay,
   exact future-Task pre-approvals, qhops guard implementation/tests, and this Evidence.
2. From clean Commit A, `gate-seal` records Commit A and exact Git blob / immutable
   contract identities in `ops/qhops/autonomous_queue_manifest.json`.
3. Commit B contains the manifest seal.
4. Exact Commit B is passed to authoritative `qh close`.
5. The lifecycle commit is separate.
6. The final safe push may carry Commit A, Commit B, and lifecycle history together.

The manifest SHA-256 and local Commit A identity are emitted by `gate-seal`. Commit B
is the exact implementation HEAD used by `qh close`; Git history and close output are
the authoritative record of those identities.

## Resume / Audit

Authoritative resume state is Repository Git state plus the exact sealed manifest.
Chat history and Codex session memory are not resume authority.

A supplemental user-local audit may be written under `%USERPROFILE%\.qhops\audit\`,
but it is never completion authority.

## Activation State

`G1 POLICY = ACCEPTED`.

Autonomous queue execution remains disabled until all of the following are true:

- QH-V2-GATE-001 is COMPLETE - VERIFIED;
- the exact manifest is committed;
- `gate-check` passes against the current Repository/Git state.

Any manifest, queue, immutable-section, branch, remote, lifecycle, authority-source,
scope, revocation, or approval mismatch requires deterministic STOP.
