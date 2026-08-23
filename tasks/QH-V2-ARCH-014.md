# QH-V2-ARCH-014 - Cross-Repository Trial Hardening Reprioritization

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

The first real cross-Repository trial in `ai_data_analyst` exposed two failures that
were not covered by the in-Repository Milestone 1 E2E Evidence:

1. `python tools\qh.py run TASK-001` can fail in an external-style Repository with
   `ModuleNotFoundError: No module named 'tools'` unless the operator manually adjusts
   `PYTHONPATH`.
2. After that workaround, real `qwen3:8b` produced multiple ToolRequests in one
   WorkerStep twice consecutively. The deterministic Runner correctly failed closed
   with `SAFETY` and zero Repository mutation, but the Worker interaction could not
   make useful progress.

The failures are recorded in GitHub Issue #1. They are new objective Evidence under
ADR-010 and justify reviewing queue priority before continuing convenience work.

The current queue still nominates QH-V2-OPS-003 next, while ADR-011 explicitly keeps
`GLOBALIZATION = NOT AUTHORIZED`. The Repository needs one explicit decision that
separates immediate hardening from later formal Globalization approval.

## Goal

Record a Human-approved decision and queue update that:

- treats GitHub Issue #1 as new cross-Repository trial Evidence;
- inserts runtime portability hardening and Worker single-tool protocol robustness
  before QH-V2-OPS-003;
- preserves the existing fail-closed multi-ToolRequest safety boundary;
- keeps formal cross-Repository Globalization unauthorized until the existing
  ADR-011 Globalization prerequisites and a separate Human Globalization Gate are met;
- creates bounded implementation Task contracts for the two hardening items without
  implementing either one in this Task.

## Architecture Basis

- ADR-001 keeps deterministic Harness Evidence authoritative over LLM self-report.
- ADR-002 uses native Ollama + Qwen3:8B while preserving fail-closed safety.
- ADR-008 defines the backend-neutral Tool interaction boundary.
- ADR-009 classifies multiple ToolRequests in one WorkerStep as deterministic FAIL.
- ADR-010 allows reprioritization when new objective Evidence justifies it.
- ADR-011 records the long-term Global Harness strategy and explicitly states
  `GLOBALIZATION = NOT AUTHORIZED` until a separate Human Globalization Gate.
- GitHub Issue #1 records the external Repository import-portability failure and the
  reproduced multi-ToolRequest SAFETY failure with zero mutation.

## Dependencies

- QH-V2-OPS-002 is COMPLETE - VERIFIED.
- GitHub Issue #1 remains open Evidence and does not by itself authorize code changes.
- Current `main` is synchronized through the OPS-002 documentation refresh.
- Human explicitly approved preparing this reprioritization before implementation.

## Scope

- Add one Accepted ADR documenting the cross-Repository trial findings and queue
  reprioritization.
- Update `BACKLOG.md` so the deterministic candidate order becomes:
  QH-V2-HARD-008 -> QH-V2-WORKER-ROB-001 -> QH-V2-OPS-003 -> QH-V2-OPS-004 ->
  existing remaining queue.
- Keep QH-V2-OPS-003 and later existing Task behavioral contracts unchanged except
  dependency/queue-link text that must reflect the inserted predecessors.
- Create `tasks/QH-V2-HARD-008.md` for runtime/import portability hardening.
- Create `tasks/QH-V2-WORKER-ROB-001.md` for Qwen single-tool interaction robustness.
- Record that formal Globalization remains unauthorized and that `ai_data_analyst`
  remains trial Evidence rather than proof of supported global execution.
- Do not change production Harness code, tests, Requirements, Worker authority,
  Runner multi-tool behavior, retry behavior, model choice, or step budget here.

## Required ADR-014 Decision Content

ADR-014 must state all of the following:

1. GitHub Issue #1 is authoritative new operational Evidence for planning purposes.
2. The import-path problem is a portability/runtime defect and is handled first by
   QH-V2-HARD-008.
3. The repeated multi-ToolRequest behavior is a Worker interaction robustness problem
   and is handled second by QH-V2-WORKER-ROB-001.
4. Existing `zero or one ToolRequest per WorkerStep` enforcement remains authoritative;
   multiple ToolRequests still fail closed and are not silently split, repaired, or
   executed.
5. WORKER-ROB-001 may strengthen Worker instructions/context inside the existing Trust
   Boundary, but any change that turns a multi-tool violation into continuation/retry,
   changes retry classification, expands Worker authority, or changes Final Gate
   authority requires a separate Human Architecture review.
6. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged. Trial fixes do not themselves
   authorize stable cross-Repository use.
7. ADR-011 Globalization prerequisites remain in force, including OPS-004 and a later
   explicit Human Globalization Gate.
8. OPS-003 is deferred, not cancelled; it resumes after the two evidence-driven
   hardening Tasks complete.

## QH-V2-HARD-008 Contract Requirements

The generated Task must be narrowly limited to runtime portability and diagnostics.
It must require at least:

- one supported internal import strategy for the existing Repository-copied runtime;
- no operator-set `PYTHONPATH` requirement for the documented `python tools\qh.py ...`
  entry path;
- a focused external-style Repository regression that exercises the real `run` import
  chain without live Ollama;
- `qh doctor` readiness coverage for the delayed Worker/run import path so doctor cannot
  report overall readiness while the documented run entry path is structurally broken;
- no packaging/global-install redesign, no new Worker authority, and no model/prompt
  behavior change;
- focused RED -> GREEN Evidence followed by the Task's final authoritative close.

## QH-V2-WORKER-ROB-001 Contract Requirements

The generated Task must preserve deterministic safety and require at least:

- explicit Worker protocol instructing Qwen to request at most one Tool per turn,
  stop after requesting it, wait for ToolResult, then decide the next action;
- existing Runner behavior that multiple ToolRequests in one WorkerStep remain
  deterministic SAFETY FAIL with no Tool execution from that invalid step;
- deterministic/mock tests proving the safety boundary is unchanged;
- representative sequential multi-step read/write interaction tests;
- Stable-versus-Candidate real `qwen3:8b` Evidence on a small representative Task,
  recording NORMAL, multi-tool SAFETY, STEP_BUDGET, and other outcomes;
- no automatic splitting/execution of multiple ToolRequests;
- no general shell/Git authority, retry-policy change, model-routing change, or step
  budget increase;
- STOP and Human Architecture review if useful robustness requires changing the
  multi-tool failure semantics or another accepted Trust Boundary.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-014.md`
- `tasks/QH-V2-HARD-008.md`
- `tasks/QH-V2-WORKER-ROB-001.md`
- `tasks/QH-V2-OPS-003.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `README.md`
- `docs/**`
- `tools/**`
- `tests/**`
- `qh.cmd`

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. `DECISIONS.md` contains Accepted ADR-014 with every Required ADR-014 Decision Content
   item above and does not claim Globalization approval.
2. `BACKLOG.md` deterministically nominates HARD-008 before WORKER-ROB-001 and both
   before OPS-003, while preserving the remaining existing queue order.
3. OPS-003 remains planned/approved work rather than being deleted or behaviorally
   redesigned; only dependency/queue-link text needed by reprioritization may change.
4. `tasks/QH-V2-HARD-008.md` exists with Goal, Scope, Allowed Changes, Forbidden Changes,
   Acceptance Criteria, Verification, Evidence Requirements, Stop Conditions, and
   Next Task sections satisfying its contract requirements.
5. `tasks/QH-V2-WORKER-ROB-001.md` exists with the same complete Task-contract structure
   and explicitly preserves deterministic multi-tool SAFETY failure semantics.
6. Neither new implementation Task authorizes formal Globalization, general shell/Git
   authority, automatic multi-tool execution, automatic architecture changes, or
   Final Gate weakening.
7. The implementation Tasks are marked `APPROVED - READY FOR CONTRACT BASELINE` only
   because the Human approved this exact plan; they are not ACTIVE and are not
   automatically started.
8. `STATUS.md` continues to show no ACTIVE implementation Task after this planning Task
   completes and nominates QH-V2-HARD-008 as the next Human-controlled candidate.
9. No production Harness code, tests, Requirements, or unrelated documentation changes.
10. `git diff --check` passes and all changed paths are inside this Task's Allowed Changes.

## Verification

Run exactly:

`python -c "from pathlib import Path; s=Path('DECISIONS.md').read_text(encoding='utf-8'); required=('ADR-014','Issue #1','QH-V2-HARD-008','QH-V2-WORKER-ROB-001','zero or one ToolRequest','GLOBALIZATION = NOT AUTHORIZED','QH-V2-OPS-003'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('BACKLOG.md').read_text(encoding='utf-8'); a=s.index('QH-V2-HARD-008'); b=s.index('QH-V2-WORKER-ROB-001'); c=s.index('QH-V2-OPS-003'); assert a < b < c"`

Then run:

`python -c "from pathlib import Path; files=('tasks/QH-V2-HARD-008.md','tasks/QH-V2-WORKER-ROB-001.md'); required=('## Status','APPROVED - READY FOR CONTRACT BASELINE','## Goal','## Scope','## Allowed Changes','## Forbidden Changes','## Acceptance Criteria','## Verification','## Evidence Requirements','## Stop Conditions','## Next Task'); assert all(Path(f).is_file() and all(x in Path(f).read_text(encoding='utf-8') for x in required) for f in files)"`

Then run:

`python -c "from pathlib import Path; s=Path('tasks/QH-V2-WORKER-ROB-001.md').read_text(encoding='utf-8'); required=('at most one','SAFETY','no Tool execution','Stable','Candidate'); assert all(x in s for x in required)"`

Then run:

`python -m unittest tests.test_harness_core.VerificationCommandContractTests`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Issue #1 failure facts are reflected without treating the issue itself as implementation
  authority.
- Diff shows only the allowed planning, queue, lifecycle, and Task-contract files.
- ADR-014 clearly distinguishes defect hardening, Worker policy robustness, and later
  Globalization approval.
- HARD-008 and WORKER-ROB-001 are bounded implementation contracts, not code changes.
- Existing multi-tool fail-closed semantics are explicitly preserved.
- ChangeScope and Verification parser accept this Task contract.
- Exact planning implementation HEAD is used by Human-invoked `qh close`; all marked
  Verification commands exit 0, Unexpected Changed Paths is no, Diff Check is 0, and
  Final Gate is PASS.
- Lifecycle commit is separate and final working tree is clean.

## Stop Conditions

STOP and report `DESIGN CHANGE REQUIRED` if:

- the plan requires changing `PROJECT.md` or `REQUIREMENTS.md`;
- formal Globalization would need to be approved now;
- existing multi-ToolRequest SAFETY semantics must change in this planning Task;
- a code/test fix is attempted before its implementation Task becomes ACTIVE;
- Worker shell/Git/network authority, Final Gate authority, retry policy, model routing,
  or step budget would expand;
- the remaining OPS queue cannot be preserved after the two inserted Tasks;
- any production or test file needs modification.

## Next Task

QH-V2-HARD-008 - Human-controlled candidate only. Do not auto-start.
