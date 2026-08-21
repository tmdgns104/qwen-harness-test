# QH-V2-OPS-003A - Codex / qhops Handoff Integration

## Status

PLANNED

## Problem

When Codex CLI becomes available again, a fresh Codex session should not depend on
chat history or Human memory to discover the installed `qhops` operations helper,
its role, or the current Repository workflow. The Repository is the Source of Truth,
but today there is no tracked Codex-facing operating note and no standardized
machine-readable/current-state handoff command for `qhops`.

Without a durable handoff, Codex may duplicate lifecycle commands manually, ignore
`qhops`, or require the Human to re-explain the current operating workflow.

## Goal

Make the existence and intended use of `qhops` discoverable to a fresh Codex session
from Repository-grounded instructions, and standardize a concise `qhops codex-context`
output that reports the current Task and operational boundaries without granting new
authority.

## Architecture Basis

- Repository documents and Git remain the Source of Truth; chat history is not
  authoritative project state.
- Codex remains an optional external executor/supervisor path and must not become a
  requirement for Harness/Qwen operation.
- `qhops` is an operations convenience layer around deterministic Git/Test/qh
  workflows; it does not replace Harness Verification or Final Gate authority.
- Qwen/Worker authority is unchanged and receives no new shell, Git, lifecycle,
  Verification, commit, push, or Architecture authority.
- The change should reduce Human relay work while keeping the current one-Task,
  scoped, evidence-driven workflow understandable and auditable.

## Dependencies

- QH-V2-OPS-003 must be COMPLETE - VERIFIED.
- The Windows workflow should be stable before documenting Codex-facing operational
  entry points.
- QH-V2-OPS-004 remains the successor after this handoff integration Task.
- If `qhops` packaging/location has changed by activation time, this Task must first
  reconcile its documented installation/discovery path with the then-current
  Repository and installed helper; do not assume today's local path.

## Scope

- Add a tracked root `AGENTS.md` containing concise Codex operating instructions for
  this Repository.
- Add `docs/CODEX_HANDOFF.md` describing how a fresh Codex session discovers and uses
  `qhops`, which commands are appropriate, and which Repository documents remain
  authoritative.
- Standardize a `qhops codex-context` command in the then-current qhops distribution
  or integration location. The command should print concise current-state context
  suitable for pasting or direct Codex inspection, including at least Repository,
  current Task, Task file/status, Git HEAD/state, Allowed/Forbidden change scope, and
  recommended next operational command.
- Ensure the context output is read-only and does not start, approve, commit, close,
  push, mutate lifecycle, or infer PASS.
- Document the recommended fresh-session entry sequence, for example reading
  `AGENTS.md`, `STATUS.md`, the current Task, and/or running `qhops codex-context`.
- Keep `qhops` optional; direct qh and Repository workflows remain possible.
- Add tests or deterministic evidence for the context output and zero-mutation
  behavior appropriate to the qhops packaging that exists when the Task is activated.

## Allowed Changes

- `AGENTS.md`
- `docs/CODEX_HANDOFF.md`
- qhops distribution/integration files that are explicitly identified and reviewed
  when this Task is approved
- tests for the qhops Codex-context contract
- `README.md`
- `docs/QUICKSTART.md`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-003A.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- Worker/Qwen authority expansion
- automatic Architecture decisions or Final PASS authority

Before approval, replace the qhops wildcard description above with exact paths based
on the actual distribution location at that time. The approved Task must contain an
exact parseable Allowed Changes contract; this PLANNED draft is not executable yet.

## Acceptance Criteria

1. A fresh Codex session can discover the Repository operating policy without prior
   chat history.
2. `AGENTS.md` explicitly points Codex to Repository Source-of-Truth files, the
   current Task, Allowed/Forbidden scope, objective Test/Git Evidence, and `qhops`.
3. The documented Codex workflow does not treat Codex self-report or Qwen self-report
   as completion Evidence.
4. `qhops codex-context` is read-only and reports concise current Task, Git, scope,
   and recommended workflow context.
5. Running `qhops codex-context` leaves Repository bytes, Git state, lifecycle state,
   remotes, and credentials unchanged.
6. The output does not expose secrets, credential-bearing URLs, tokens, or private
   configuration values.
7. Codex can still work without `qhops` by following the documented direct Repository
   and qh workflow.
8. Harness/Qwen remains usable without Codex.
9. No Worker, Runner, Retry, Adapter, Evidence, Final Gate, or Architecture authority
   changes are introduced.
10. Documentation clearly distinguishes `qhops` convenience automation from
    authoritative `qh close`/Harness Verification.
11. The approved implementation Task uses exact Allowed/Forbidden paths and exact
    Verification commands based on the qhops packaging that exists at activation.

## Verification

PLANNING PLACEHOLDER - HUMAN REVIEW REQUIRED BEFORE APPROVAL.

At activation, define exact deterministic commands that cover:

- `qhops codex-context` output contract;
- zero Repository mutation;
- tracked `AGENTS.md` and `docs/CODEX_HANDOFF.md` required content;
- existing qh/qhops regressions relevant to the final integration;
- `git diff --check`;
- `git status --short`.

This PLANNED Task must not be passed to `qh start` until the placeholder is replaced
with an explicit executable Verification contract and exact qhops paths.

## Evidence Requirements

- Fresh-session instructions are Repository-grounded and do not depend on chat memory.
- A deterministic test proves `qhops codex-context` is read-only and stable enough for
  Codex handoff use.
- Before/after Git and lifecycle snapshots prove zero mutation from context discovery.
- No credential or secret appears in context output.
- Existing qh and relevant qhops regressions pass.
- Exact implementation HEAD is used by authoritative `qh close` after the Task is
  fully specified, approved, and implemented.

## Stop Conditions

STOP if completion requires:

- making Codex mandatory for Harness/Qwen operation;
- granting Codex or qhops unreviewed Architecture, lifecycle, destructive Git, or
  Final PASS authority;
- granting Qwen/Worker additional filesystem, shell, Git, lifecycle, Verification,
  commit, push, or Architecture authority;
- relying on chat history instead of Repository-grounded instructions;
- storing secrets or credentials in Repository handoff material;
- approving the current placeholder scope/Verification without first replacing it
  with exact paths and commands.

## Next Task

Queue successor candidate: QH-V2-OPS-004.

This Task is intended to be inserted after QH-V2-OPS-003 and before QH-V2-OPS-004
through a separate Human-approved backlog planning change. It is not ACTIVE and does
not alter the current HARD-005 execution.