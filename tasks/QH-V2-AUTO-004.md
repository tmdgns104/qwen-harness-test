# QH-V2-AUTO-004 - Task-Range Scope Review

## Status

APPROVED - READY FOR CONTRACT BASELINE

## Parent

ADR-005 - Repetitive Harness Workflow Automation Priority
FR-005 - Change scope contract
FR-006 - Independent completion evidence
FR-007 - Git baseline
FR-008 - Failure stop behavior
QH-V2-AUTO-001 - Deterministic Harness Workflow Automation
QH-V2-AUTO-003 - Lifecycle Next-Planned Consistency Fix

## Problem

`qh.py review` currently evaluates changed paths from the current HEAD baseline, so a clean working tree can hide Repository changes that were committed earlier during the active Task. STATUS.md explicitly records Task-range scope review as a priority candidate to revisit before Runner/E2E.

## Goal

Extend deterministic review so Task scope Evidence can cover the active Task range from an explicitly identified Task baseline commit through the current HEAD, while preserving the existing Harness Core as the authoritative scope/Evidence/final-gate engine.

## Scope

Modify `tools/qh.py` and focused tests only as needed to add Task-range changed-path review.

V1 capability:

- accept or deterministically identify an explicit Task baseline commit for review
- compare Repository changes from that baseline through current HEAD
- include committed Task changes in Changed Paths Evidence
- preserve detection of current uncommitted changes
- evaluate those paths against the existing Task Allowed/Forbidden scope
- fail closed for invalid or unusable baseline commits
- continue using existing Harness Core scope, Evidence, and Final Gate functions

## Trust Boundary

This Task does not create a second scope or final-gate engine.

Git range discovery may be orchestrated by `qh.py`, but scope interpretation, Evidence assembly, and final gating remain deterministic and reuse existing Harness Core behavior.

Human approval remains required for Task completion and commits.

## Boundary

This Task does not:

- invoke Qwen or Ollama
- implement Single-Task Runner
- implement retry
- auto-commit
- auto-complete Tasks
- auto-select the next Task
- modify Architecture
- change Harness Core authority

## Allowed Changes

- `tools/qh.py`
- `tests/test_qh.py`
- `tasks/QH-V2-AUTO-004.md`
- `STATUS.md`

## Forbidden Changes

- `tools/harness_core.py`
- `tools/ollama_worker.py`
- `tools/repo_tools.py`
- `tests/test_harness_core.py`
- `tests/test_ollama_worker.py`
- `tests/test_repo_tools.py`
- `PROJECT.md`
- `REQUIREMENTS.md`
- `DECISIONS.md`
- existing Task files
- fixtures
- all other Repository files

## Acceptance Criteria

- Review can inspect committed changes from an explicit Task baseline through current HEAD.
- A committed path outside Allowed Changes is reported as unexpected even when working tree is clean.
- Allowed committed Task changes do not cause a false scope failure.
- Current uncommitted changes remain visible to review.
- Invalid baseline commits fail closed.
- Existing Verification behavior remains unchanged.
- Existing lifecycle start/close behavior remains passing.
- Existing Harness Core regression remains passing.
- Existing Repository tool regression remains passing.
- No third-party dependency is added.
- No file outside Allowed Changes is modified.

## Verification

Run exactly:

`python -m unittest tests.test_qh`

Then run:

`python -m unittest tests.test_harness_core`

Then run:

`python -m unittest tests.test_repo_tools`

Then run:

`git diff --check`

Then run:

`git status --short`

## Stop Condition

Stop after implementation, Verification, independent review, commit, lifecycle close, and clean working tree.

Do not start Single-Task Runner, retry, Minimal CLI, or E2E work.
