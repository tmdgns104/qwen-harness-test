# QH-V2-MD-002 - Verified Problem Resolution Runbook

## Status

APPROVED - READY FOR CONTRACT BASELINE PREPARATION

## Problem

The Repository records Architecture and Task decisions, but repeated operational failures and their verified fixes are not yet captured in a reusable runbook.

As a result, Windows CMD quoting/escaping mistakes, accidental untracked artifacts, candidate-validation mistakes, whitespace-diff pollution, and NUL-delimiter escaping problems can be rediscovered and solved manually again.

## Goal

Create a Repository runbook that records verified operational problems in a reusable form and add an ADR that defines when repeated manual recovery procedures should be promoted to a Python utility.

This Task is documentation only. It must not implement Worker Adapter code or change the HC-001 through HC-007 implementation sequence.

## Required Documentation

Create:

- `docs/verified_problem_resolutions.md`

The document must define this record format:

1. Problem
2. Symptoms / Trigger
3. Root Cause
4. Verified Resolution
5. Verification Evidence
6. Prevention
7. Automation Candidate
8. Automation Status

It must record at minimum these already-observed incidents:

- Windows CMD multiline / redirection failure during long `python -c` input.
- Accidental untracked artifact creation and inspect-before-delete recovery.
- Qwen candidate isolation and verification before Repository application.
- Global trailing-whitespace cleanup polluting previously verified code diff.
- Nested CMD/Python NUL escaping producing `b"\\0"` instead of a real NUL delimiter, resolved with `bytes([0])`.
- Oversized or malformed Qwen candidate output detected by syntax/AST/diff/test Evidence and handled with bounded repair.

## Decision Update

Append `ADR-003 - Verified Problem Resolution and Automation Escalation` to `DECISIONS.md`.

ADR-003 must state:

- operational failures with a verified resolution are recorded in the Repository runbook;
- the verified resolution and Evidence are reused when the same failure shape appears again;
- repeated or error-prone manual procedures should be promoted to a small Python utility through a separate approved Task;
- promotion to a Python utility does not override current Architecture, Task scope, or the HC-001 through HC-007 sequence;
- Worker Adapter implementation remains deferred until the Architecture permits it.

## Allowed Changes

During QH-V2-MD-002 implementation:

- `docs/verified_problem_resolutions.md`
- `DECISIONS.md`

## Forbidden Changes

During QH-V2-MD-002 implementation:

- `tools/**`
- `src/**`
- `tests/**`
- `tasks/**`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `STATUS.md`
- all other Repository files

## Acceptance Criteria

- `docs/verified_problem_resolutions.md` exists.
- The required record format exists exactly once.
- All six required incidents are documented with Problem, Root Cause, Verified Resolution, Verification Evidence, Prevention, and Automation status.
- ADR-003 exists exactly once after ADR-002.
- ADR-003 preserves ADR-001 and ADR-002 unchanged.
- ADR-003 explicitly preserves the HC-001 through HC-007 sequence.
- ADR-003 does not authorize Worker Adapter implementation.
- Only the two Allowed Changes files are modified during implementation.

## Verification

Run:

`python -c "from pathlib import Path; d=Path('docs/verified_problem_resolutions.md').read_text(encoding='utf-8'); a=Path('DECISIONS.md').read_text(encoding='utf-8'); assert all(x in d for x in ['Problem','Root Cause','Verified Resolution','Verification Evidence','Prevention','Automation Candidate','Automation Status']); assert a.count('ADR-003 - Verified Problem Resolution and Automation Escalation') == 1; print('QH-V2-MD-002 DOC CHECK: PASS')"`

Then run:

`git diff --check`

Then verify actual changed paths against the Allowed Changes / Forbidden Changes contract.

## Stop

Stop after QH-V2-MD-002.
Do not start HC-004 or implement a Worker Adapter in this Task.
