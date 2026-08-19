# QH-V2-AUTO-002 - Deterministic Task Lifecycle Assistance

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-005 - Repetitive Harness Workflow Automation Priority
QH-V2-AUTO-001 - Deterministic Harness Workflow Automation
Deferred Automation Follow-up in STATUS.md

## Problem

Task transitions still require manual STATUS.md and Task-file editing. During QH-V2-OWA-001, a broad string replacement modified duplicate handoff text and required STOP, diagnosis, and repair. The same lifecycle transition is now repeating before the next planned Task.

## Goal

Add the smallest deterministic lifecycle assistance to `tools/qh.py` so an explicitly requested Human transition can be prepared safely without broad text replacement.

This Task does not create autonomous Task progression. Human invocation remains the approval boundary.

## Scope

Implement lifecycle assistance for explicit Human-invoked Task transitions only.

The implementation must:

- identify the single Current Task field structurally
- validate the requested Task file exists before a start transition
- reject ambiguous or duplicate Current Task fields
- update only the intended lifecycle fields rather than broad global replacement
- preserve unrelated historical Handoff text
- fail closed on unexpected STATUS.md structure
- remain deterministic and Repository-local

## Human Gate

Lifecycle commands run only when explicitly invoked by the Human.

This Task must not:

- automatically choose the next Task
- automatically run after another command
- automatically commit
- automatically modify Architecture or Decisions
- automatically declare semantic correctness
- bypass Verification or Final Gate
- start implementation of the next Task

## Completion Boundary

Any close/completion assistance must require already-existing deterministic Evidence and explicit Human invocation. It must not infer PASS from model output.

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `tasks/QH-V2-AUTO-002.md`
- `STATUS.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tests/test_harness_core.py`
- `tests/test_ollama_worker.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- Lifecycle assistance is deterministic and Human-invoked only.
- Duplicate or ambiguous lifecycle structure fails closed.
- Historical Handoff text is not accidentally rewritten.
- A requested start validates the target Task before modifying STATUS.md.
- No automatic next-Task selection exists.
- No auto-commit exists.
- No model output can authorize lifecycle completion.
- Existing qh status/preflight/verify/review behavior remains passing.
- Focused tests reproduce the QH-V2-OWA-001 duplicate-replacement failure class and prove it is prevented.
- Harness Core regression remains passing.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after lifecycle assistance implementation, Verification, independent review, commit, and clean working tree.

Do not start Harness-owned Repository Read Tools in this Task.
