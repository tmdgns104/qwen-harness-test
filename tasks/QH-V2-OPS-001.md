# QH-V2-OPS-001 - Human-Approved Task Scaffold

## Status

PLANNED

## Problem

Creating every Task contract by hand repeats the same required headings and makes
missing scope, malformed Verification markers, and lifecycle confusion more likely.
The current flat qh CLI has no Task-draft command, but automation must not invent or
approve Goal, Architecture, scope, or Verification on the Human's behalf.

## Goal

Add a minimal `task-new <TASK-ID>` command that exclusively creates a clearly
unapproved Task draft with the required structure and never approves, starts,
commits, or closes it.

## Architecture Basis

- ADR-003 favors simple deterministic CLI utilities.
- ADR-005 keeps Task assignment and lifecycle transitions under Human control.
- ADR-006 identifies a Task scaffold as an operations candidate while requiring
  every implementation to retain its own approved Task and Human Gate.
- ADR-010 lists Human-approved Task scaffolding as NEXT-HARDENING work.
- The current CLI uses a flat command parser, so a flat command avoids an unrelated
  nested-parser redesign.

## Dependencies

- QH-V2-HARD-007 must be COMPLETE - VERIFIED in the deterministic queue.
- QH-V2-HARD-002 supplies the fail-closed Verification-contract parser baseline.
- QH-V2-HARD-003 supplies the lifecycle guard this draft tool must not bypass.
- Until committed Requirement/Accepted Decision updates and the Human-approved G1
  manifest cover this exact unchanged Task and queue blob identity, explicit Human
  approval is required before activation.

## Scope

- Add the exact flat command `task-new <TASK-ID>` to qh.
- Validate a conservative Task ID and map it to one file under `tasks/`.
- Exclusively create a deterministic UTF-8 draft containing all required headings.
- Mark the file `DRAFT - HUMAN REVIEW REQUIRED` so it cannot be confused with PLANNED,
  approved, ACTIVE, or COMPLETE state.
- Leave Goal, Architecture Basis, scope, Acceptance Criteria, and Verification as
  explicit Human-review placeholders rather than inferred authority.
- Document the draft/review/start boundary for beginners.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh_task_scaffold.py`
- `tests/test_qh.py`
- `README.md`
- `docs/QUICKSTART.md`
- `docs/DEVELOPMENT.md`
- `STATUS.md`
- `tasks/QH-V2-OPS-001.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. `task-new <valid-ID>` creates exactly `tasks/<valid-ID>.md` and no other file.
2. The draft includes every required contract section in deterministic order,
   UTF-8 encoding, and stable newline form.
3. Status is exactly `DRAFT - HUMAN REVIEW REQUIRED` and the draft explains that
   Human review and approval are still required.
4. The command does not infer or approve Architecture, Allowed/Forbidden scope,
   Acceptance Criteria, or executable Verification commands.
5. An untouched generated draft makes both `parse_change_scope()` and
   `parse_verification_commands()` raise until a Human supplies valid scope and
   explicitly marked commands.
6. After HARD-003, passing the generated DRAFT to `qh start` returns non-zero and
   leaves STATUS and the draft byte-for-byte unchanged.
7. Invalid IDs, traversal-like IDs, and an existing target return non-zero before write.
8. Every failed invocation leaves the Repository and STATUS byte-for-byte unchanged.
9. The command never calls start, run, review, close, Git commit, or Git push.
10. Existing qh commands and parser behavior remain compatible.
11. The documented workflow requires Human review before a separate explicit start.

## Verification

Run exactly:

`python -m unittest tests.test_qh_task_scaffold`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused tests cover valid creation, stable bytes, invalid IDs, exclusive-create
  refusal, traversal refusal, and zero mutation.
- Parser tests prove the untouched draft fails closed in both ChangeScope and
  Verification parsing instead of granting placeholder authority.
- A lifecycle regression proves the generated DRAFT cannot be started and both
  STATUS and target bytes remain unchanged.
- Before/after STATUS and Repository snapshots show the command never changes lifecycle.
- Existing qh and Harness Core regression modules pass.
- Documentation clearly separates draft, Human approval, start, and implementation.
- Baseline-to-implementation changed paths contain only Allowed Changes and no
  generated example Task remains.
- Exact implementation HEAD is used by `qh close`; all Verification commands exit 0,
  no unexpected path is reported, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP if completion requires:

- automatic Architecture, scope, Acceptance Criteria, or Verification approval;
- automatic Task selection, start, commit, close, or push;
- making a draft parse as an approved executable contract;
- broad CLI parser redesign or new lifecycle states outside existing Architecture;
- Harness Core, Worker, Runner, Retry, Adapter, or Repository-tool changes.

## Next Task

Queue successor candidate: QH-V2-OPS-002.

Until committed Requirement/Accepted Decision updates and the Human-approved G1
manifest cover the exact unchanged queue and successor contract blob, Human approval
is required and the successor must not be auto-started.
