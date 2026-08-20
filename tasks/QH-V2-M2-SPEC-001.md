# QH-V2-M2-SPEC-001 - Milestone 2 Specification and Architecture Review

## Status

PLANNED

## Problem

Milestone 2 capability candidates range from backend-neutral extensions to new
orchestration and broader tool authority. Starting implementation without separating
current-Architecture work, Architecture changes, and Trust Boundary expansion would
bypass the Human Architecture Gate and could invalidate the M1 safety model.

## Goal

Produce a proposal-only Milestone 2 review that classifies every named capability,
surfaces requirements, risks, authority, Evidence gaps, and alternatives, and stops
at a Human Architecture Gate without creating implementation Tasks.

## Architecture Basis

- PROJECT Future Direction permits later capability analysis but does not authorize it.
- FR-004 preserves one explicit Task and forbids automatic next-Task selection.
- FR-002 preserves the default local-Worker direction.
- FR-008 preserves safe failure, and FR-009 keeps Codex optional.
- FR-011 through FR-013 preserve backend-independent Core, Harness-owned tool
  authority, and bounded Retry.
- ADR-001 and ADR-002 separate deterministic Core authority from the local model backend.
- ADR-004 places LangGraph, multi-agent orchestration, and automatic Codex use outside M1.
- ADR-006 requires a Human-approved Task and Human Gate for each implementation.
- ADR-008 through ADR-010 preserve bounded tools, Retry, hardening order, and Human control.

## Dependencies

- QH-V2-OPS-006 and every earlier deterministic queue item must be COMPLETE - VERIFIED.
- This Task is analysis only and still requires explicit Human approval before activation.
- Its output does not approve Architecture or authorize any implementation.

## Scope

- Analyze LangGraph orchestration, Subtask Queue, expanded Worker tools, shell authority,
  additional local models, model routing, multiple agents, larger autonomous tasks,
  and supervisor/fallback structure.
- For every candidate record use case, non-goal, state owner, tool authority, side
  effects, retry/idempotency, objective Evidence, risks, alternatives, open questions,
  and required Human Gate.
- Assign one primary classification: current Architecture, Architecture decision
  required, or Trust Boundary expansion required; record trust impact separately.
- State the M1 invariants that remain mandatory unless a future Human-approved ADR changes them.
- Produce proposed requirements and decisions-to-make, not accepted Requirements/ADRs.
- End with a Human Architecture Gate and no automatic successor.

## Allowed Changes

- `docs/MILESTONE_2_REVIEW.md`
- `STATUS.md`
- `tasks/QH-V2-M2-SPEC-001.md`

## Forbidden Changes

- `tools/**`
- `tests/**`
- `src/**`
- `fixtures/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- `BACKLOG.md`

All paths not listed under Allowed Changes remain default-denied by ChangeScope.

## Acceptance Criteria

1. The review covers all nine named capability candidates without omission.
2. Every candidate has exactly one primary classification from the three defined categories.
3. Every candidate records use case, non-goal, state owner, tool authority, side
   effects, retry/idempotency, Evidence, risks, alternatives, and open Human questions.
4. Shell authority, expanded tools, multi-agent operation, and larger autonomy have
   explicit Trust Boundary impact analysis.
5. Current M1 invariants are listed, including one ACTIVE Task, scoped harness-owned
   writes, no Worker final PASS, objective Git/Test Evidence, bounded Retry, and
   authoritative qh close.
6. Proposed requirements and open decisions are labelled proposals, not accepted changes.
7. No prototype, API implementation, code edit, ADR edit, or implementation Task
   decomposition is created.
8. STATUS names `HUMAN ARCHITECTURE GATE - NO AUTOMATIC TASK` as the next state after
   successful close of this review Task.
9. The conclusion explicitly requires Human review before any Architecture, authority,
   priority, or Milestone 2 implementation decision.

## Verification

Run exactly:

`python -c "from pathlib import Path; s=Path('docs/MILESTONE_2_REVIEW.md').read_text(encoding='utf-8'); required=('LangGraph','Subtask Queue','expanded Worker tools','shell authority','additional local models','model routing','multiple agents','larger autonomous tasks','supervisor/fallback','Human Architecture Gate'); assert all(x in s for x in required)"`

Then run:

`python -c "from pathlib import Path; s=Path('docs/MILESTONE_2_REVIEW.md').read_text(encoding='utf-8'); assert all(x in s for x in ('Current Architecture','Architecture Decision Required','Trust Boundary Expansion Required','Proposal Only','No implementation'))"`

Then run:

`git diff --check`

Then run:

`git status --short`

## Evidence Requirements

- A capability coverage matrix proves all nine candidates and all required analysis
  fields are present.
- Classification counts and trust-impact flags are recorded with no unclassified item.
- Changed-path Evidence proves this is documentation/lifecycle only and contains no
  code, test, fixture, ADR, Requirements, BACKLOG, or implementation-Task change.
- Human open questions and Evidence gaps are explicit rather than silently resolved.
- Exact implementation HEAD is used by `qh close`; all Verification commands exit 0,
  unexpected paths are absent, Diff Check is 0, and Final Gate is PASS.
- Lifecycle commit is separate, final working tree is clean, and no next Task is started.

## Stop Conditions

STOP with `DESIGN CHANGE REQUIRED` at the Human Architecture Gate if completion requires:

- accepting or editing Requirements, Architecture, or an ADR;
- approving shell, expanded tool, multi-agent, routing, or other authority expansion;
- choosing capability priority without a Human product decision;
- building a prototype or creating Milestone 2 implementation Tasks;
- changing the M1 Trust Boundary during analysis.

## Next Task

HUMAN ARCHITECTURE GATE - NO AUTOMATIC TASK.

No Task may be generated, approved, or started automatically from this review.
