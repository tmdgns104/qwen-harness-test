# QH-V2-LIFECYCLE-001 - Evidence-Backed Unsuccessful Task Closure

## Status

PLANNED

## Problem

The current Task lifecycle has only a durable successful terminal path. `qh start`
requires the Current Task to be exactly `COMPLETE - VERIFIED`, and `qh close` always
runs the successful Verification / Final Gate path before writing that successful
state.

QH-V2-WORKER-ROB-001 produced objective Stable-versus-Candidate Evidence but no
promotable Candidate. Keeping that Task ACTIVE forever blocks the queue, while marking
it `COMPLETE - VERIFIED` would falsely report success.

ADR-015 therefore accepts a separate Evidence-backed unsuccessful terminal state and
one Human-authorized bootstrap transition. Durable support must now be implemented so
a future failed experiment can close truthfully without another manual lifecycle
exception.

## Goal

Add a deterministic, Human-invoked unsuccessful-close lifecycle path that records
`CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`, requires a committed Repository Evidence
artifact, preserves successful `qh close` semantics unchanged, and allows a later
Human-approved Task to start from either legitimate terminal state.

## Architecture Basis

- ADR-015 accepts `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` as a distinct non-success
  terminal lifecycle state and authorizes this implementation Task.
- `COMPLETE - VERIFIED` remains the only successful completion state.
- ADR-001 keeps mechanically decidable lifecycle behavior in deterministic Python.
- ADR-005 and ADR-006 preserve Human-invoked lifecycle authority and forbid automatic
  successor start.
- ADR-008 and ADR-009 keep Worker, tool, Runner, and Retry authority unchanged.
- ADR-014 multi-tool SAFETY behavior remains unchanged.
- The one-time QH-V2-WORKER-ROB-001 bootstrap is Architecture Evidence, not a reusable
  manual lifecycle procedure after this Task is implemented.

## Dependencies

- QH-V2-HARD-008 is COMPLETE - VERIFIED.
- QH-V2-WORKER-ROB-001 has objective non-promotion Evidence and is the ADR-015
  one-time bootstrap case.
- ADR-015 is Accepted before this Task implementation begins.
- The Human-authorized bootstrap must make this Task ACTIVE with a clean baseline
  before implementation.

## Scope

- Add a deterministic unsuccessful-close command to `tools/qh.py`.
- The command is valid only while exactly one Current Task is ACTIVE.
- Require an explicit Repository-relative Evidence file argument.
- Require the Evidence file to exist, remain inside the Repository, be a regular file,
  and be tracked in the exact current HEAD before lifecycle mutation.
- Reject lifecycle-control files themselves as the Evidence artifact.
- Require a clean working tree before unsuccessful closure so the recorded Evidence and
  lifecycle predecessor state are reviewable and committed.
- On success, change the Current Task lifecycle to
  `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` while persistently recording the Evidence
  path in `STATUS.md`.
- Change the current Task document `## Status` to exactly
  `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`.
- Do not run successful Verification / Final Gate and do not claim PASS.
- Extend `qh start` only enough to accept either an exact successful terminal Current
  Task or the new exact unsuccessful terminal Current Task as a legitimate predecessor.
- Preserve the entire predecessor result, including unsuccessful Evidence path, in
  `Previous Task` when a later Human-approved Task is started.
- Keep normal target-task approval checks, baseline recording, one-ACTIVE invariant,
  and no-automatic-successor behavior unchanged.
- Inspect qhops compatibility. `qhops activate` may rely on the broadened legitimate
  predecessor parsing through `qh start`; do not add a new qhops command unless tests
  prove it is required for correctness.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `ops/qhops/tests/test_qh_ops.py`
- `STATUS.md`
- `tasks/QH-V2-LIFECYCLE-001.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/task_runner.py`
- `tools/retry_runner.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `ops/qhops/qh_ops.py`
- `ops/qhops/autonomous_queue_manifest.json`
- `DECISIONS.md`
- `REQUIREMENTS.md`
- `PROJECT.md`
- `BACKLOG.md`
- all Worker/model/backend/prompt policy files not explicitly allowed above

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. A Human-invoked unsuccessful-close command exists and requires an explicit Evidence
   path argument.
2. The command succeeds only when Current Task is exactly ACTIVE and the working tree is
   clean before mutation.
3. The Evidence path must be Repository-relative, resolve inside the Repository, exist
   as a regular file, and be tracked in exact current HEAD.
4. `STATUS.md`, the current Task document, or another lifecycle-control file cannot be
   used as the Evidence artifact.
5. Missing, absolute, escaping, untracked, directory, or lifecycle-control Evidence
   paths fail non-zero with byte-for-byte zero mutation of `STATUS.md` and the current
   Task document.
6. Successful unsuccessful closure writes the Task document Status exactly as
   `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`.
7. Successful unsuccessful closure writes a deterministic Current Task line containing
   the same terminal state plus the Repository-relative Evidence path, so the Evidence
   reference persists in Source of Truth.
8. Unsuccessful closure does not run or claim successful Verification, Final Gate PASS,
   or successful implementation completion.
9. Existing successful `qh close <HEAD>` behavior and `COMPLETE - VERIFIED` semantics
   remain unchanged.
10. `qh start` accepts a predecessor that is either exact `COMPLETE - VERIFIED` or exact
    `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` with a valid persisted Evidence path.
11. Starting after unsuccessful closure preserves that predecessor state and Evidence
    path in `Previous Task`, makes only the explicitly requested approved target ACTIVE,
    records the pre-start HEAD as Task Baseline, and clears the consumed Next pointer.
12. Malformed unsuccessful terminal lines or missing/invalid persisted Evidence paths
    fail closed before start mutation.
13. `qhops activate` remains compatible through the normal `qh start` path without
    changing `ops/qhops/qh_ops.py`; a focused qhops regression proves this if needed.
14. No Worker, Runner, Retry, Repository-tool, model-routing, step-budget, Verification,
    Evidence-gate, Final Gate, Git authority, or automatic successor behavior changes.

## Verification

Run exactly:

`python -m unittest tests.test_qh.QhUnsuccessfulLifecycleTests`

Then run:

`python -m unittest tests.test_qh.QhLifecycleStartGuardTests`

Then run:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest ops.qhops.tests.test_qh_ops`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Focused RED first proves the missing unsuccessful-close command/state and inability to
  start from an evidence-backed unsuccessful predecessor.
- Focused GREEN records test count and exit 0.
- Rejection cases compare exact pre/post bytes for `STATUS.md` and the current Task
  document to prove zero mutation.
- A successful fixture records the exact Evidence path in STATUS and the exact terminal
  Task Status without any Final Gate PASS claim.
- Existing successful close regression remains PASS.
- Existing lifecycle start guard regression remains PASS.
- qhops compatibility regression remains PASS without production qhops changes.
- Full `tests.test_qh` regression passes.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Exact implementation HEAD is used by the normal successful close of
  QH-V2-LIFECYCLE-001 itself.
- Final close output for QH-V2-LIFECYCLE-001 shows all Verification commands exit 0,
  no unexpected paths, Diff Check 0, and Final Gate PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP for Human Architecture review if implementation requires:

- treating unsuccessful closure as PASS or `COMPLETE - VERIFIED`;
- weakening successful `qh close`, Verification, Evidence, or Final Gate semantics;
- allowing closure without a committed Evidence artifact;
- automatically choosing or starting a successor Task;
- changing Worker, Runner, Retry, Repository tools, model routing, or step budget;
- changing qhops production authority or autonomous-queue policy;
- adding general shell, Git, network, filesystem, lifecycle, or Architecture authority;
- changing ADR-015 or another Accepted Architecture decision.

## Next Task

Human selection required after this Task is COMPLETE - VERIFIED.

QH-V2-OPS-003 remains deferred until the Human decides whether Worker investigation
must occur first. Do not auto-start either path.
