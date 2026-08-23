# QH-V2-ARCH-018 - Deterministic Worker Brief Production Promotion Decision

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Problem

QH-V2-WORKER-DIAG-001 showed that the current native `qwen3:8b` Worker is responsive for short requests but unstable on full Repository Task solving under the current 30-second bounded timeout. QH-V2-WORKER-ROB-002 then compared three first-step interaction variants under the same model, `think:false`, timeout, and tool schema.

Tracked Evidence reports:

- Stable full Task: 6/10 valid bounded first steps, 4/10 timeouts;
- Candidate A deterministic Worker Brief: 10/10 valid bounded first steps, 0/10 timeouts;
- Candidate B Worker Brief plus one-step instruction: 2/10 valid bounded first steps, 3/10 timeouts;
- no Worker ToolRequest was executed in the experiment and Worker writes were zero.

The experiment recommends Candidate A only for a separate production Task. ADR-011 classifies prompt/context strategy changes inside the existing Trust Boundary as Level B policy changes that require objective Stable-versus-Candidate Evidence and a Promotion Gate. ADR-017 also requires Human review for Candidate production promotion.

The Human has now selected the recommended order: evaluate and record Candidate A production promotion before resuming the deferred Operations queue.

## Goal

Record the Human-reviewed production-promotion decision for Candidate A - Deterministic Worker Brief, preserve all existing safety and authority boundaries, and define the exact separately approved implementation Task that may integrate the deterministic Worker Brief before QH-V2-OPS-003 resumes.

This Architecture Task does not implement Worker behavior.

## Architecture Basis

- ADR-001 deterministic Harness authority remains unchanged.
- ADR-008 backend-neutral tool interaction and zero-or-one ToolRequest safety rule remain unchanged.
- ADR-009 bounded Retry and safe-stop policy remain unchanged.
- ADR-011 Evidence-driven Stable/Candidate promotion policy applies.
- ADR-014 multi-tool SAFETY remains fail closed.
- ADR-015 unsuccessful Task state remains non-success Evidence.
- ADR-016 requires the Worker diagnostic path to reach Human-reviewed disposition before Operations resume.
- ADR-017 requires Human review for Candidate production promotion and permits routine continuation only after that direction is recorded in Source of Truth.
- QH-V2-WORKER-ROB-002 is COMPLETE - VERIFIED and its Evidence is the promotion basis.

`GLOBALIZATION = NOT AUTHORIZED` remains unchanged.

## Decision Scope

The decision may authorize only Candidate A's deterministic Worker Brief concept for a separate production implementation Task.

The production Candidate must preserve all of the following:

- the original tracked Task remains the only Source of Truth;
- the brief is produced deterministically by Harness code, not by free-form LLM summarization;
- the brief copies only approved Task contract material defined by the implementation Task;
- missing or ambiguous required Task sections fail closed;
- Candidate B's extra one-step instruction is not promoted by this decision;
- Worker Tool authority does not expand;
- model remains `qwen3:8b` unless a later separately approved policy changes it;
- `think:false`, current timeout, Retry budget, Worker-step budget, and zero-or-one ToolRequest safety rule remain unchanged;
- Verification, Evidence, Final Gate, lifecycle, Git, and successor authority remain Harness/Human-controlled as already defined.

## Scope

1. Add an Accepted ADR recording the Candidate A promotion decision and its evidence basis.
2. Update BACKLOG only as needed to record the Human-selected sequence:

   `QH-V2-ARCH-018 -> QH-V2-WORKER-ROB-003 -> QH-V2-OPS-003`

3. Create `tasks/QH-V2-WORKER-ROB-003.md` as the exact approved production integration contract.
4. The successor contract must require focused RED/GREEN/regression Evidence and an authoritative `qh close` Final Gate before production integration is considered complete.
5. Do not modify Worker/Runner/Retry/runtime implementation in this Architecture Task.

## Allowed Changes

- `DECISIONS.md`
- `BACKLOG.md`
- `STATUS.md`
- `tasks/QH-V2-ARCH-018.md`
- `tasks/QH-V2-WORKER-ROB-003.md`

## Forbidden Changes

- `PROJECT.md`
- `REQUIREMENTS.md`
- `tools/**`
- `tests/**`
- `experiments/**`
- `ops/**`
- any Task file other than `tasks/QH-V2-ARCH-018.md` and `tasks/QH-V2-WORKER-ROB-003.md`
- Candidate B production promotion
- model, `think`, timeout, Retry budget, Worker-step budget, Tool authority, Verification, Final Gate, lifecycle, Git authority, or Globalization changes
- historical G1 manifest modification or reactivation

## Acceptance Criteria

1. `DECISIONS.md` contains an Accepted ADR for Candidate A production promotion based on QH-V2-WORKER-ROB-002 Evidence.
2. The decision accurately records Stable 6/10 valid with 4/10 timeout, Candidate A 10/10 valid with 0/10 timeout, Candidate B 2/10 valid with 3/10 timeout, and zero Worker writes.
3. Candidate A is authorized only through a separate implementation Task; this Architecture Task changes no production Worker behavior.
4. Candidate B is explicitly not promoted.
5. `tasks/QH-V2-WORKER-ROB-003.md` exists with exact approved status and preserves the original Task as Source of Truth.
6. The successor contract does not change model, thinking mode, timeout, Retry budget, Worker-step budget, Tool authority, Verification, Final Gate, lifecycle, or Git authority.
7. BACKLOG records the Human-selected order `ARCH-018 -> WORKER-ROB-003 -> OPS-003` without cancelling OPS-003.
8. `GLOBALIZATION = NOT AUTHORIZED` remains unchanged.
9. Only Allowed Changes occur.
10. `git diff --check` passes.

## Verification

Run exactly:

`python -c "from pathlib import Path; d=Path('DECISIONS.md').read_text(encoding='utf-8'); b=Path('BACKLOG.md').read_text(encoding='utf-8'); t=Path('tasks/QH-V2-WORKER-ROB-003.md'); assert 'ADR-018' in d; assert 'Candidate A' in d; assert '6/10' in d and '4/10' in d and '10/10' in d and '0/10' in d and '2/10' in d and '3/10' in d; assert t.is_file(); s=t.read_text(encoding='utf-8'); assert 'APPROVED - READY FOR CONTRACT BASELINE' in s; assert 'QH-V2-ARCH-018' in b and 'QH-V2-WORKER-ROB-003' in b and 'QH-V2-OPS-003' in b"`

Run exactly:

`python -c "from pathlib import Path; text=Path('DECISIONS.md').read_text(encoding='utf-8')+'\n'+Path('tasks/QH-V2-WORKER-ROB-003.md').read_text(encoding='utf-8'); required=['GLOBALIZATION = NOT AUTHORIZED','original tracked Task','think:false','zero-or-one ToolRequest']; missing=[x for x in required if x not in text]; assert not missing, missing"`

Run exactly:

`git diff --check`

Run exactly:

`git status --short`

## Evidence Requirements

Before successful close, demonstrate:

- the QH-V2-WORKER-ROB-002 measured comparison used for promotion;
- the Accepted ADR-018 text;
- the exact successor Task contract;
- BACKLOG sequence preserving OPS-003 as deferred successor;
- no production implementation changes in this Architecture Task;
- authoritative `qh close <exact implementation HEAD>` Final Gate PASS;
- separate lifecycle commit after Final Gate PASS.

## Stop Conditions

STOP for Human/ChatGPT review if the decision would require:

- promoting Candidate B;
- changing model, thinking mode, timeout, Retry budget, Worker-step budget, Tool authority, Verification, Final Gate, lifecycle, Git authority, or Globalization;
- weakening fail-closed behavior for multi-tool or malformed Worker output;
- making the deterministic brief a replacement Source of Truth;
- cancelling or materially redesigning OPS-003 rather than deferring it behind the approved Worker integration;
- any production-code implementation inside this Architecture Task.

## Next Task

If QH-V2-ARCH-018 reaches COMPLETE - VERIFIED, the exact successor is:

`QH-V2-WORKER-ROB-003 - Deterministic Worker Brief Production Integration`

QH-V2-OPS-003 remains deferred until that production integration Task reaches a Human-reviewed terminal disposition.