# QH-V2-PLAN-001 - Post-Lifecycle Queue Reconciliation

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

Repository Source of Truth is not fully consistent after QH-V2-WORKER-ROB-001 and QH-V2-LIFECYCLE-001.

- ADR-014 originally placed QH-V2-OPS-003 after a successful Worker robustness stage.
- QH-V2-WORKER-ROB-001 instead ended as `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED` under ADR-015.
- ADR-015 explicitly requires a later Human decision before either separate Worker investigation or resumption of QH-V2-OPS-003.
- BACKLOG already acknowledges that Human selection boundary, but `tasks/QH-V2-OPS-003.md` still requires QH-V2-WORKER-ROB-001 to be `COMPLETE - VERIFIED`, which can never become true without falsifying the recorded non-success outcome.
- New runtime Evidence from QH-V2-LIFECYCLE-001 execution also showed intermittent 30-second Qwen/Ollama timeouts for the full Task prompt while short requests remained stable.

The Human has now selected the Evidence-first path: perform a dedicated Worker diagnosis before resuming the operations queue.

## Goal

Reconcile DECISIONS, BACKLOG, and the deferred QH-V2-OPS-003 dependency so the Repository truthfully records this Human-selected sequence:

`QH-V2-PLAN-001 -> QH-V2-WORKER-DIAG-001 -> conditional QH-V2-WORKER-ROB-002 -> QH-V2-OPS-003 -> QH-V2-OPS-004 -> QH-V2-OPS-005 -> QH-V2-OPS-006 -> QH-V2-M2-SPEC-001 -> HUMAN ARCHITECTURE GATE`

This Task is planning/state reconciliation only. It does not diagnose or modify Worker behavior.

## Architecture Basis

- ADR-014 remains historical authority for why HARD-008 and Worker robustness work were inserted before OPS-003.
- ADR-015 remains authoritative for the truthful unsuccessful terminal state and the Human-selection boundary after LIFECYCLE-001.
- QH-V2-LIFECYCLE-001 is COMPLETE - VERIFIED and durable unsuccessful-close support is implemented.
- QH-V2-STATUS-001 is COMPLETE - VERIFIED and removed the stale ACTIVE handoff wording.
- The Human explicitly selected Worker diagnosis before OPS-003 after reviewing the current Repository state and recent timeout Evidence.
- No Worker, Runner, Retry, tool, model, lifecycle, Verification, Final Gate, or Trust Boundary authority changes are authorized by this planning Task.

## Scope

- Record a new Accepted decision clarifying the post-LIFECYCLE-001 sequence and the Human-selected Worker diagnostic priority.
- Update BACKLOG queue/dependency text so QH-V2-WORKER-DIAG-001 is the next candidate before OPS-003.
- Record that QH-V2-WORKER-ROB-002 is conditional and may be created only if diagnostic Evidence justifies an implementation fix.
- Correct QH-V2-OPS-003 dependencies so they no longer require the impossible condition that QH-V2-WORKER-ROB-001 become `COMPLETE - VERIFIED`.
- Preserve QH-V2-WORKER-ROB-001 exactly as `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`.
- Keep QH-V2-OPS-003 deferred until the diagnostic path reaches a Human-reviewed disposition.
- Do not create, start, diagnose, or implement QH-V2-WORKER-DIAG-001 in this Task.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `tasks/QH-V2-OPS-003.md`
- `STATUS.md`
- `tasks/QH-V2-PLAN-001.md`

## Forbidden Changes

- all production code
- all tests
- all Worker/model/backend/prompt files
- `PROJECT.md`
- `REQUIREMENTS.md`
- all other Task files
- `ops/qhops/**`
- Worker, Runner, Retry, Repository-tool, Verification, Final Gate, lifecycle, Git, or automatic-successor behavior

All paths not listed under Allowed Changes remain default-denied.

## Acceptance Criteria

1. DECISIONS records an Accepted post-lifecycle queue decision that explicitly selects Worker diagnosis before OPS-003 and preserves ADR-015 unsuccessful-state semantics.
2. BACKLOG names QH-V2-WORKER-DIAG-001 as the next candidate after this planning Task.
3. BACKLOG records QH-V2-WORKER-ROB-002 as conditional, not automatically required or authorized.
4. The remaining operations order stays `OPS-003 -> OPS-004 -> OPS-005 -> OPS-006 -> M2-SPEC-001 -> HUMAN ARCHITECTURE GATE` after the Worker diagnostic path.
5. `tasks/QH-V2-OPS-003.md` no longer requires QH-V2-WORKER-ROB-001 to be `COMPLETE - VERIFIED`.
6. OPS-003 instead requires completion of QH-V2-LIFECYCLE-001 plus a Human-reviewed conclusion of the Worker diagnostic path before activation.
7. QH-V2-WORKER-ROB-001 remains recorded only as `CLOSED - UNSUCCESSFUL - EVIDENCE RECORDED`; no file claims it succeeded.
8. No Worker diagnostic or Worker implementation code is added in this Task.
9. No Architecture or Trust Boundary authority is expanded; the new decision is sequencing/diagnostic-priority clarification only.
10. No successor is automatically started after this Task closes.

## Verification

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); o=Path('tasks/QH-V2-OPS-003.md').read_text(encoding='utf-8'); assert 'ADR-016 - Post-Lifecycle Worker Diagnosis Before Operations Resume' in d; assert 'QH-V2-WORKER-DIAG-001' in b; assert 'QH-V2-WORKER-ROB-002' in b; assert 'QH-V2-WORKER-ROB-001 must be COMPLETE - VERIFIED' not in o; assert 'QH-V2-LIFECYCLE-001' in o and 'QH-V2-WORKER-DIAG-001' in o"`

Then run:

`python -c "from pathlib import Path; s=Path('STATUS.md').read_text(encoding='utf-8'); assert 'Current Task: QH-V2-PLAN-001 - ACTIVE' in s; assert 'Previous Task: QH-V2-STATUS-001 - COMPLETE - VERIFIED - commit 5f315f5127ed6b8778a3861ae4a93b28fe7fa98f' in s"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- Show the exact DECISIONS/BACKLOG/OPS-003 diff.
- Verification commands exit 0.
- Baseline-to-implementation changed paths contain only Allowed Changes.
- Review proves WORKER-ROB-001 remains unsuccessful and is not rewritten as successful completion.
- Exact implementation HEAD is used by normal `qh close`; Final Gate PASS is required.
- Lifecycle close commit is separate and final working tree is clean.
- After completion, stop at Human Gate; QH-V2-WORKER-DIAG-001 is nominated but not automatically created or started.

## Stop Conditions

STOP if reconciliation requires:

- changing Worker, Runner, Retry, model, tool, Verification, Final Gate, lifecycle, or Git implementation;
- converting WORKER-ROB-001 into a successful completion;
- automatically creating or starting Worker diagnostic/repair implementation work;
- expanding shell, network, filesystem, Git, model-routing, or multi-agent authority;
- modifying PROJECT or REQUIREMENTS;
- changing the Milestone 2 Human Architecture Gate.

## Next Task

Human review required for a separately defined `QH-V2-WORKER-DIAG-001` contract after this Task is COMPLETE - VERIFIED. Do not auto-start it.
